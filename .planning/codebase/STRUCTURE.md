# Codebase Structure

**Analysis Date:** 2026-09-13

## Directory Layout

```text
CascadeBreakAI/
├── .planning/                              # GSD project memory and planning artifacts
│   └── codebase/                           # Codebase map reference documents
│       ├── STACK.md                        # Technology stack and dependencies
│       ├── INTEGRATIONS.md                 # External APIs and data sources
│       ├── ARCHITECTURE.md                 # System architecture and data flow
│       ├── STRUCTURE.md                    # Directory organization and locations
│       ├── CONVENTIONS.md                  # Code style and design patterns
│       ├── TESTING.md                      # Test setup, patterns, and runner
│       └── CONCERNS.md                     # Technical debt and bug registry
├── cascadebreak-mini/                      # Main decision-support prototype directory
│   ├── .streamlit/                         # Streamlit framework configuration
│   │   └── config.toml                     # Dark tactical theme and server configuration
│   ├── __pycache__/                        # Compiled Python bytecode cache
│   ├── app.py                              # Streamlit 10-section decision-support dashboard
│   ├── cascade_engine.py                   # NetworkX topological cascade simulation engine
│   ├── intervention_engine.py              # Counterfactual intervention optimizer
│   ├── scenario.py                         # City graph data & flood scenario definitions
│   ├── visualization.py                    # Folium interactive geospatial map renderer
│   ├── ml_prediction_interface.py          # Stage 2 ML failure prediction contracts
│   ├── test_cascadebreak.py                # Automated integrity test suite
│   ├── requirements.txt                    # Virtual environment dependencies
│   └── README.md                           # System documentation and math specifications
├── CascadeBreakAIfinal.pptx                # Project presentation slide deck (10 MB)
└── CascadeBreak_AI_Project_Brief.docx      # Executive project brief document (17 KB)
```

## Directory Purposes

**`cascadebreak-mini/`:**
- Purpose: Contains all active executable source code, configuration, testing, and documentation for the decision-support prototype.
- Contains: Python modules (`*.py`), config files (`config.toml`), dependencies (`requirements.txt`), and documentation (`README.md`).
- Key files: `cascadebreak-mini/app.py`, `cascadebreak-mini/cascade_engine.py`, `cascadebreak-mini/intervention_engine.py`.

**`cascadebreak-mini/.streamlit/`:**
- Purpose: Streamlit application configuration directory.
- Contains: `config.toml`.
- Key files: `cascadebreak-mini/.streamlit/config.toml` (defines `#22D3EE` cyan theme and `#0B1220` dark background).

**`cascadebreak-mini/__pycache__/`:**
- Purpose: Auto-generated CPython bytecode cache.
- Contains: `*.cpython-312.pyc`, `*.cpython-314.pyc`.
- Key files: Compiled modules for rapid Python startup.

**`.planning/`:**
- Purpose: Get Shit Done (GSD) project planning, memory, and codebase documentation.
- Contains: Codebase maps (`codebase/*.md`), future project states (`STATE.md`, `ROADMAP.md`).
- Key files: `.planning/codebase/*.md`.

## Key File Locations

**Entry Points:**
- `cascadebreak-mini/app.py`: Streamlit web dashboard entry point launched via `streamlit run app.py`.
- `cascadebreak-mini/test_cascadebreak.py`: Standalone test suite runner launched via `python test_cascadebreak.py`.

**Configuration:**
- `cascadebreak-mini/requirements.txt`: Python package dependency list.
- `cascadebreak-mini/.streamlit/config.toml`: Theme, server, and networking settings.

**Core Logic & Engines:**
- `cascadebreak-mini/cascade_engine.py`: Core `CascadeEngine` class managing topological network graph models and reachability algorithms.
- `cascadebreak-mini/intervention_engine.py`: Core `InterventionEngine` simulating counterfactual options and computing utility.
- `cascadebreak-mini/scenario.py`: Parametric definitions of synthetic nodes, roads, and flood profiles.
- `cascadebreak-mini/visualization.py`: Geospatial map generator using Folium and Leaflet.
- `cascadebreak-mini/ml_prediction_interface.py`: Future Stage 2 ML schemas (`RoadFeatureVector`, `MLPredictionOutput`, `RoadFailurePredictorInterface`).

**Testing:**
- `cascadebreak-mini/test_cascadebreak.py`: Complete unit tests verifying population integrity, scenario outcomes, and graph immutability.

## Naming Conventions

**Files:**
- Snake case for all Python modules: `cascade_engine.py`, `intervention_engine.py`, `test_cascadebreak.py`.
- Lowercase for configuration files: `config.toml`, `requirements.txt`.
- Uppercase for project artifacts and markdown docs: `README.md`, `STACK.md`, `ARCHITECTURE.md`.

**Directories:**
- Hyphenated lowercase: `cascadebreak-mini/`.
- Dotted prefixes for tooling configuration: `.streamlit/`, `.planning/`.

**Classes:**
- PascalCase: `CascadeEngine`, `InterventionEngine`, `RoadFeatureVector`, `MLPredictionOutput`, `RoadFailurePredictorInterface`.

**Functions and Methods:**
- Snake case: `get_synthetic_city_nodes()`, `get_synthetic_city_roads()`, `evaluate_network_state()`, `simulate_candidate()`, `evaluate_all_interventions()`, `create_network_map()`.

## Where to Add New Code

**New Flood Scenario:**
- Primary code: Append new scenario profile to `scenario_profiles` dictionary in `cascadebreak-mini/scenario.py:163`. Add scenario name to `get_available_scenarios()` and description to `get_scenario_metadata()` in `cascadebreak-mini/scenario.py:225-260`.
- Tests: Add scenario validation function in `cascadebreak-mini/test_cascadebreak.py`.

**New Intervention Type (e.g., Drone Relay, Ferry Crossing):**
- Primary code: Add candidate generator logic in `InterventionEngine.get_candidate_interventions()` (`cascadebreak-mini/intervention_engine.py:40`).
- Simulation handling: Update `InterventionEngine.simulate_candidate()` to apply new intervention mechanics (`cascadebreak-mini/intervention_engine.py:132`).
- Visualization: Add marker/polyline rendering styles in `cascadebreak-mini/visualization.py`.

**New Critical Facility Type (e.g., Fire Stations, Water Treatment Plants):**
- Primary code: Update node definitions in `cascadebreak-mini/scenario.py:get_synthetic_city_nodes()`.
- Engine: Add node set classification and reachability loop in `CascadeEngine.__init__()` and `evaluate_network_state()` in `cascadebreak-mini/cascade_engine.py`.
- UI: Update facility impact cards in `cascadebreak-mini/app.py`.

**Machine Learning Road Disruption Models (Stage 2):**
- Implementation: Implement subclass inheriting from `RoadFailurePredictorInterface` in `cascadebreak-mini/ml_prediction_interface.py`.
- Training pipeline: Place model training scripts in a new `training/` or `models/` directory under `cascadebreak-mini/`.

## Special Directories

**`cascadebreak-mini/__pycache__/`:**
- Purpose: Stores compiled bytecode files generated by the Python interpreter.
- Generated: Yes.
- Committed: Should NOT be committed (should be added to `.gitignore`).

**`.planning/`:**
- Purpose: Project roadmap, memory, and codebase mapping artifacts for GSD.
- Generated: Mixed (maintained by agents and developer).
- Committed: Yes, tracked in git unless local-only planning is explicitly configured.

---

*Structure analysis: 2026-09-13*
