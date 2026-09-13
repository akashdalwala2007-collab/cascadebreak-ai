# External Integrations

**Analysis Date:** 2026-09-13

## APIs & External Services

**Geospatial Basemap Provider:**
- CartoDB / Positron & Dark Matter - Provides dark tactical map tiles rendered through Folium/Leaflet.
  - SDK/Client: `folium` (`folium.Map(tiles="CartoDB dark_matter")`) in `cascadebreak-mini/visualization.py`
  - Auth: None (Public Leaflet tile service)
  - Protocol: HTTPS raster tile layer (`https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png`)

**Stage 2 Production Geospatial Ingestion Feeds (Roadmap):**
- European Space Agency (ESA) Copernicus Hub / Google Earth Engine:
  - Purpose: Real-time Sentinel-1 SAR cloud-penetrating synthetic aperture radar imagery for automated flood inundation polygon extraction.
  - Client: `earthengine-api` / Copernicus Open Access Hub REST API.
  - Auth: Planned `EE_SERVICE_ACCOUNT_KEY` or `COPERNICUS_API_KEY`.
- NASA Earthdata (GPM IMERG):
  - Purpose: 6-hour accumulated precipitation and real-time precipitation rates (`accumulated_rainfall_mm`).
  - Client: NASA Earthdata REST API / OpenDAP.
  - Auth: Planned `EARTHDATA_TOKEN`.
- OpenStreetMap (OSM):
  - Purpose: Real-world urban arterial and secondary road network extraction.
  - Client: `osmnx` / Overpass API.
  - Auth: None (Public API with rate limits).
- WorldPop / Meta High Resolution Settlement Layer (HRSL):
  - Purpose: 100m raster population density for zonal exposure statistics.
  - Client: Direct GeoTIFF ingestion via `rasterio`.
  - Auth: Open Data license.

## Data Storage

**Databases:**
- In-Memory NetworkX Graph:
  - Primary topology store maintained in Python memory within `cascadebreak-mini/cascade_engine.py`.
  - Nodes: `dict` of dictionaries keyed by node ID (`N1` to `N11`).
  - Edges: `networkx.Graph` data structure storing length, terrain factor, damage factor, and effort index.
  - Connection: Local process memory (no database server required for synthetic prototype).
  - Client: `networkx>=3.0`

**File Storage:**
- Local filesystem only:
  - Synthetic network topologies defined as static Python dictionaries in `cascadebreak-mini/scenario.py`.
  - Presentation artifacts stored directly in root (`CascadeBreakAIfinal.pptx`, `CascadeBreak_AI_Project_Brief.docx`).
  - Streamlit configuration stored in `cascadebreak-mini/.streamlit/config.toml`.

**Caching:**
- Local Python bytecode caching in `cascadebreak-mini/__pycache__/`.
- Streamlit built-in caching (`@st.cache_data`, `@st.cache_resource`) is not currently applied in `cascadebreak-mini/app.py` (recalculated on each Streamlit rerun).

## Authentication & Identity

**Auth Provider:**
- None (Local/Demo application).
  - Implementation: Open access emergency dashboard for local simulation and decision support. Any user with network access to the Streamlit server port (8501) can interact with scenarios.

## Monitoring & Observability

**Error Tracking:**
- None configured (no Sentry or Rollbar).
- Unhandled Python exceptions bubble up to Streamlit UI stacktrace components.

**Logs:**
- Standard console stdout/stderr:
  - Streamlit runtime logs printed to console.
  - Unit test suite prints formatted output via `print()` to stdout in `cascadebreak-mini/test_cascadebreak.py`.

## CI/CD & Deployment

**Hosting:**
- Local execution or cloud host (Streamlit Cloud, Docker on Linux, AWS EC2 / Azure VM).
- No cloud deployment configuration files found (e.g., no `Dockerfile`, `docker-compose.yml`, or `Procfile`).

**CI Pipeline:**
- None configured in repository (no `.github/workflows/`, `.gitlab-ci.yml`, or Jenkinsfile).
- Tests must be triggered manually using `python cascadebreak-mini/test_cascadebreak.py`.

## Environment Configuration

**Required env vars:**
- None required for baseline synthetic prototype execution.

**Secrets location:**
- No secrets or credentials are used in the codebase.
- No `.env` or credential files present.

## Webhooks & Callbacks

**Incoming:**
- Streamlit internal WebSocket for bidirectional UI reactivity between browser client and Python server.

**Outgoing:**
- None (no external webhooks or notification dispatchers).

---

*Integration audit: 2026-09-13*
