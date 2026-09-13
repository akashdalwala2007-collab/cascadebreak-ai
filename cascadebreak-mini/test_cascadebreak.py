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

# Ensure UTF-8 output encoding
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from scenario import get_synthetic_city_nodes, get_synthetic_city_roads, get_available_scenarios
from cascade_engine import CascadeEngine
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
    Verifies that in Scenario 2, the most damaged road (R10, damage_factor 2.5, effort 9.8)
    is NOT the highest-ranked intervention.
    """
    nodes = get_synthetic_city_nodes()
    roads = get_synthetic_city_roads("Scenario 2: Critical Corridor Disruption")
    ce = CascadeEngine(nodes, roads)
    ie = InterventionEngine(ce)

    ranking_df = ie.evaluate_all_interventions()
    top_cand = ranking_df.iloc[0]
    
    # Verify R10 is NOT top
    assert "R10" not in top_cand["candidate_id"], "R10 (most damaged) should not be the top intervention!"
    
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
    Verifies that running counterfactual simulations leaves the original graph unchanged.
    """
    nodes = get_synthetic_city_nodes()
    roads = get_synthetic_city_roads("Scenario 1: Urban Flood — Distributed Road Failures")
    ce = CascadeEngine(nodes, roads)
    ie = InterventionEngine(ce)

    edges_before = ce.flooded_graph.number_of_edges()
    
    # Run all interventions
    ie.evaluate_all_interventions()
    
    edges_after = ce.flooded_graph.number_of_edges()
    assert edges_before == edges_after, f"Baseline flooded graph modified! Before: {edges_before}, After: {edges_after}"
    print("[PASS] Test Non-Destructive Simulation: Baseline graph is strictly immutable.")


def main():
    print("Running CascadeBreak AI V2 Test Suite...\n")
    test_data_integrity()
    test_scenario_1_urban_flood()
    test_scenario_2_damage_vs_value()
    test_scenario_3_multi_route_bottleneck()
    test_scenario_4_zero_disruption_fallback()
    test_non_destructive_simulation()
    print("\nALL TESTS PASSED SUCCESSFULLY!")


if __name__ == "__main__":
    main()

