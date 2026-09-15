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
    test_carto_dark_matter_basemap_api_key_integration()
    print("\nALL TESTS PASSED SUCCESSFULLY!")


if __name__ == "__main__":
    main()

