# Codebase Concerns

**Analysis Date:** 2026-09-13

## Tech Debt

**Inline CSS/HTML Monolith in Application Layer:**
- Issue: Over 350 lines of custom CSS and inline HTML string literals are embedded directly inside Python functions in `cascadebreak-mini/app.py` and `cascadebreak-mini/visualization.py`.
- Files: `cascadebreak-mini/app.py:44-480`, `cascadebreak-mini/visualization.py:101-287`
- Impact: Code readability is degraded; syntax highlighting and CSS linting are unavailable; any string manipulation or styling changes risk breaking Python syntax.
- Fix approach: Extract all custom styles into a dedicated `cascadebreak-mini/assets/style.css` file and load it via `st.markdown()` at startup. Replace raw HTML blocks with reusable UI helper components.

**Duplicated Code from Incomplete Theme Merge:**
- Issue: Several styling declarations and function parameters are duplicated back-to-back due to an unmerged dark tactical theme refactor.
- Files:
  - `cascadebreak-mini/app.py:47-53, 95-101, 151-161, 250-256`
  - `cascadebreak-mini/visualization.py:54-55, 72-73, 75-76, 81-87, 92-96`
- Impact: Confuses developers, creates dead code branches, and bloats the codebase.
- Fix approach: Clean up duplicated lines and enforce a single canonical styling definition for cards, metrics, and folium polyline weights.

**Committed Bytecode Cache:**
- Issue: `cascadebreak-mini/__pycache__/` contains 8 compiled `.pyc` files across multiple Python versions (`cpython-312` and `cpython-314`) tracked directly in the project directory.
- Files: `cascadebreak-mini/__pycache__/*.pyc`
- Impact: Repository bloat and potential caching conflicts across environments.
- Fix approach: Add `.gitignore` ignoring `__pycache__/`, `*.pyc`, and `.venv/`, and delete existing cache files.

## Known Bugs

*(None currently known — previous launch-blocking syntax errors in `app.py` and `visualization.py` resolved on 2026-09-13).*

## Security Considerations

**Unrestricted Streamlit Server Exposure:**
- Risk: In `cascadebreak-mini/.streamlit/config.toml`, `enableCORS = false` and `enableXsrfProtection = false` are configured.
- Files: `cascadebreak-mini/.streamlit/config.toml:11-12`
- Current mitigation: None (assumed local developer execution).
- Recommendations: Enable XSRF protection (`enableXsrfProtection = true`) and configure explicit CORS origins prior to any public network or cloud deployment.

**Raw HTML Ingestion via `st.markdown(unsafe_allow_html=True)`:**
- Risk: Widespread use of `unsafe_allow_html=True` throughout `app.py`. While current data is synthetic, future dynamic user inputs or external API feeds could expose XSS vulnerabilities if injected directly into HTML strings.
- Files: `cascadebreak-mini/app.py`
- Current mitigation: Only synthetic data is rendered.
- Recommendations: Sanitize any external or user-provided strings before rendering in HTML templates.

## Performance Bottlenecks

**Combinatorial Shortest Path Recalculation:**
- Problem: During `InterventionEngine.evaluate_all_interventions()`, Dijkstra shortest path calculations (`nx.shortest_path_length`) are re-evaluated from scratch for every population node to every critical facility across all candidates.
- Files: `cascadebreak-mini/intervention_engine.py:184-188`, `cascadebreak-mini/cascade_engine.py:128-147`
- Cause: Full graph re-evaluation without incremental path updating.
- Improvement path: Acceptable for 11 nodes, but scaling to real-world OpenStreetMap graphs with thousands of nodes will require regional network bounding, A* heuristics, or contraction hierarchies.

## Fragile Areas

**Frontend Rendering Pipeline (`app.py` and `visualization.py`):**
- Files: `cascadebreak-mini/app.py`, `cascadebreak-mini/visualization.py`
- Why fragile: Tight coupling of presentation code, complex HTML string templates, and absence of automated tests for UI components.
- Safe modification: Add a smoke test script that verifies `python -m py_compile` across all repository modules before committing changes.
- Test coverage: 0% automated coverage for `app.py` and `visualization.py`.

## Scaling Limits

**Synthetic Urban Topology vs Real Geospatial Data:**
- Resource/System: Graph model in `cascadebreak-mini/cascade_engine.py`.
- Current limit: 11 nodes and 16 edges with synthetic coordinates and scalar damage factors.
- Scaling boundary: Transitioning to Stage 2 (real Copernicus DEM, Sentinel-1 SAR water masks, OSM road networks) will require geospatial raster processing (`rasterio`, `shapely`, `geopandas`) that cannot be handled in-memory using pure Python dictionaries.

---

*Concerns audit: 2026-09-13*
