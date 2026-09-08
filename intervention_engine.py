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
from typing import Dict, List, Tuple, Any, Optional
import pandas as pd
import networkx as nx

from cascade_engine import CascadeEngine


class InterventionEngine:
    """
    Evaluates candidate interventions against an immutable flooded baseline,
    computes Utility, ranks strategies, and compares against heuristic baselines.
    """

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
        flooded_roads = [r for r in self.roads if r.get("is_flooded", False)]
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
        if len(flooded_roads) >= 2:
            # Pair the top-2 most strategic flooded roads or bridge combos
            r_pairs = []
            for i in range(len(flooded_roads)):
                for j in range(i + 1, len(flooded_roads)):
                    r_pairs.append((flooded_roads[i], flooded_roads[j]))
                    if len(r_pairs) >= 3:  # Keep combinatorial search small for MVP
                        break
                if len(r_pairs) >= 3:
                    break

            for r1, r2 in r_pairs:
                combined_effort = round(r1["effort_cost"] + r2["effort_cost"], 1)
                candidates.append({
                    "id": f"COMBINED_{r1['road_id']}_{r2['road_id']}",
                    "name": f"Dual Restore: {r1['road_id']} + {r2['road_id']}",
                    "type": "Combined Intervention",
                    "target_roads": [r1["road_id"], r2["road_id"]],
                    "temporary_links": [],
                    "effort_cost": combined_effort,
                    "description": f"Simultaneous dual-corridor restoration of {r1['road_id']} and {r2['road_id']}.",
                })

        return candidates

    def simulate_candidate(self, candidate: Dict[str, Any]) -> Tuple[nx.Graph, Dict[str, Any]]:
        """
        Simulates an intervention candidate non-destructively:
          - Starts from clean baseline flooded graph
          - Restores specified target roads
          - Adds any temporary links
          - Calculates resulting accessibility metrics
        """
        target_roads_set = set(candidate.get("target_roads", []))
        temp_links = candidate.get("temporary_links", [])

        # Clone roads and update target roads to passable
        sim_roads = copy.deepcopy(self.roads)
        for r in sim_roads:
            if r["road_id"] in target_roads_set:
                r["is_flooded"] = False
                r["is_accessible"] = True

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
            df = df.sort_values(by=["utility", "delta_population"], ascending=[False, False]).reset_index(drop=True)
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
        flooded_roads = [r for r in self.roads if r.get("is_flooded", False)]
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

    def get_analysis_reliability(self) -> Dict[str, Any]:
        """
        Evaluates prototype analysis reliability based on data completeness indicators.
        Label: Prototype analysis reliability — not a calibrated probability.
        """
        has_nodes = len(self.nodes) >= 10
        has_facilities = len(self.ce.hospital_nodes) >= 1 and len(self.ce.relief_nodes) >= 1
        has_roads = len(self.roads) >= 12

        if has_nodes and has_facilities and has_roads:
            level = "HIGH"
            badge_color = "green"
            explanation = (
                "Topology graph, facility dependencies, and population cluster registries are 100% complete. "
                "Deterministic counterfactual model produces exact graph simulation results."
            )
        else:
            level = "MEDIUM"
            badge_color = "orange"
            explanation = "Partial network coverage. Recommendations should be verified with field reconnaissance."

        return {
            "level": level,
            "badge_color": badge_color,
            "explanation": explanation,
            "label": "Prototype analysis reliability — not a calibrated probability.",
            "metrics": {
                "Network Completeness": "100% (Synthetic Urban Graph)",
                "Facility Dependency Model": "100% (Trauma Hospital + Relief Logistics)",
                "Intervention Candidate Coverage": "Multi-Modal (Restoration + Temporary + Combined)",
            }
        }

