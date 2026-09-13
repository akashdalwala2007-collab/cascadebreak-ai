# Technology Stack

**Analysis Date:** 2026-09-13

## Languages

**Primary:**
- Python 3.12+ (CPython) - Core graph simulation, optimization engine, scenario modeling, and Streamlit web application. Detected bytecodes in `cascadebreak-mini/__pycache__/` indicate compatibility across Python 3.12 and 3.14.

**Secondary:**
- HTML5 / CSS3 - Injected inline custom UI styling within `cascadebreak-mini/app.py` and `cascadebreak-mini/visualization.py` for dark tactical climate-tech GIS dashboard styling.
- TOML - Streamlit server and theme configuration in `cascadebreak-mini/.streamlit/config.toml`.

## Runtime

**Environment:**
- Python 3.12.11 (tested on Windows 64-bit environment)
- Multi-version bytecode artifacts found: `cpython-312.pyc`, `cpython-314.pyc` in `cascadebreak-mini/__pycache__/`

**Package Manager:**
- Pip
- Dependency manifest: `cascadebreak-mini/requirements.txt`
- Lockfile: Missing (`requirements.txt` specifies minimum version ranges with `>=`)

## Frameworks

**Core:**
- Streamlit (`>=1.30.0`) - Web dashboard framework, state management, session handling, UI components (`cascadebreak-mini/app.py`).
- NetworkX (`>=3.0`) - Graph data structures, shortest path calculation (`nx.shortest_path`, `nx.shortest_path_length`), connected components (`nx.number_connected_components`), reachability matrices (`nx.has_path`) (`cascadebreak-mini/cascade_engine.py`).
- Pandas (`>=2.0.0`) - Tabular evaluation of candidate interventions, data sorting, rank assignment, and heuristic strategy comparison (`cascadebreak-mini/intervention_engine.py`).

**Visualization / Geospatial:**
- Folium (`>=0.15.0`) - Interactive geospatial Leaflet.js map renderer with dark matter basemap (`CartoDB dark_matter`), custom DivIcon HUD markers, and polyline route layers (`cascadebreak-mini/visualization.py`).
- Streamlit-Folium (`>=0.17.0`) - Bidirectional rendering bridge embedding Folium map objects within Streamlit layouts (`cascadebreak-mini/app.py`).

**Testing:**
- Python Standard Library (`unittest` style assertions with `assert` statements) in `cascadebreak-mini/test_cascadebreak.py`. Pytest is not configured yet.

**Build/Dev:**
- Standard Python interpreter runtime (`python -m py_compile`, `python script.py`). No build bundler required.

## Key Dependencies

**Critical:**
- `networkx` (`>=3.0`): The foundation for all graph computations. A topological graph model represents urban intersections and critical facilities. Without NetworkX, the cascade engine cannot calculate component fragmentation, hospital accessibility, or relief reachability.
- `streamlit` (`>=1.30.0`): Renders the interactive 10-section decision-support prototype.
- `pandas` (`>=2.0.0`): Manages intervention rankings and heuristic comparison matrices.
- `folium` (`>=0.15.0`) & `streamlit-folium` (`>=0.17.0`): Powers the Before vs After visual counterfactual GIS comparison maps.

**Infrastructure:**
- Microsoft PowerPoint / Word: Project artifacts `CascadeBreakAIfinal.pptx` (10 MB presentation) and `CascadeBreak_AI_Project_Brief.docx` (17 KB project brief) stored in root.

## Configuration

**Environment:**
- No `.env` or external environment variables currently required for the synthetic prototype.
- Stage 2 architecture anticipates future Copernicus API keys, NASA Earthdata credentials, and Google Earth Engine service account tokens.

**Build & UI Configuration:**
- `cascadebreak-mini/.streamlit/config.toml`:
  - `[theme]`: Dark base (`base = "dark"`), Electric Cyan primary accent (`primaryColor = "#22D3EE"`), Deep Navy background (`backgroundColor = "#0B1220"`), Slate dark card background (`secondaryBackgroundColor = "#0F172A"`), off-white text (`textColor = "#F1F5F9"`).
  - `[server]`: Headless execution enabled (`headless = true`), CORS disabled (`enableCORS = false`), XSRF protection disabled (`enableXsrfProtection = false`).

## Platform Requirements

**Development:**
- Python 3.10+ (requires standard library typing annotations `Dict`, `List`, `Tuple`, `Any`, `Optional` and `dataclasses`).
- Virtual environment recommended (`venv` or `conda`).
- Shell / Terminal to execute `streamlit run cascadebreak-mini/app.py`.

**Production:**
- Streamlit Community Cloud, Hugging Face Spaces, or Dockerized Linux container (Ubuntu with Python 3.12).
- Memory footprint: ~150MB - 300MB RAM for synthetic network graphs.

---

*Stack analysis: 2026-09-13*
