# Coding Conventions

**Analysis Date:** 2026-09-13

## Naming Patterns

**Files:**
- Snake case for all Python modules: `cascade_engine.py`, `intervention_engine.py`, `visualization.py`.
- Lowercase with dots for configuration files: `config.toml`, `requirements.txt`.
- Uppercase for project artifacts and markdown specs: `README.md`, `PROJECT.md`.

**Classes:**
- PascalCase for all class definitions:
  - `CascadeEngine` (`cascadebreak-mini/cascade_engine.py:27`)
  - `InterventionEngine` (`cascadebreak-mini/intervention_engine.py:29`)
  - `RoadFeatureVector` (`cascadebreak-mini/ml_prediction_interface.py:29`)
  - `MLPredictionOutput` (`cascadebreak-mini/ml_prediction_interface.py:43`)
  - `RoadFailurePredictorInterface` (`cascadebreak-mini/ml_prediction_interface.py:52`)

**Functions and Methods:**
- Snake case for top-level functions and class methods:
  - `get_synthetic_city_nodes()` (`cascadebreak-mini/scenario.py:18`)
  - `get_synthetic_city_roads()` (`cascadebreak-mini/scenario.py:152`)
  - `evaluate_network_state()` (`cascadebreak-mini/cascade_engine.py:104`)
  - `simulate_candidate()` (`cascadebreak-mini/intervention_engine.py:132`)
  - `evaluate_all_interventions()` (`cascadebreak-mini/intervention_engine.py:159`)
  - `create_network_map()` (`cascadebreak-mini/visualization.py:16`)
- Private helper methods prefixed with single underscore:
  - `_build_graph()` (`cascadebreak-mini/cascade_engine.py:50`)

**Variables:**
- Snake case for local variables and object attributes: `flooded_roads`, `delta_pop`, `sim_metrics`, `total_city_population`.
- Node identifiers use alphanumeric codes: `N1` to `N11` (e.g., `N6` for hospital, `N7` for relief).
- Road identifiers use alphanumeric codes: `R1` to `R16`.
- Temporary intervention link IDs use uppercase prefix: `TEMP_N4_N6`, `RESTORE_R5`, `COMBINED_R5_R6`.

**Types:**
- Python standard `typing` module type hints throughout method signatures:
  - `Dict[str, Dict[str, Any]]`
  - `List[Dict[str, Any]]`
  - `Tuple[nx.Graph, Dict[str, Any]]`
  - `Optional[Dict[str, Any]]`
  - `pd.DataFrame`

## Code Style

**Formatting:**
- Standard PEP 8 with 4-space indentation.
- Double quotes preferred for strings and docstrings.
- UTF-8 file encoding enforced.

**Linting:**
- No linter (Flake8, Ruff, or Black) configuration file currently committed. Code follows PEP 8 conventions generally, though recent UI styling edits introduced syntax issues in `app.py` and `visualization.py`.

## Import Organization

**Order:**
1. Standard library imports (`copy`, `typing`, `io`, `sys`, `dataclasses`)
2. Third-party library imports (`networkx`, `pandas`, `folium`, `streamlit`)
3. Local application modules (`scenario`, `cascade_engine`, `intervention_engine`, `visualization`)

**Pattern observed in `cascadebreak-mini/intervention_engine.py:21-26`:**
```python
import copy
from typing import Dict, List, Tuple, Any, Optional
import pandas as pd
import networkx as nx

from cascade_engine import CascadeEngine
```

**Path Aliases:**
- No path aliases used; local modules are imported directly assuming execution from within `cascadebreak-mini/` or with `cascadebreak-mini` on `PYTHONPATH`.

## Error Handling

**Patterns:**
- Safe dictionary access with defaults: `attr.get("type") == "hospital"` or `r.get("is_flooded", False)`.
- Defensive division-by-zero protection:
  ```python
  effort_safe = max(effort, 0.1)
  utility = total_benefit / effort_safe
  ```
- Graceful empty scenario handling: In `InterventionEngine.get_dynamic_recommendation()`, when all interventions yield zero improvement (e.g., Scenario 4), the engine returns a clean structured fallback dictionary rather than throwing an exception:
  ```python
  if top["utility"] <= 0 or (top["delta_population"] == 0 and top["delta_hospital"] == 0 and top["delta_relief"] == 0):
      return {
          "has_beneficial_intervention": False,
          "title": "NO BENEFICIAL INTERVENTION IDENTIFIED",
          "message": "...",
          "ranking_df": ranking_df,
      }
  ```
- Unimplemented interfaces raise `NotImplementedError` with descriptive migration messages (`cascadebreak-mini/ml_prediction_interface.py:65`).

## Logging

**Framework:**
- `print()` statements used for test suite progress reporting in `cascadebreak-mini/test_cascadebreak.py`.
- No structured Python `logging` logger in core engine modules; engine returns structured dictionary outputs to the caller.

## Comments & Documentation

**When to Comment:**
- Header docstrings on every module explaining the domain concept, mathematical formulas, and operational boundary.
- ASCII art workflow diagrams in file headers:
  - Cascade chain in `cascadebreak-mini/cascade_engine.py:7-15`
  - ML covariate dataflow in `cascadebreak-mini/ml_prediction_interface.py:12-16`

**Docstring Format:**
- Triple double-quote `"""` Google/Numpy style docstrings describing class purpose, argument types, and mathematical objective functions:
  ```python
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
  ```

## Function & Class Design

**Size:**
- Modular functions focused on single responsibilities. Engine methods generally range from 15 to 40 lines.

**Parameters:**
- Explicit keyword arguments with demonstration default weights: `wp=0.5, wh=0.3, wr=0.2`.
- Avoids mutable default arguments (uses `None` with `custom_roads if custom_roads is not None else self.roads`).

**Return Values:**
- Structured typed objects: `Dict[str, Any]`, `pd.DataFrame`, `Tuple[nx.Graph, Dict[str, Any]]`.
- Dictionaries contain explicit metric keys with units (e.g., `length_km`, `effort_cost`, `total_distance_km`).

## Immutability Design Pattern

**Graph Immutability:**
- Core rule: Never mutate the baseline network graph during counterfactual exploration.
- Implemented via `copy.deepcopy(self.roads)` and isolated graph instantiation in `InterventionEngine.simulate_candidate()`:
  ```python
  sim_roads = copy.deepcopy(self.roads)
  for r in sim_roads:
      if r["road_id"] in target_roads_set:
          r["is_flooded"] = False
          r["is_accessible"] = True
  ```

---

*Convention analysis: 2026-09-13*
