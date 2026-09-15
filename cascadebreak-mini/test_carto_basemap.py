"""
Tests CARTO Dark Matter basemap API key integration in visualization.py.
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
from scenario import get_synthetic_city_nodes, get_synthetic_city_roads


def test_carto_dark_matter_basemap_api_key_integration():
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

        m = create_network_map(nodes, roads, {})
        assert isinstance(m, folium.Map)
        tile_layers = [c for c in m._children.values() if isinstance(c, folium.TileLayer)]
        assert len(tile_layers) == 1
        assert tile_layers[0].tiles == expected_url
        assert tile_layers[0].options["subdomains"] == "abcd"
        assert tile_layers[0].options["max_zoom"] == 20
        assert "CARTO" in tile_layers[0].options["attribution"]

    # 2. Test key formats and variants (lowercase, section, env var, quotes)
    import os
    with patch.object(st, "secrets", {"carto_api_key": "lower_key_1"}):
        assert get_carto_api_key() == "lower_key_1"
    with patch.object(st, "secrets", {"carto": {"api_key": "section_key_2"}}):
        assert get_carto_api_key() == "section_key_2"
    with patch.object(st, "secrets", {"CARTO_API_KEY": '"quoted_key_3"'}):
        assert get_carto_api_key() == "quoted_key_3"
    with patch.object(st, "secrets", {}):
        with patch.dict(os.environ, {"CARTO_API_KEY": "env_key_4"}):
            assert get_carto_api_key() == "env_key_4"

    # 3. Test explicit api_key override
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
        assert retrieved_key_missing is None

        tile_url_missing, has_key_missing = get_carto_tile_url()
        assert has_key_missing is False
        assert tile_url_missing == CARTO_DARK_MATTER_URL
        assert "?key=" not in tile_url_missing

        m_missing = create_network_map(nodes, roads, {})
        assert isinstance(m_missing, folium.Map)
        tile_layers_missing = [c for c in m_missing._children.values() if isinstance(c, folium.TileLayer)]
        assert len(tile_layers_missing) == 1
        assert tile_layers_missing[0].tiles == CARTO_DARK_MATTER_URL
        assert "?key=" not in tile_layers_missing[0].tiles

    # 4. Test when secrets raises an exception
    class MissingSecrets:
        def get(self, key, default=None):
            raise FileNotFoundError("No secrets file found")

    with patch.object(st, "secrets", MissingSecrets()):
        assert get_carto_api_key() is None
        url_err, has_k_err = get_carto_tile_url()
        assert has_k_err is False
        assert url_err == CARTO_DARK_MATTER_URL

        m_err = create_network_map(nodes, roads, {})
        assert isinstance(m_err, folium.Map)

    print("[PASS] Test CARTO Dark Matter Basemap API Key Integration: URL formatting, graceful fallback, and security verified.")


if __name__ == "__main__":
    test_carto_dark_matter_basemap_api_key_integration()

