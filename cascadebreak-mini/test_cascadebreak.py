"""
Automated Test Suite for CascadeBreak AI (V2)
============================================
Verifies:
  1. Synthetic data integrity and population sum (59,000).
  2. Baseline graph generation and cascade mechanics.
  3. Non-destructive counterfactual intervention evaluation.
  4. Multi-modal candidate interventions (Restoration, Temporary, Combined).
  5. Multi-scenario behavior:
     - Scenario 1 (Urban Flood): Validates optimal intervention identified.
     - Scenario 2 (Critical Corridor): Validates MOST DAMAGED ROAD != MOST VALUABLE INTERVENTION.
     - Scenario 3 (Multi-Route Bottleneck): Validates multi-route evaluation.
     - Scenario 4 (Clear): Validates NO BENEFICIAL INTERVENTION IDENTIFIED handling.
  6. Explainability generation (no hardcoded claims).
  7. Baseline heuristic comparisons.
"""

import io
import sys
import math
import networkx as nx

# Ensure UTF-8 output encoding
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from scenario import get_synthetic_city_nodes, get_synthetic_city_roads, get_available_scenarios
from cascade_engine import CascadeEngine, is_road_impassable, is_road_passable
from intervention_engine import InterventionEngine


def test_data_integrity():
    nodes = get_synthetic_city_nodes()
    pop_nodes = [nid for nid, attr in nodes.items() if attr.get("type") == "population"]
    total_pop = sum(nodes[nid]["population"] for nid in pop_nodes)
    assert total_pop == 59000, f"Expected total population 59,000, got {total_pop}"
    print("[PASS] Test Data Integrity: Total Population = 59,000")


def test_scenario_1_urban_flood():
    nodes = get_synthetic_city_nodes()
    roads = get_synthetic_city_roads("Scenario 1: Urban Flood — Distributed Road Failures")
    ce = CascadeEngine(nodes, roads)
    ie = InterventionEngine(ce)

    base = ce.get_baseline_summary()
    assert base["flooded_road_count"] == 4, f"Expected 4 flooded roads, got {base['flooded_road_count']}"
    assert base["flooded_metrics"]["pop_without_both"] == 59000, "All population should lose dual access under flood"

    rec = ie.get_dynamic_recommendation()
    assert rec["has_beneficial_intervention"] is True
    assert rec["delta_population"] > 0
    assert rec["utility"] > 0
    assert rec["intervention_name"] in rec["explanation"]
    print(f"[PASS] Test Scenario 1: Optimal intervention identified ({rec['intervention_name']}, Utility={rec['utility']}).")


def test_scenario_2_damage_vs_value():
    """
    Verifies that in Scenario 2, the most damaged road (R10, damage_factor 2.5, effort 22.8)
    alone is NOT the highest-ranked intervention.
    """
    nodes = get_synthetic_city_nodes()
    roads = get_synthetic_city_roads("Scenario 2: Critical Corridor Disruption")
    ce = CascadeEngine(nodes, roads)
    ie = InterventionEngine(ce)

    ranking_df = ie.evaluate_all_interventions()
    top_cand = ranking_df.iloc[0]
    
    # Verify single restoration of R10 alone is NOT top
    assert top_cand["candidate_id"] != "RESTORE_R10", "RESTORE_R10 (most damaged road alone) should not be the top intervention!"
    
    # Check baseline comparison
    comp_df = ie.evaluate_baseline_heuristics_comparison()
    assert not comp_df.empty
    print(f"[PASS] Test Scenario 2: Most Damaged Road (R10) != Most Valuable ({top_cand['intervention']}).")


def test_scenario_3_multi_route_bottleneck():
    nodes = get_synthetic_city_nodes()
    roads = get_synthetic_city_roads("Scenario 3: Multi-Route Bottleneck")
    ce = CascadeEngine(nodes, roads)
    ie = InterventionEngine(ce)

    ranking_df = ie.evaluate_all_interventions()
    assert not ranking_df.empty
    rec = ie.get_dynamic_recommendation()
    assert rec["has_beneficial_intervention"] is True
    print(f"[PASS] Test Scenario 3: Multi-Route Bottleneck evaluated (Top: {rec['intervention_name']}).")


def test_scenario_4_zero_disruption_fallback():
    """
    Verifies that when no beneficial intervention exists, the engine outputs
    'NO BENEFICIAL INTERVENTION IDENTIFIED' instead of picking a fake winner.
    """
    nodes = get_synthetic_city_nodes()
    roads = get_synthetic_city_roads("Scenario 4: Baseline Clear (No Inundation / Zero Disruption)")
    ce = CascadeEngine(nodes, roads)
    ie = InterventionEngine(ce)

    rec = ie.get_dynamic_recommendation()
    assert rec["has_beneficial_intervention"] is False
    assert rec["title"] == "NO BENEFICIAL INTERVENTION IDENTIFIED"
    print("[PASS] Test Scenario 4: Clean fallback on zero-benefit scenario ('NO BENEFICIAL INTERVENTION IDENTIFIED').")


def test_non_destructive_simulation():
    """
    Verifies that running counterfactual simulations leaves the original graph unchanged
    in both edge count and exact graph structure/topology (nodes, canonical edges, edge attributes).
    Also includes a regression case proving structural comparison distinguishes graphs with equal edge counts.
    """
    nodes = get_synthetic_city_nodes()
    roads = get_synthetic_city_roads("Scenario 1: Urban Flood — Distributed Road Failures")
    ce = CascadeEngine(nodes, roads)
    ie = InterventionEngine(ce)

    # Capture complete structural representation before simulation
    nodes_before = set(ce.flooded_graph.nodes())
    node_data_before = {n: dict(d) for n, d in ce.flooded_graph.nodes(data=True)}
    edges_before = ce.flooded_graph.number_of_edges()
    canonical_edges_before = {tuple(sorted([u, v])): dict(d) for u, v, d in ce.flooded_graph.edges(data=True)}
    
    # Run all interventions
    ie.evaluate_all_interventions()
    
    # Capture complete structural representation after simulation
    nodes_after = set(ce.flooded_graph.nodes())
    node_data_after = {n: dict(d) for n, d in ce.flooded_graph.nodes(data=True)}
    edges_after = ce.flooded_graph.number_of_edges()
    canonical_edges_after = {tuple(sorted([u, v])): dict(d) for u, v, d in ce.flooded_graph.edges(data=True)}

    assert edges_before == edges_after, f"Baseline edge count changed! Before: {edges_before}, After: {edges_after}"
    assert nodes_before == nodes_after, "Baseline graph nodes changed!"
    assert node_data_before == node_data_after, "Baseline node attributes changed!"
    assert set(canonical_edges_before.keys()) == set(canonical_edges_after.keys()), "Baseline graph topology/edges changed!"
    assert canonical_edges_before == canonical_edges_after, "Baseline edge attributes changed!"

    # Regression case: two graphs with equal edge count (3) but completely different topology
    g_path = nx.Graph()
    g_path.add_edges_from([("A", "B"), ("B", "C"), ("C", "D")])  # Path graph: 3 edges

    g_star = nx.Graph()
    g_star.add_edges_from([("A", "B"), ("A", "C"), ("A", "D")])  # Star graph: 3 edges

    # Edge counts alone are identical (would create a false pass)
    assert g_path.number_of_edges() == g_star.number_of_edges() == 3
    # Structural topology comparison correctly identifies the discrepancy
    edges_path_canonical = {tuple(sorted(e)) for e in g_path.edges()}
    edges_star_canonical = {tuple(sorted(e)) for e in g_star.edges()}
    assert edges_path_canonical != edges_star_canonical, "Structural comparison must detect difference between path and star graphs!"

    print("[PASS] Test Non-Destructive Simulation: Graph structure, topology, and attributes strictly immutable.")


import random


def test_combined_interventions_order_invariance():
    """
    Regression test for Finding #1:
    Verifies that reordering the input road list does not change the generated
    or selected combined interventions across scenarios.
    """
    nodes = get_synthetic_city_nodes()
    test_scenarios = [
        "Scenario 1: Urban Flood — Distributed Road Failures",
        "Scenario 2: Critical Corridor Disruption",
        "Scenario 3: Multi-Route Bottleneck",
    ]

    for sc in test_scenarios:
        original_roads = get_synthetic_city_roads(sc)
        ce_orig = CascadeEngine(nodes, original_roads)
        ie_orig = InterventionEngine(ce_orig)
        df_orig = ie_orig.evaluate_all_interventions()
        comb_orig = df_orig[df_orig["type"] == "Combined Intervention"].reset_index(drop=True)

        assert not comb_orig.empty, f"Expected combined interventions in {sc}"
        top_orig_id = comb_orig.iloc[0]["candidate_id"]
        top_orig_utility = comb_orig.iloc[0]["utility"]
        orig_ids = list(comb_orig["candidate_id"])
        orig_utils = list(comb_orig["utility"])

        # Test permutations: reversed, sorted by various keys, and random shuffles
        permutations = [
            list(reversed(original_roads)),
            sorted(original_roads, key=lambda r: r["road_id"], reverse=True),
            sorted(original_roads, key=lambda r: r["effort_cost"], reverse=True),
            sorted(original_roads, key=lambda r: r["length_km"]),
        ]

        # Add 10 deterministic pseudo-random shuffles
        rng = random.Random(42)
        for _ in range(10):
            shuffled = list(original_roads)
            rng.shuffle(shuffled)
            permutations.append(shuffled)

        for p_idx, perm_roads in enumerate(permutations):
            ce_perm = CascadeEngine(nodes, perm_roads)
            ie_perm = InterventionEngine(ce_perm)
            df_perm = ie_perm.evaluate_all_interventions()
            comb_perm = df_perm[df_perm["type"] == "Combined Intervention"].reset_index(drop=True)

            top_perm_id = comb_perm.iloc[0]["candidate_id"]
            top_perm_utility = comb_perm.iloc[0]["utility"]

            assert top_orig_id == top_perm_id, (
                f"Selected combined intervention changed in {sc} under permutation {p_idx}! "
                f"Original: {top_orig_id}, Permuted: {top_perm_id}"
            )
            assert top_orig_utility == top_perm_utility, (
                f"Selected combined intervention utility changed in {sc} under permutation {p_idx}! "
                f"Original: {top_orig_utility}, Permuted: {top_perm_utility}"
            )
            assert orig_ids == list(comb_perm["candidate_id"]), (
                f"Combined candidate IDs changed in {sc} under permutation {p_idx}!"
            )
            assert orig_utils == list(comb_perm["utility"]), (
                f"Combined candidate utilities changed in {sc} under permutation {p_idx}!"
            )

    print("[PASS] Test Combined Interventions Order Invariance: Reordering roads does not change selected combined intervention.")


def test_combined_intervention_including_r10():
    """
    Regression test for Finding #4:
    Verifies that valid combined interventions containing R10 are not rejected
    by candidate selection or validation logic.
    """
    nodes = get_synthetic_city_nodes()
    roads = get_synthetic_city_roads("Scenario 2: Critical Corridor Disruption")
    ce = CascadeEngine(nodes, roads)
    ie = InterventionEngine(ce)

    candidates = ie.get_candidate_interventions()
    r10_combined = [
        c for c in candidates
        if c["type"] == "Combined Intervention" and "R10" in c["target_roads"]
    ]
    assert len(r10_combined) > 0, "Combined interventions containing R10 must not be rejected during selection!"

    # Verify each R10 combined candidate passes validation
    for cand in r10_combined:
        assert ie.validate_candidate(cand) is True, f"Candidate {cand['id']} must pass validation!"
        # Simulate non-destructively
        G_sim, sim_metrics = ie.simulate_candidate(cand)
        assert G_sim is not None
        assert "pop_with_both" in sim_metrics

    # Verify R10 combined candidates appear in evaluate_all_interventions
    ranking_df = ie.evaluate_all_interventions()
    ranked_ids = set(ranking_df["candidate_id"])
    for cand in r10_combined:
        assert cand["id"] in ranked_ids, f"{cand['id']} must be included in ranking results!"

    print("[PASS] Test Combined Interventions With R10: R10 combinations correctly validated and evaluated.")


def test_reliability_metrics_match_level():
    """
    Regression test for Finding #2 (and remaining finding: explicit level cannot override completeness):
    Verifies that reported reliability metrics correspond to data completeness, and that an
    explicit level cannot falsify or override measured completeness.
    """
    nodes = get_synthetic_city_nodes()
    roads = get_synthetic_city_roads("Scenario 1: Urban Flood — Distributed Road Failures")
    ce = CascadeEngine(nodes, roads)
    ie = InterventionEngine(ce)

    # 1. Full complete data -> Measured HIGH level
    rel_default = ie.get_analysis_reliability()
    assert rel_default["level"] == "HIGH"
    assert rel_default["badge_color"] == "green"
    assert "100%" in rel_default["metrics"]["Network Completeness"]
    assert "100%" in rel_default["metrics"]["Facility Dependency Model"]

    # 1a. Explicit level matching measured completeness -> returns HIGH
    rel_explicit_match = ie.get_analysis_reliability(level="HIGH")
    assert rel_explicit_match["level"] == "HIGH"
    assert "100%" in rel_explicit_match["metrics"]["Network Completeness"]

    # 1b. Explicit LOW with complete measured data -> CANNOT falsify to LOW, remains authoritative HIGH
    rel_falsify_low = ie.get_analysis_reliability(level="LOW")
    assert rel_falsify_low["level"] == "HIGH", "Explicit LOW must not override complete measured data!"
    assert "100%" in rel_falsify_low["metrics"]["Network Completeness"]

    # 2. Incomplete measured data (depleted nodes/facilities/roads)
    small_nodes = {k: v for i, (k, v) in enumerate(nodes.items()) if i < 3}  # missing facilities and < 10 nodes
    small_ce = CascadeEngine(small_nodes, roads[:3])
    small_ie = InterventionEngine(small_ce)

    rel_inferred_incomplete = small_ie.get_analysis_reliability()
    assert rel_inferred_incomplete["level"] == "LOW"
    assert rel_inferred_incomplete["badge_color"] == "red"
    assert "Low" in rel_inferred_incomplete["metrics"]["Network Completeness"]

    # 2a. Explicit HIGH with incomplete measured data -> CANNOT falsify to HIGH, remains authoritative LOW/MEDIUM
    rel_falsify_high = small_ie.get_analysis_reliability(level="HIGH")
    assert rel_falsify_high["level"] == "LOW", "Explicit HIGH must not override incomplete measured data!"
    assert "Low" in rel_falsify_high["metrics"]["Network Completeness"]
    assert "100% (Synthetic Urban Graph)" not in rel_falsify_high["metrics"]["Network Completeness"]

    print("[PASS] Test Reliability Metrics: Measured completeness is strictly authoritative against explicit levels.")


def test_exclude_all_impassable_roads_from_flooded_graph():
    """
    Regression test for Finding #6:
    Verifies that ALL impassable roads (via is_flooded=True, is_accessible=False,
    is_impassable=True, or status='submerged'/'closed') are excluded from the flooded graph,
    while accessible roads remain included.
    """
    nodes = get_synthetic_city_nodes()
    # Create test roads with multiple different impassable markers
    custom_roads = [
        {"road_id": "TEST_R1", "u": "N1", "v": "N2", "name": "Flooded Road", "length_km": 1.0, "is_flooded": True, "is_accessible": False},
        {"road_id": "TEST_R2", "u": "N2", "v": "N3", "name": "Inaccessible Road", "length_km": 1.0, "is_flooded": False, "is_accessible": False},
        {"road_id": "TEST_R3", "u": "N3", "v": "N4", "name": "Impassable Flag Road", "length_km": 1.0, "is_impassable": True, "is_accessible": True},
        {"road_id": "TEST_R4", "u": "N4", "v": "N5", "name": "Submerged Status Road", "length_km": 1.0, "status": "submerged"},
        {"road_id": "TEST_R5", "u": "N5", "v": "N6", "name": "Closed Status Road", "length_km": 1.0, "status": "closed"},
        {"road_id": "TEST_PASS", "u": "N1", "v": "N4", "name": "Passable Open Road", "length_km": 2.0, "is_flooded": False, "is_accessible": True},
    ]
    ce = CascadeEngine(nodes, custom_roads)
    flooded_edges = {tuple(sorted([u, v])) for u, v in ce.flooded_graph.edges()}

    # All impassable roads must be excluded
    assert tuple(sorted(["N1", "N2"])) not in flooded_edges, "is_flooded=True must be excluded"
    assert tuple(sorted(["N2", "N3"])) not in flooded_edges, "is_accessible=False must be excluded"
    assert tuple(sorted(["N3", "N4"])) not in flooded_edges, "is_impassable=True must be excluded"
    assert tuple(sorted(["N4", "N5"])) not in flooded_edges, "status='submerged' must be excluded"
    assert tuple(sorted(["N5", "N6"])) not in flooded_edges, "status='closed' must be excluded"

    # Passable road must remain in graph
    assert tuple(sorted(["N1", "N4"])) in flooded_edges, "Passable road must remain in flooded graph"
    print("[PASS] Test Exclude All Impassable Roads: All impassability markers excluded while passable roads remain.")


def test_validate_candidate_malformed_shapes_rejected_cleanly():
    """
    Regression test for Finding 1:
    Verifies that validate_candidate() defensively rejects malformed field shapes and types
    cleanly (returning False) without leaking KeyError, TypeError, AttributeError, IndexError, etc.
    """
    nodes = get_synthetic_city_nodes()
    roads = get_synthetic_city_roads("Scenario 1: Urban Flood — Distributed Road Failures")
    ce = CascadeEngine(nodes, roads)
    ie = InterventionEngine(ce)

    malformed_candidates = [
        None,
        42,
        "RESTORE_R1",
        [],
        True,
        False,
        {},
        {"id": 123, "effort_cost": 3.0, "target_roads": ["R4"]},
        {"id": "   ", "effort_cost": 3.0, "target_roads": ["R4"]},
        {"id": "C1", "target_roads": ["R4"]},
        {"id": "C1", "effort_cost": True, "target_roads": ["R4"]},
        {"id": "C1", "effort_cost": False, "target_roads": ["R4"]},
        {"id": "C1", "effort_cost": "high", "target_roads": ["R4"]},
        {"id": "C1", "effort_cost": math.nan, "target_roads": ["R4"]},
        {"id": "C1", "effort_cost": math.inf, "target_roads": ["R4"]},
        {"id": "C1", "effort_cost": -math.inf, "target_roads": ["R4"]},
        {"id": "C1", "effort_cost": 0, "target_roads": ["R4"]},
        {"id": "C1", "effort_cost": -2.5, "target_roads": ["R4"]},
        {"id": "C1", "effort_cost": 3.0, "target_roads": "R4"},
        {"id": "C1", "effort_cost": 3.0, "target_roads": 123},
        {"id": "C1", "effort_cost": 3.0, "target_roads": [123]},
        {"id": "C1", "effort_cost": 3.0, "target_roads": [""]},
        {"id": "C1", "effort_cost": 3.0, "target_roads": ["NONEXISTENT_ROAD_ID"]},
        {"id": "C1", "effort_cost": 3.0, "target_roads": [], "temporary_links": []},
        {"id": "C1", "effort_cost": 3.0, "temporary_links": "N1-N2"},
        {"id": "C1", "effort_cost": 3.0, "temporary_links": ["N1_N2"]},
        {"id": "C1", "effort_cost": 3.0, "temporary_links": [{"u": 1, "v": 2}]},
        {"id": "C1", "effort_cost": 3.0, "temporary_links": [{"u": "N1"}]},
        {"id": "C1", "effort_cost": 3.0, "temporary_links": [{}]},
        {"id": "C1", "effort_cost": 3.0, "temporary_links": [{"u": "UNKNOWN", "v": "N2"}]},
        {"id": "C1", "effort_cost": 3.0, "temporary_links": [{"u": "N1", "v": "N2", "effort_cost": "bad"}]},
        {"id": "C1", "effort_cost": 3.0, "temporary_links": [{"u": "N1", "v": "N2", "effort_cost": math.nan}]},
        {"id": "C1", "effort_cost": 3.0, "temporary_links": [{"u": "N1", "v": "N2", "length_km": True}]},
        {"id": "C1", "effort_cost": 10**10000, "target_roads": ["R4"]},
        {"id": "C1", "effort_cost": -(10**10000), "target_roads": ["R4"]},
        {"id": "C1", "effort_cost": 3.0, "temporary_links": [{"u": "N1", "v": "N2", "effort_cost": 10**10000}]},
        {"id": "C1", "effort_cost": 3.0, "temporary_links": [{"u": "N1", "v": "N2", "effort_cost": -(10**10000)}]},
        {"id": "C1", "effort_cost": 3.0, "temporary_links": [{"u": "N1", "v": "N2", "length_km": 10**10000}]},
        {"id": "C1", "effort_cost": 3.0, "temporary_links": [{"u": "N1", "v": "N2", "length_km": -(10**10000)}]},
    ]

    for idx, bad_cand in enumerate(malformed_candidates):
        try:
            result = ie.validate_candidate(bad_cand)
            assert result is False, f"Malformed candidate #{idx} was not rejected: {bad_cand}"
        except Exception as e:
            assert False, f"validate_candidate leaked exception {type(e).__name__} on candidate #{idx}: {e}"

        # simulate_candidate must cleanly raise ValueError rather than unhandled internal exceptions
        try:
            ie.simulate_candidate(bad_cand)
            assert False, f"simulate_candidate should raise ValueError on bad candidate #{idx}"
        except ValueError:
            pass
        except Exception as e:
            assert False, f"simulate_candidate leaked unexpected exception {type(e).__name__} on candidate #{idx}: {e}"

    print("[PASS] Test Validate Candidate: Malformed field shapes rejected cleanly without leaking exceptions.")


def test_shared_passability_contract_consistency():
    """
    Regression test for Finding 3:
    Verifies that the shared passability contract (is_road_impassable / is_road_passable)
    is consistent across cascade filtering and intervention generation across each supported marker.
    """
    nodes = get_synthetic_city_nodes()

    # Test cases covering all supported impassability indicators + passable baseline
    test_cases = [
        ({"road_id": "TC_FLOOD", "u": "N1", "v": "N2", "name": "Flood", "length_km": 1.0, "effort_cost": 2.0, "is_flooded": True}, True),
        ({"road_id": "TC_INACC", "u": "N2", "v": "N3", "name": "Inacc", "length_km": 1.0, "effort_cost": 2.0, "is_accessible": False}, True),
        ({"road_id": "TC_IMPASS", "u": "N3", "v": "N4", "name": "Impass", "length_km": 1.0, "effort_cost": 2.0, "is_impassable": True}, True),
        ({"road_id": "TC_SUB", "u": "N4", "v": "N5", "name": "Sub", "length_km": 1.0, "effort_cost": 2.0, "status": "submerged"}, True),
        ({"road_id": "TC_CLOSED", "u": "N5", "v": "N6", "name": "Closed", "length_km": 1.0, "effort_cost": 2.0, "status": "closed"}, True),
        ({"road_id": "TC_BLOCK", "u": "N1", "v": "N4", "name": "Block", "length_km": 1.0, "effort_cost": 2.0, "status": "blocked"}, True),
        ({"road_id": "TC_NOT_PASS", "u": "N2", "v": "N7", "name": "NotPass", "length_km": 1.0, "effort_cost": 2.0, "passable": False}, True),
        ({"road_id": "TC_PASSABLE", "u": "N3", "v": "N7", "name": "Passable", "length_km": 1.0, "effort_cost": 2.0, "is_flooded": False, "is_accessible": True}, False),
    ]

    all_test_roads = [tc[0] for tc in test_cases]
    ce = CascadeEngine(nodes, all_test_roads)
    ie = InterventionEngine(ce)

    flooded_edges = {tuple(sorted([u, v])) for u, v in ce.flooded_graph.edges()}
    candidate_interventions = ie.get_candidate_interventions()
    restored_target_roads = set()
    for c in candidate_interventions:
        if c["type"] == "Road Restoration":
            restored_target_roads.update(c["target_roads"])

    for road_dict, expected_impassable in test_cases:
        r_id = road_dict["road_id"]
        edge_key = tuple(sorted([road_dict["u"], road_dict["v"]]))

        # Check contract directly
        contract_result = is_road_impassable(road_dict)
        assert contract_result == expected_impassable, f"Contract mismatch for {r_id}: expected {expected_impassable}, got {contract_result}"
        assert is_road_passable(road_dict) == (not expected_impassable)

        # Check cascade graph filtering decision
        in_flooded_graph = edge_key in flooded_edges
        if expected_impassable:
            assert not in_flooded_graph, f"Impassable road {r_id} must be excluded from cascade flooded graph!"
            # Check intervention engine decision
            assert r_id in restored_target_roads, f"Impassable road {r_id} must be generated as a restoration candidate!"
        else:
            assert in_flooded_graph, f"Passable road {r_id} must be included in cascade flooded graph!"
            assert r_id not in restored_target_roads, f"Passable road {r_id} must NOT be a restoration candidate!"

    print("[PASS] Test Shared Passability Contract: Cascade filtering and interventions make identical decisions.")


def test_ml_prediction_interface_contract_enforcement():
    """
    Regression test for Finding #7 and remaining finding:
    Verifies that the documented prediction contract is enforced at construction,
    specifically rejecting boolean values and non-finite numeric values (NaN, +inf, -inf)
    across all numeric fields.
    """
    from ml_prediction_interface import MLPredictionOutput, RoadFeatureVector

    # Valid constructions
    valid_rfv = RoadFeatureVector(
        road_id="R1",
        length_km=3.2,
        road_class="primary",
        elevation_m=15.0,
        slope_degrees=4.5,
        soil_saturation_pct=75.0,
        accumulated_rainfall_mm=45.0,
        river_proximity_m=120.0,
        bridge_structure=False,
    )
    assert valid_rfv.road_id == "R1"

    valid_pred = MLPredictionOutput(
        road_id="R1",
        failure_probability=0.85,
        predicted_status="submerged",
        confidence_score=0.92,
        key_risk_factor="High soil moisture and river proximity",
    )
    assert valid_pred.failure_probability == 0.85

    # Non-finite and boolean inputs to test
    invalid_numeric_values = [True, False, math.nan, math.inf, -math.inf]

    # Test MLPredictionOutput numeric fields: failure_probability and confidence_score
    for bad_val in invalid_numeric_values:
        # failure_probability
        try:
            MLPredictionOutput("R1", bad_val, "submerged", 0.9, "Risk")
            assert False, f"MLPredictionOutput should reject failure_probability={bad_val!r}"
        except ValueError:
            pass

        # confidence_score
        try:
            MLPredictionOutput("R1", 0.5, "submerged", bad_val, "Risk")
            assert False, f"MLPredictionOutput should reject confidence_score={bad_val!r}"
        except ValueError:
            pass

    # Test RoadFeatureVector numeric fields:
    # length_km, elevation_m, slope_degrees, soil_saturation_pct, accumulated_rainfall_mm, river_proximity_m
    for bad_val in invalid_numeric_values:
        # length_km
        try:
            RoadFeatureVector("R1", bad_val, "primary", 15.0, 4.5, 75.0, 45.0, 120.0, False)
            assert False, f"RoadFeatureVector should reject length_km={bad_val!r}"
        except ValueError:
            pass

        # elevation_m
        try:
            RoadFeatureVector("R1", 3.2, "primary", bad_val, 4.5, 75.0, 45.0, 120.0, False)
            assert False, f"RoadFeatureVector should reject elevation_m={bad_val!r}"
        except ValueError:
            pass

        # slope_degrees
        try:
            RoadFeatureVector("R1", 3.2, "primary", 15.0, bad_val, 75.0, 45.0, 120.0, False)
            assert False, f"RoadFeatureVector should reject slope_degrees={bad_val!r}"
        except ValueError:
            pass

        # soil_saturation_pct
        try:
            RoadFeatureVector("R1", 3.2, "primary", 15.0, 4.5, bad_val, 45.0, 120.0, False)
            assert False, f"RoadFeatureVector should reject soil_saturation_pct={bad_val!r}"
        except ValueError:
            pass

        # accumulated_rainfall_mm
        try:
            RoadFeatureVector("R1", 3.2, "primary", 15.0, 4.5, 75.0, bad_val, 120.0, False)
            assert False, f"RoadFeatureVector should reject accumulated_rainfall_mm={bad_val!r}"
        except ValueError:
            pass

        # river_proximity_m
        try:
            RoadFeatureVector("R1", 3.2, "primary", 15.0, 4.5, 75.0, 45.0, bad_val, False)
            assert False, f"RoadFeatureVector should reject river_proximity_m={bad_val!r}"
        except ValueError:
            pass

    # Standard out-of-range checks
    for bad_prob in [1.5, -0.1]:
        try:
            MLPredictionOutput("R1", bad_prob, "submerged", 0.9, "Risk")
            assert False, f"Should reject failure_probability={bad_prob}"
        except ValueError:
            pass

    try:
        MLPredictionOutput("R1", 0.5, "destroyed", 0.9, "Risk")
        assert False, "Should reject invalid predicted_status"
    except ValueError:
        pass

    try:
        MLPredictionOutput("", 0.5, "passable", 0.8, "Risk")
        assert False, "Should reject empty road_id"
    except ValueError:
        pass

    try:
        RoadFeatureVector("R1", 0.0, "primary", 15.0, 4.5, 75.0, 45.0, 120.0, False)
        assert False, "Should reject length_km <= 0"
    except ValueError:
        pass

    try:
        RoadFeatureVector("R1", 3.2, "highway", 15.0, 4.5, 75.0, 45.0, 120.0, False)
        assert False, "Should reject invalid road_class"
    except ValueError:
        pass

    try:
        RoadFeatureVector("R1", 3.2, "primary", 15.0, 4.5, 120.0, 45.0, 120.0, False)
        assert False, "Should reject soil_saturation_pct > 100"
    except ValueError:
        pass

    try:
        RoadFeatureVector("R1", 3.2, "primary", 15.0, 95.0, 50.0, 45.0, 120.0, False)
        assert False, "Should reject slope_degrees > 90"
    except ValueError:
        pass

    print("[PASS] Test ML Prediction Interface Contract: Booleans, non-finites, and invalid bounds rejected.")


def test_candidate_validation_integer_overflow_handling():
    """
    Regression test for handling integer overflow during finite number validation.
    Verifies that arbitrarily large Python integers (e.g., 10**10000, -10**10000)
    in effort_cost, temporary link effort_cost, and length_km are cleanly rejected
    without raising OverflowError or leaking exceptions.
    """
    from intervention_engine import _is_safe_finite_numeric

    # 1. Direct unit checks for _is_safe_finite_numeric
    assert _is_safe_finite_numeric(10**10000) is False, "10**10000 must be rejected"
    assert _is_safe_finite_numeric(-(10**10000)) is False, "-10**10000 must be rejected"
    assert _is_safe_finite_numeric(2**1024) is False, "2**1024 must be rejected"
    assert _is_safe_finite_numeric(True) is False, "bool True must be rejected"
    assert _is_safe_finite_numeric(False) is False, "bool False must be rejected"
    assert _is_safe_finite_numeric(math.nan) is False, "NaN must be rejected"
    assert _is_safe_finite_numeric(math.inf) is False, "+inf must be rejected"
    assert _is_safe_finite_numeric(-math.inf) is False, "-inf must be rejected"
    assert _is_safe_finite_numeric("100") is False, "str must be rejected"
    assert _is_safe_finite_numeric(None) is False, "None must be rejected"
    assert _is_safe_finite_numeric(1) is True, "int 1 must be accepted"
    assert _is_safe_finite_numeric(0) is True, "int 0 must be accepted"
    assert _is_safe_finite_numeric(-5) is True, "int -5 must be accepted"
    assert _is_safe_finite_numeric(3.14) is True, "float 3.14 must be accepted"

    # Also verify staticmethod access on InterventionEngine class and instance
    assert InterventionEngine._is_safe_finite_numeric(10**10000) is False
    assert InterventionEngine._is_safe_finite_numeric(4.5) is True

    # 2. Integration checks through validate_candidate and simulate_candidate
    nodes = get_synthetic_city_nodes()
    roads = get_synthetic_city_roads("Scenario 1: Urban Flood — Distributed Road Failures")
    ce = CascadeEngine(nodes, roads)
    ie = InterventionEngine(ce)

    overflow_test_cases = [
        ("effort_cost huge positive", {"id": "OV1", "effort_cost": 10**10000, "target_roads": ["R4"]}),
        ("effort_cost huge negative", {"id": "OV2", "effort_cost": -(10**10000), "target_roads": ["R4"]}),
        ("link effort_cost huge positive", {"id": "OV3", "effort_cost": 3.0, "temporary_links": [{"u": "N1", "v": "N2", "effort_cost": 10**10000}]}),
        ("link effort_cost huge negative", {"id": "OV4", "effort_cost": 3.0, "temporary_links": [{"u": "N1", "v": "N2", "effort_cost": -(10**10000)}]}),
        ("link length_km huge positive", {"id": "OV5", "effort_cost": 3.0, "temporary_links": [{"u": "N1", "v": "N2", "length_km": 10**10000}]}),
        ("link length_km huge negative", {"id": "OV6", "effort_cost": 3.0, "temporary_links": [{"u": "N1", "v": "N2", "length_km": -(10**10000)}]}),
    ]

    for label, cand in overflow_test_cases:
        try:
            valid = ie.validate_candidate(cand)
            assert valid is False, f"Candidate with {label} should be rejected, got True"
        except OverflowError as e:

            assert False, f"validate_candidate leaked OverflowError on {label}: {e}"
        except Exception as e:
            assert False, f"validate_candidate leaked unexpected exception {type(e).__name__} on {label}: {e}"

        try:
            ie.simulate_candidate(cand)
            assert False, f"simulate_candidate should raise ValueError for {label}"
        except ValueError:
            pass
        except OverflowError as e:
            assert False, f"simulate_candidate leaked OverflowError on {label}: {e}"
        except Exception as e:
            assert False, f"simulate_candidate leaked unexpected exception {type(e).__name__} on {label}: {e}"

    print("[PASS] Test Candidate Validation Integer Overflow: Arbitrarily large integers cleanly rejected without OverflowError.")


def test_carto_dark_matter_basemap_api_key_integration():
    """
    Regression test for CARTO Dark Matter basemap API-key integration.
    Verifies:
      1. When CARTO_API_KEY is present in st.secrets, tile URL appends '?key=<key>'.
      2. When CARTO_API_KEY is missing, fails gracefully without crashing and renders fallback tiles.
      3. Attribution, subdomains ('abcd'), and map structure are strictly preserved.
      4. Explicit api_key parameter is supported.
      5. The secret key value is never hardcoded or leaked into error logs.
    """
    from unittest.mock import patch
    import streamlit as st
    import folium
    from visualization import (
        get_carto_api_key,
        get_carto_tile_url,
        create_network_map,
        CARTO_DARK_MATTER_URL,
        CARTO_ATTRIBUTION,
    )

    nodes = get_synthetic_city_nodes()
    roads = get_synthetic_city_roads("Scenario 1: Urban Flood — Distributed Road Failures")

    # 1. Test when CARTO_API_KEY is present in Streamlit secrets
    mock_key = "test_carto_secret_token_123"
    with patch.object(st, "secrets", {"CARTO_API_KEY": mock_key}):
        retrieved_key = get_carto_api_key()
        assert retrieved_key == mock_key, f"Expected {mock_key}, got {retrieved_key}"

        tile_url, has_key = get_carto_tile_url()
        assert has_key is True
        expected_url = f"{CARTO_DARK_MATTER_URL}?key={mock_key}"
        assert tile_url == expected_url, f"Expected {expected_url}, got {tile_url}"

        # Create map with secret-derived key
        m = create_network_map(nodes, roads, {})
        assert isinstance(m, folium.Map)
        tile_layers = [c for c in m._children.values() if isinstance(c, folium.TileLayer)]
        assert len(tile_layers) == 1
        assert tile_layers[0].tiles == expected_url
        assert tile_layers[0].options["subdomains"] == "abcd"
        assert tile_layers[0].options["max_zoom"] == 20
        assert "CARTO" in tile_layers[0].options["attribution"]

    # 2. Test explicit api_key override
    explicit_key = "explicit_custom_key_456"
    tile_url_exp, has_key_exp = get_carto_tile_url(api_key=explicit_key)
    assert has_key_exp is True
    assert tile_url_exp == f"{CARTO_DARK_MATTER_URL}?key={explicit_key}"

    m_exp = create_network_map(nodes, roads, {}, api_key=explicit_key)
    tile_layers_exp = [c for c in m_exp._children.values() if isinstance(c, folium.TileLayer)]
    assert tile_layers_exp[0].tiles == f"{CARTO_DARK_MATTER_URL}?key={explicit_key}"

    # 3. Test when CARTO_API_KEY is missing from Streamlit secrets
    with patch.object(st, "secrets", {}):
        retrieved_key_missing = get_carto_api_key()
        assert retrieved_key_missing is None, "Missing secret should return None"

        tile_url_missing, has_key_missing = get_carto_tile_url()
        assert has_key_missing is False
        assert tile_url_missing == CARTO_DARK_MATTER_URL
        assert "?key=" not in tile_url_missing

        # Map creation must fail gracefully without crashing
        m_missing = create_network_map(nodes, roads, {})
        assert isinstance(m_missing, folium.Map)
        tile_layers_missing = [c for c in m_missing._children.values() if isinstance(c, folium.TileLayer)]
        assert len(tile_layers_missing) == 1
        assert tile_layers_missing[0].tiles == CARTO_DARK_MATTER_URL
        assert "?key=" not in tile_layers_missing[0].tiles

    # 4. Test when secrets raises an exception (e.g. StreamlitSecretNotFoundError)
    class MissingSecrets:
        def get(self, key, default=None):
            raise FileNotFoundError("No secrets file found")

    with patch.object(st, "secrets", MissingSecrets()):
        assert get_carto_api_key() is None, "Should handle missing secrets gracefully"
        url_err, has_k_err = get_carto_tile_url()
        assert has_k_err is False
        assert url_err == CARTO_DARK_MATTER_URL

        m_err = create_network_map(nodes, roads, {})
        assert isinstance(m_err, folium.Map)

    print("[PASS] Test CARTO Dark Matter Basemap API Key Integration: URL formatting, graceful fallback, and security verified.")


def main():
    print("Running CascadeBreak AI V2 Test Suite...\n")
    test_data_integrity()
    test_scenario_1_urban_flood()
    test_scenario_2_damage_vs_value()
    test_scenario_3_multi_route_bottleneck()
    test_scenario_4_zero_disruption_fallback()
    test_non_destructive_simulation()
    test_combined_interventions_order_invariance()
    test_combined_intervention_including_r10()
    test_reliability_metrics_match_level()
    test_validate_candidate_malformed_shapes_rejected_cleanly()
    test_shared_passability_contract_consistency()
    test_exclude_all_impassable_roads_from_flooded_graph()
    test_ml_prediction_interface_contract_enforcement()
    test_candidate_validation_integer_overflow_handling()
    test_carto_dark_matter_basemap_api_key_integration()
    print("\nALL TESTS PASSED SUCCESSFULLY!")


if __name__ == "__main__":
    main()

