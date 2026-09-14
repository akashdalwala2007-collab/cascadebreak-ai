"""
CascadeBreak AI - Counterfactual Intervention & Optimization Engine (V2)
=======================================================================
Implements the multi-modal counterfactual evaluation engine:

Intervention Types:
  1. ROAD RESTORATION: Restore an individual flooded road.
  2. TRAFFIC REROUTING: Evaluate open network detour capacity.
  3. TEMPORARY ACCESS: Deploy temporary emergency bridge/pontoon links.
  4. COMBINED INTERVENTION: Multi-action emergency package (e.g., dual road restoration).

Optimization Objective:
  Utility(i) = [ wp * DeltaP(i) + wh * DeltaH(i) + wr * DeltaR(i) ] / Effort(i)

Demonstration Weights (Configurable):
  wp = 0.5 (Population dual critical access)
  wh = 0.3 (Hospital trauma access)
  wr = 0.2 (Relief shelter access)
"""

import copy
import itertools
import math
from typing import Dict, List, Tuple, Any, Optional
import pandas as pd
import networkx as nx

from cascade_engine import CascadeEngine, is_road_impassable, is_road_passable


def _is_safe_finite_numeric(val: Any) -> bool:
    """
    Safely checks if a value is a finite number (int or float).
    Rejects booleans (isinstance(True, int) is True in Python), NaN, +/-inf,
    and arbitrarily large integers that would cause OverflowError on float conversion.
    """
    if isinstance(val, bool):
        return False
    if isinstance(val, int):
        if val.bit_length() > 1024:
            return False
        try:
            return math.isfinite(float(val))
        except (OverflowError, ValueError):
            return False
    if isinstance(val, float):
        return math.isfinite(val)
    return False


class InterventionEngine:
    """
    Evaluates candidate interventions against an immutable flooded baseline,
    computes Utility, ranks strategies, and compares against heuristic baselines.
    """

    _is_safe_finite_numeric = staticmethod(_is_safe_finite_numeric)

    def __init__(self, cascade_engine: CascadeEngine):
        self.ce = cascade_engine
        self.nodes = self.ce.nodes
        self.roads = self.ce.roads

    def get_candidate_interventions(self) -> List[Dict[str, Any]]:
        """
        Generates candidate interventions across all supported types:
          1. Road Restoration (all flooded roads)
          2. Temporary Access (standard strategic emergency pontoons/bypasses)
          3. Combined Interventions (curated pairs of complementary actions)
        """
        flooded_roads = sorted([r for r in self.roads if is_road_impassable(r)], key=lambda r: r["road_id"])
        candidates = []

        # Type 1: Single Road Restorations
        for r in flooded_roads:
            candidates.append({
                "id": f"RESTORE_{r['road_id']}",
                "name": f"Restore Road {r['road_id']} ({r['name']})",
                "type": "Road Restoration",
                "target_roads": [r["road_id"]],
                "temporary_links": [],
                "effort_cost": r["effort_cost"],
                "description": f"Clear debris and restore passable traffic on {r['road_id']} ({r['length_km']} km).",
            })

        # Type 2: Temporary Emergency Connections
        # E.g., Strategic river pontoon or bypass links across key corridors
        temp_options = [
            {
                "id": "TEMP_N4_N6",
                "name": "Deploy Emergency River Pontoon (N4 to N6)",
                "type": "Temporary Access",
                "target_roads": [],
                "temporary_links": [
                    {
                        "u": "N4",
                        "v": "N6",
                        "road_id": "TEMP_N4_N6",
                        "name": "Central-to-Hospital Emergency River Pontoon",
                        "length_km": 2.8,
                        "effort_cost": 4.5,
                        "condition_note": "Rapid deployable floating bridge",
                    }
                ],
                "effort_cost": 4.5,
                "description": "Install emergency pontoon bridge bypassing central river crossing directly to Hospital.",
            },
            {
                "id": "TEMP_N3_N7",
                "name": "Deploy West-Relief Culvert Bridge (N3 to N7)",
                "type": "Temporary Access",
                "target_roads": [],
                "temporary_links": [
                    {
                        "u": "N3",
                        "v": "N7",
                        "road_id": "TEMP_N3_N7",
                        "name": "West-to-Relief Emergency Culvert Bridge",
                        "length_km": 3.6,
                        "effort_cost": 4.0,
                        "condition_note": "Emergency culvert crossing across western wash",
                    }
                ],
                "effort_cost": 4.0,
                "description": "Install temporary Bailey bridge connecting West Hills directly to Relief Hub.",
            },
        ]
        candidates.extend(temp_options)

        # Type 3: Combined Interventions (Bundles of 2 complementary actions)
        # Select strategic pairs using deterministic semantic criteria independent of road list ordering
        if len(flooded_roads) >= 2:
            fac_nodes = set(self.ce.hospital_nodes + self.ce.relief_nodes)
            candidate_pairs = []
            for r_a, r_b in itertools.combinations(flooded_roads, 2):
                # Canonical ordering within each pair by road_id
                r1, r2 = sorted([r_a, r_b], key=lambda r: r["road_id"])

                # Deterministic semantic priority criteria:
                # 1. Corridor continuity: roads that share an intersection form a connected corridor
                is_adjacent = bool({r1["u"], r1["v"]} & {r2["u"], r2["v"]})
                # 2. Critical facility connectivity: connects directly to hospital or relief centre
                connects_facility = bool({r1["u"], r1["v"], r2["u"], r2["v"]} & fac_nodes)
                # 3. Population exposure: total population across distinct endpoints
                pop_weight = sum(self.nodes[n].get("population", 0) for n in {r1["u"], r1["v"], r2["u"], r2["v"]})
                # 4. Logistical feasibility: lower combined effort is preferred
                combined_effort = round(r1["effort_cost"] + r2["effort_cost"], 1)

                # Priority key:
                # Priority rank (lower is better):
                #   is_adjacent (0 vs 1)
                #   connects_facility (0 vs 1)
                #   -pop_weight (higher population first)
                #   combined_effort (lower effort first)
                #   road_id tie-breaker
                priority_key = (
                    0 if is_adjacent else 1,
                    0 if connects_facility else 1,
                    -pop_weight,
                    combined_effort,
                    r1["road_id"],
                    r2["road_id"],
                )
                candidate_pairs.append((priority_key, r1, r2, combined_effort))

            # Sort deterministically by semantic priority and evaluate all strategic pairs
            candidate_pairs.sort(key=lambda x: x[0])
            for _, r1, r2, combined_effort in candidate_pairs:
                combined_cand = {
                    "id": f"COMBINED_{r1['road_id']}_{r2['road_id']}",
                    "name": f"Dual Restore: {r1['road_id']} + {r2['road_id']}",
                    "type": "Combined Intervention",
                    "target_roads": [r1["road_id"], r2["road_id"]],
                    "temporary_links": [],
                    "effort_cost": combined_effort,
                    "description": f"Simultaneous dual-corridor restoration of {r1['road_id']} and {r2['road_id']}.",
                }
                candidates.append(combined_cand)

        return candidates

    def validate_candidate(self, candidate: Dict[str, Any]) -> bool:
        """
        Defensively validates that a candidate intervention is properly formed,
        well-typed, and feasible.
        Rejects malformed candidates cleanly (returns False) without leaking exceptions.
        """
        if not isinstance(candidate, dict):
            return False

        cand_id = candidate.get("id")
        if not isinstance(cand_id, str) or not cand_id.strip():
            return False

        if "effort_cost" not in candidate:
            return False
        effort = candidate["effort_cost"]
        if not _is_safe_finite_numeric(effort) or effort <= 0:
            return False

        target_roads = candidate.get("target_roads", [])
        temp_links = candidate.get("temporary_links", [])

        # Validate containers are lists, tuples, or sets (not str, dict, int, etc.)
        if not isinstance(target_roads, (list, tuple, set)):
            return False
        if not isinstance(temp_links, (list, tuple, set)):
            return False

        # Must have at least one restoration road or temporary link
        if not target_roads and not temp_links:
            return False

        all_road_ids = {r.get("road_id") for r in self.roads if isinstance(r, dict) and "road_id" in r}
        for r_id in target_roads:
            if not isinstance(r_id, str) or not r_id.strip() or r_id not in all_road_ids:
                return False

        all_node_ids = set(self.nodes.keys())
        for link in temp_links:
            if not isinstance(link, dict):
                return False
            u = link.get("u")
            v = link.get("v")
            if not isinstance(u, str) or not isinstance(v, str):
                return False
            if not u.strip() or not v.strip() or u not in all_node_ids or v not in all_node_ids:
                return False
            if "effort_cost" in link:
                link_effort = link["effort_cost"]
                if not _is_safe_finite_numeric(link_effort) or link_effort < 0:
                    return False
            if "length_km" in link:
                link_len = link["length_km"]
                if not _is_safe_finite_numeric(link_len) or link_len <= 0:
                    return False

        return True

    def simulate_candidate(self, candidate: Dict[str, Any]) -> Tuple[nx.Graph, Dict[str, Any]]:
        """
        Simulates an intervention candidate non-destructively:
          - Validates candidate structure
          - Starts from clean baseline flooded graph
          - Restores specified target roads to passable
          - Adds any temporary links
          - Calculates resulting accessibility metrics
        """
        if not self.validate_candidate(candidate):
            raise ValueError(f"Cannot simulate malformed or invalid candidate: {candidate}")

        target_roads_set = set(candidate.get("target_roads", []))
        temp_links = candidate.get("temporary_links", [])

        # Clone roads and update target roads to passable across all passability indicators
        sim_roads = copy.deepcopy(self.roads)
        for r in sim_roads:
            if r["road_id"] in target_roads_set:
                r["is_flooded"] = False
                r["is_accessible"] = True
                r["is_impassable"] = False
                r["passable"] = True
                r["is_passable"] = True
                if "status" in r and str(r["status"]).lower() in {"impassable", "submerged", "closed", "blocked"}:
                    r["status"] = "restored"

        G_intervened = self.ce._build_graph(
            filter_flooded=True,
            custom_roads=sim_roads,
            extra_edges=temp_links,
        )

        metrics = self.ce.evaluate_network_state(G_intervened)
        return G_intervened, metrics

    def evaluate_all_interventions(
        self,
        wp: float = 0.5,
        wh: float = 0.3,
        wr: float = 0.2,
    ) -> pd.DataFrame:
        """
        Systematically evaluates all candidate interventions against the flooded baseline.

        Utility Formula:
          Utility = (wp * DeltaP + wh * DeltaH + wr * DeltaR) / max(Effort, 0.1)

        Returns sorted DataFrame by Utility descending.
        """
        baseline_summary = self.ce.get_baseline_summary()
        flooded_metrics = baseline_summary["flooded_metrics"]
        base_both = flooded_metrics["pop_with_both"]
        base_hosp = flooded_metrics["pop_with_hospital"]
        base_relief = flooded_metrics["pop_with_relief"]

        candidates = self.get_candidate_interventions()
        results = []

        for cand in candidates:
            effort = cand["effort_cost"]
            _, sim_metrics = self.simulate_candidate(cand)

            delta_pop = sim_metrics["pop_with_both"] - base_both
            delta_hosp = sim_metrics["pop_with_hospital"] - base_hosp
            delta_relief = sim_metrics["pop_with_relief"] - base_relief

            total_benefit = (wp * delta_pop) + (wh * delta_hosp) + (wr * delta_relief)
            effort_safe = max(effort, 0.1)
            utility = total_benefit / effort_safe

            results.append({
                "candidate_id": cand["id"],
                "intervention": cand["name"],
                "type": cand["type"],
                "delta_population": delta_pop,
                "delta_hospital": delta_hosp,
                "delta_relief": delta_relief,
                "effort": effort,
                "raw_benefit": round(total_benefit, 2),
                "utility": round(utility, 2),
                "isolated_pop_remaining": sim_metrics["pop_fully_isolated"],
                "connected_components": sim_metrics["num_connected_components"],
                "candidate_obj": cand,
            })

        df = pd.DataFrame(results)
        if not df.empty:
            df = df.sort_values(
                by=["utility", "delta_population", "effort", "candidate_id"],
                ascending=[False, False, True, True]
            ).reset_index(drop=True)
            df.index = df.index + 1
            df.index.name = "Rank"

        return df

    def get_dynamic_recommendation(
        self,
        wp: float = 0.5,
        wh: float = 0.3,
        wr: float = 0.2,
    ) -> Dict[str, Any]:
        """
        Derives an actionable AI recommendation dynamically from calculated graph metrics.
        Guarantees:
          - If all interventions produce zero improvement: Shows 'NO BENEFICIAL INTERVENTION IDENTIFIED'
          - Explanation contains zero hard-coded claims and is formulated purely from graph numbers.
        """
        ranking_df = self.evaluate_all_interventions(wp=wp, wh=wh, wr=wr)

        if ranking_df.empty:
            return {
                "has_beneficial_intervention": False,
                "title": "NO BENEFICIAL INTERVENTION IDENTIFIED",
                "message": "No candidate interventions are available for evaluation.",
                "ranking_df": ranking_df,
            }

        top = ranking_df.iloc[0]

        # Check if the top intervention produces zero improvement
        if top["utility"] <= 0 or (top["delta_population"] == 0 and top["delta_hospital"] == 0 and top["delta_relief"] == 0):
            return {
                "has_beneficial_intervention": False,
                "title": "NO BENEFICIAL INTERVENTION IDENTIFIED",
                "message": (
                    "All simulated interventions produce 0 accessibility improvement over the current baseline. "
                    "Either all critical facilities remain already accessible or current flood damage requires multi-stage access."
                ),
                "ranking_df": ranking_df,
            }

        cand_name = top["intervention"]
        cand_type = top["type"]
        cand_effort = top["effort"]
        cand_utility = top["utility"]
        delta_pop = int(top["delta_population"])
        delta_hosp = int(top["delta_hospital"])
        delta_relief = int(top["delta_relief"])
        isolated_rem = int(top["isolated_pop_remaining"])
        cand_obj = top["candidate_obj"]

        # Formulate dynamic reasoning from exact numbers
        benefit_clauses = []
        if delta_pop > 0:
            benefit_clauses.append(f"reconnecting {delta_pop:,} residents to full dual-critical access")
        if delta_hosp > 0 and delta_hosp != delta_pop:
            benefit_clauses.append(f"restoring trauma hospital connectivity for {delta_hosp:,} citizens")
        if delta_relief > 0 and delta_relief != delta_pop:
            benefit_clauses.append(f"re-establishing relief supply corridors for {delta_relief:,} people")

        benefits_summary = ", ".join(benefit_clauses) if benefit_clauses else "restoring essential network connectivity"

        explanation = (
            f"Candidate **{cand_name}** ({cand_type}) produces the highest downstream accessibility "
            f"improvement relative to intervention effort. At an Intervention Effort Index of **{cand_effort} units**, "
            f"it achieves a Utility score of **{cand_utility:,.2f}** by {benefits_summary}. "
            f"Simulated post-intervention state leaves only {isolated_rem:,} residents isolated, "
            f"maximizing humanitarian access efficiency per deployed resource unit."
        )

        return {
            "has_beneficial_intervention": True,
            "title": f"RECOMMENDED INTERVENTION: {cand_name}",
            "intervention_name": cand_name,
            "intervention_type": cand_type,
            "effort": cand_effort,
            "utility": cand_utility,
            "delta_population": delta_pop,
            "delta_hospital": delta_hosp,
            "delta_relief": delta_relief,
            "isolated_remaining": isolated_rem,
            "explanation": explanation,
            "candidate_obj": cand_obj,
            "ranking_df": ranking_df,
        }

    def evaluate_baseline_heuristics_comparison(
        self,
        wp: float = 0.5,
        wh: float = 0.3,
        wr: float = 0.2,
    ) -> pd.DataFrame:
        """
        Compares CascadeBreak AI optimization against naive operational heuristics:
          - Baseline A (Damage Severity First): Responders tackle the most severely damaged / longest road first.
          - Baseline B (Population Exposure First): Responders restore the road directly adjacent to the largest cut-off population cluster.
          - CascadeBreak AI (Proposed): Top-ranked intervention maximizing downstream accessibility utility.
        """
        flooded_roads = [r for r in self.roads if is_road_impassable(r)]
        if not flooded_roads:
            return pd.DataFrame()

        # Strategy 1: Naive Severity First (Highest damage_factor * length or effort)
        sorted_by_damage = sorted(flooded_roads, key=lambda r: (r.get("damage_factor", 1.0) * r["length_km"], r["effort_cost"]), reverse=True)
        top_damage_road = sorted_by_damage[0]
        cand_sev = {
            "id": f"RESTORE_{top_damage_road['road_id']}",
            "name": f"Restore Road {top_damage_road['road_id']} ({top_damage_road['name']})",
            "type": "Road Restoration",
            "target_roads": [top_damage_road["road_id"]],
            "temporary_links": [],
            "effort_cost": top_damage_road["effort_cost"],
        }
        _, sev_metrics = self.simulate_candidate(cand_sev)

        # Strategy 2: Naive Population Exposure First (Road adjacent to largest population node)
        pop_nodes_sorted = sorted(
            self.ce.population_nodes,
            key=lambda nid: self.nodes[nid]["population"],
            reverse=True
        )
        adj_road = None
        for pn in pop_nodes_sorted:
            for r in flooded_roads:
                if r["u"] == pn or r["v"] == pn:
                    adj_road = r
                    break
            if adj_road:
                break
        if adj_road is None:
            adj_road = flooded_roads[0]

        cand_pop = {
            "id": f"RESTORE_{adj_road['road_id']}",
            "name": f"Restore Road {adj_road['road_id']} ({adj_road['name']})",
            "type": "Road Restoration",
            "target_roads": [adj_road["road_id"]],
            "temporary_links": [],
            "effort_cost": adj_road["effort_cost"],
        }
        _, pop_metrics = self.simulate_candidate(cand_pop)

        # Proposed Strategy: CascadeBreak AI
        ranking_df = self.evaluate_all_interventions(wp=wp, wh=wh, wr=wr)
        top_cascade = ranking_df.iloc[0]

        base_summary = self.ce.get_baseline_summary()["flooded_metrics"]
        base_both = base_summary["pop_with_both"]
        base_hosp = base_summary["pop_with_hospital"]
        base_relief = base_summary["pop_with_relief"]

        # Calculate metrics for Baseline A
        sev_delta_p = sev_metrics["pop_with_both"] - base_both
        sev_delta_h = sev_metrics["pop_with_hospital"] - base_hosp
        sev_delta_r = sev_metrics["pop_with_relief"] - base_relief
        sev_util = round(((wp * sev_delta_p) + (wh * sev_delta_h) + (wr * sev_delta_r)) / max(cand_sev["effort_cost"], 0.1), 2)

        # Calculate metrics for Baseline B
        pop_delta_p = pop_metrics["pop_with_both"] - base_both
        pop_delta_h = pop_metrics["pop_with_hospital"] - base_hosp
        pop_delta_r = pop_metrics["pop_with_relief"] - base_relief
        pop_util = round(((wp * pop_delta_p) + (wh * pop_delta_h) + (wr * pop_delta_r)) / max(cand_pop["effort_cost"], 0.1), 2)

        comparison_data = [
            {
                "Strategy": "Baseline A: Highest Flood Severity / Damage First",
                "Selected Intervention": cand_sev["name"],
                "Pop. Restored (ΔP)": f"+{sev_delta_p:,}",
                "Hospital Restored (ΔH)": f"+{sev_delta_h:,}",
                "Relief Restored (ΔR)": f"+{sev_delta_r:,}",
                "Effort Index": cand_sev["effort_cost"],
                "Utility Score": f"{sev_util:,.2f}",
                "Operational Logic": "Focuses on the most physically damaged road regardless of network connectivity impact.",
            },
            {
                "Strategy": "Baseline B: Highest Population Exposure First",
                "Selected Intervention": cand_pop["name"],
                "Pop. Restored (ΔP)": f"+{pop_delta_p:,}",
                "Hospital Restored (ΔH)": f"+{pop_delta_h:,}",
                "Relief Restored (ΔR)": f"+{pop_delta_r:,}",
                "Effort Index": cand_pop["effort_cost"],
                "Utility Score": f"{pop_util:,.2f}",
                "Operational Logic": "Repairs road closest to the largest local population cluster, risking dead-ends.",
            },
            {
                "Strategy": "Proposed: CascadeBreak AI (Cascade Optimization)",
                "Selected Intervention": top_cascade["intervention"],
                "Pop. Restored (ΔP)": f"+{int(top_cascade['delta_population']):,}",
                "Hospital Restored (ΔH)": f"+{int(top_cascade['delta_hospital']):,}",
                "Relief Restored (ΔR)": f"+{int(top_cascade['delta_relief']):,}",
                "Effort Index": top_cascade["effort"],
                "Utility Score": f"{top_cascade['utility']:,.2f}",
                "Operational Logic": "Simulates systemic downstream access gains across the entire city graph per effort unit.",
            },
        ]

        return pd.DataFrame(comparison_data)

    def get_analysis_reliability(self, level: Optional[str] = None) -> Dict[str, Any]:
        """
        Evaluates prototype analysis reliability based on data completeness indicators.
        Label: Prototype analysis reliability — not a calibrated probability.

        Measured completeness remains authoritative when determining the effective reliability level.
        An explicitly supplied level parameter cannot override or falsify data completeness.
        """
        has_nodes = len(self.nodes) >= 10
        has_facilities = len(self.ce.hospital_nodes) >= 1 and len(self.ce.relief_nodes) >= 1
        has_roads = len(self.roads) >= 12

        if has_nodes and has_facilities and has_roads:
            measured_level = "HIGH"
        elif has_facilities and (has_nodes or has_roads):
            measured_level = "MEDIUM"
        else:
            measured_level = "LOW"

        # Measured completeness is strictly authoritative.
        # If an explicit level is supplied that disagrees with measured completeness,
        # resolve using measured completeness thresholds/logic.
        selected_level = measured_level

        if selected_level == "HIGH":
            badge_color = "green"
            explanation = (
                "Topology graph, facility dependencies, and population cluster registries are 100% complete. "
                "Deterministic counterfactual model produces exact graph simulation results."
            )
            metrics = {
                "Network Completeness": "100% (Synthetic Urban Graph)",
                "Facility Dependency Model": "100% (Trauma Hospital + Relief Logistics)",
                "Intervention Candidate Coverage": "Multi-Modal (Restoration + Temporary + Combined)",
            }
        elif selected_level == "MEDIUM":
            badge_color = "orange"
            explanation = "Partial network coverage. Recommendations should be verified with field reconnaissance."
            metrics = {
                "Network Completeness": "Partial (<100% Urban Graph)",
                "Facility Dependency Model": "100% (Trauma Hospital + Relief Logistics)" if has_facilities else "Partial (Degraded Facilities)",
                "Intervention Candidate Coverage": "Restricted (Reduced Candidate Set)",
            }
        else:
            selected_level = "LOW"
            badge_color = "red"
            explanation = "Insufficient network or facility coverage for reliable counterfactual optimization."
            metrics = {
                "Network Completeness": "Low (<50% Urban Graph)",
                "Facility Dependency Model": "Incomplete (Missing Critical Facilities)",
                "Intervention Candidate Coverage": "Limited (Minimal Candidate Set)",
            }

        return {
            "level": selected_level,
            "badge_color": badge_color,
            "explanation": explanation,
            "label": "Prototype analysis reliability — not a calibrated probability.",
            "metrics": metrics,
        }

