<!-- refreshed: 2026-09-13 -->
# Architecture

**Analysis Date:** 2026-09-13

## System Overview

```text
┌────────────────────────────────────────────────────────────────────────┐
│                   STREAMLIT WEB DASHBOARD (UI LAYER)                   │
│                       `cascadebreak-mini/app.py`                       │
│    (10 Decision Sections, KPI Cards, Simulation Lab, Explainability)   │
└───────────────────┬────────────────────────────────┬───────────────────┘
                    │                                │
                    ▼                                ▼
┌──────────────────────────────────────┐  ┌──────────────────────────────┐
│       COUNTERFACTUAL SIMULATOR       │  │     GEOSPATIAL RENDERER      │
│ `cascadebreak-mini/intervention_     │  │ `cascadebreak-mini/visual-   │
│               engine.py`             │  │          ization.py`         │
│  - Candidate Generator               │  │  - Interactive Folium Maps   │
│  - Utility Maximizer                 │  │  - CartoDB Dark Matter       │
│  - Heuristic Baselines Comparator    │  │  - HUD Facility & Route Pins │
└───────────────────┬──────────────────┘  └──────────────┬───────────────┘
                    │                                    │
                    ▼                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   TOPOLOGICAL CASCADE GRAPH ENGINE                     │
│                    `cascadebreak-mini/cascade_engine.py`               │
│  - NetworkX Graph Construction (Immutable Baseline vs Cloned Scenarios) │
│  - Connected Component & Shortest Path (Dijkstra) Analyzers            │
│  - Facility Reachability (Trauma Hospital N6 & Relief Logistics N7)    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                    SYNTHETIC CITY & SCENARIOS (DATA)                   │
│                      `cascadebreak-mini/scenario.py`                   │
│  - 11 City Nodes (59,000 Population, Hospitals, Relief, Junctions)     │
│  - 16 Parametric Road Corridors (Length, Terrain, Damage Multiplier)   │
│  - 4 Deterministic Climate Disaster Scenarios                          │
└────────────────────────────────────────────────────────────────────────┘
```

## Component Responsibilities

| Component | Responsibility | File |
|-----------|----------------|------|
| **Streamlit Dashboard** | Orchestrates 10 UI sections, renders KPI metrics, manages scenario controls, runs simulation sliders, displays rankings and explainability | `cascadebreak-mini/app.py` |
| **Cascade Engine** | Builds NetworkX graphs, measures component fragmentation, evaluates node reachability to hospital and relief centers, finds detour paths | `cascadebreak-mini/cascade_engine.py` |
| **Intervention Engine** | Generates multi-modal candidates (Restoration, Temporary Bridge, Combined), runs counterfactual simulations non-destructively, calculates utility scores, formulates dynamic explanations | `cascadebreak-mini/intervention_engine.py` |
| **Synthetic Scenario Model** | Supplies deterministic definitions of 11 city nodes, 16 road edges, and 4 flood scenarios with damage multipliers | `cascadebreak-mini/scenario.py` |
| **Geospatial Visualizer** | Constructs interactive Folium maps with custom CSS/DivIcon markers, dashed flood lines, cyan restoration routes, and facility popups | `cascadebreak-mini/visualization.py` |
| **ML Prediction Contract** | Defines dataclasses and abstract interface for future Stage 2 continuous flood failure probability estimation | `cascadebreak-mini/ml_prediction_interface.py` |
| **Automated Test Suite** | Asserts population integrity, cascade mechanics, counterfactual immutability, ranking correctness, and fallback edge cases | `cascadebreak-mini/test_cascadebreak.py` |

## Pattern Overview

**Overall:** Decoupled Layered Architecture with Non-Destructive Counterfactual Graph Simulation.

**Key Characteristics:**
- **Strict Baseline Immutability:** Baseline flooded networks are never mutated in place. Candidate interventions are simulated by deep-copying road catalogs and re-evaluating isolated cloned graphs (`CascadeEngine._build_graph`).
- **Deterministic Scenario Injection:** Scenarios are parameter-driven catalogs enabling reproducible benchmarking of decision algorithms.
- **Dynamic Evidence-Based Explainability:** AI recommendations generate justification text dynamically from actual graph accessibility numbers (`delta_population`, `delta_hospital`, `delta_relief`, `effort_cost`), avoiding hallucinated or static text.

## Layers

**Presentation Layer:**
- Purpose: User-facing decision-support console for emergency responders.
- Location: `cascadebreak-mini/app.py`
- Contains: Streamlit widgets, layout columns, custom CSS styling, Folium map embeds, tabbed interface panels.
- Depends on: `cascade_engine.py`, `intervention_engine.py`, `scenario.py`, `visualization.py`.
- Used by: End user / responder commander in web browser.

**Decision & Optimization Layer:**
- Purpose: Evaluates potential human interventions, balances logistical cost vs humanitarian gain.
- Location: `cascadebreak-mini/intervention_engine.py`
- Contains: `InterventionEngine`, utility objective formula, heuristic baseline models (Damage-First, Pop-Exposure-First).
- Depends on: `cascade_engine.py`, `pandas`, `networkx`.
- Used by: `app.py`.

**Topological Network Layer:**
- Purpose: Pure graph mechanics and topological accessibility quantification.
- Location: `cascadebreak-mini/cascade_engine.py`
- Contains: `CascadeEngine`, NetworkX wrappers, Dijkstra shortest paths, connected component counters.
- Depends on: `networkx`.
- Used by: `intervention_engine.py`, `app.py`.

**Data / Scenario Layer:**
- Purpose: Ground-truth geometry, node attributes, road lengths, and flood event definitions.
- Location: `cascadebreak-mini/scenario.py`
- Contains: `get_synthetic_city_nodes()`, `get_synthetic_city_roads()`, `get_available_scenarios()`, `get_scenario_metadata()`.
- Depends on: Standard library.
- Used by: `cascade_engine.py`, `intervention_engine.py`, `app.py`, `test_cascadebreak.py`.

## Data Flow

### Primary Request Path (Scenario Selection to AI Recommendation)

1. User selects a disaster scenario from the sidebar in `cascadebreak-mini/app.py:488`
2. `scenario.py:get_synthetic_city_roads` generates road catalog with damage states for the scenario (`cascadebreak-mini/scenario.py:152`)
3. `CascadeEngine.__init__` constructs pre-flood and baseline flooded `networkx.Graph` instances (`cascadebreak-mini/cascade_engine.py:33`)
4. `CascadeEngine.evaluate_network_state` calculates baseline isolation and reachability matrices (`cascadebreak-mini/cascade_engine.py:104`)
5. `InterventionEngine.evaluate_all_interventions` clones graph per candidate, calculates accessibility deltas, and computes utility (`cascadebreak-mini/intervention_engine.py:160`)
6. `InterventionEngine.get_dynamic_recommendation` selects highest utility candidate and formulates natural-language explanation (`cascadebreak-mini/intervention_engine.py:217`)
7. `app.py` displays priority action card, ranking table, side-by-side Folium maps, and heuristic comparisons (`cascadebreak-mini/app.py:700-1100`)

### Secondary Flow (Interactive Counterfactual Simulation Lab)

1. User selects an individual candidate intervention or adjusts slider weights in UI (`cascadebreak-mini/app.py:650`)
2. `InterventionEngine.simulate_candidate` builds hypothetical graph with custom road attributes or temporary links (`cascadebreak-mini/intervention_engine.py:132`)
3. Resulting accessibility metrics are compared against baseline flooded metrics
4. Dynamic Folium map renders hypothetical topology highlighting restored routes in cyan (`cascadebreak-mini/visualization.py:16`)

**State Management:**
- Stateless execution per Streamlit script run. Streamlit triggers a top-to-bottom re-run on user input change, passing selected scenario state down the engine pipeline.

## Key Abstractions

**Cascade Engine (`CascadeEngine`):**
- Purpose: Encapsulates urban road network topology and evaluates service reachability for population nodes.
- Examples: `cascadebreak-mini/cascade_engine.py:27`
- Pattern: Domain service / Facade over NetworkX.

**Intervention Engine (`InterventionEngine`):**
- Purpose: Coordinates multi-modal candidate generation, non-destructive counterfactual execution, and utility optimization.
- Examples: `cascadebreak-mini/intervention_engine.py:29`
- Pattern: Strategy & Optimization engine.

**Road Feature Vector (`RoadFeatureVector`):**
- Purpose: Strict schema specification for remote sensing environmental covariates for machine learning.
- Examples: `cascadebreak-mini/ml_prediction_interface.py:28`
- Pattern: Data Transfer Object (DTO) / Dataclass.

## Entry Points

**Web Dashboard:**
- Location: `cascadebreak-mini/app.py`
- Triggers: `streamlit run cascadebreak-mini/app.py`
- Responsibilities: Renders complete UI, captures user interactions, coordinates simulation and visualization calls.

**Automated Test Suite:**
- Location: `cascadebreak-mini/test_cascadebreak.py`
- Triggers: `python cascadebreak-mini/test_cascadebreak.py`
- Responsibilities: Executes 6 automated integrity tests across all 4 scenarios.

## Architectural Constraints

- **Threading:** Single-threaded execution per Streamlit session. NetworkX calculations run synchronously in Python process.
- **Global state:** No shared mutable global state; all simulation state is scoped within class instances initialized per run.
- **Circular imports:** Clean DAG dependency structure (`scenario` -> `cascade_engine` -> `intervention_engine` -> `app.py`). No circular dependencies exist.
- **Graph Topology:** Undirected graph (`nx.Graph`). All roads are modeled as bidirectional for the synthetic prototype.

## Anti-Patterns

### Inline CSS String Concatenation & Incomplete Dark Mode Refactor

**What happens:** Extensive raw HTML/CSS strings (>200 lines) are embedded in `cascadebreak-mini/app.py` and `cascadebreak-mini/visualization.py`. A recent attempt to update dark mode styles caused syntax errors (e.g., unmatched triple quotes at `cascadebreak-mini/app.py:529-536` and unclosed parens at `cascadebreak-mini/visualization.py:244`).
**Why it's wrong:** Breaks Python compilation, inhibits linting, tightly couples styling with business logic, and makes UI maintenance error-prone.
**Do this instead:** Store CSS in a standalone `assets/style.css` file loaded via `st.markdown(open("style.css").read(), unsafe_allow_html=True)` and validate syntax with automated linting.

### Repetitive Network Recalculations

**What happens:** When `InterventionEngine.evaluate_all_interventions()` runs, it calls `simulate_candidate` for every candidate, which re-runs Dijkstra shortest path for all population nodes (`O(P * (H + R))`) without caching paths that could not be affected by the intervention.
**Why it's wrong:** Fine for 11 nodes, but does not scale to OpenStreetMap city networks with >10,000 edges.
**Do this instead:** Use graph subgraph diffing or incremental shortest path recalculation.

## Error Handling

**Strategy:**
- Guard conditions with clean fallbacks for edge cases (e.g., Scenario 4 with zero disruptions outputs a clear `NO BENEFICIAL INTERVENTION IDENTIFIED` notice instead of an uncaught exception).
- Safe division protections: `max(Effort, 0.1)` in utility calculations prevents zero-division errors.

## Cross-Cutting Concerns

**Logging:** Standard Python stdout/stderr. No structured logger (`logging` module) currently implemented.
**Validation:** `assert` statements in `test_cascadebreak.py` validate total population (59,000) and scenario metrics.
**Security:** No external data ingestion or SQL/command injection vulnerabilities in synthetic prototype.

---

*Architecture analysis: 2026-09-13*
