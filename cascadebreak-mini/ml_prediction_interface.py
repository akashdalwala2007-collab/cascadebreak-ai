"""
CascadeBreak AI - Machine Learning Road Failure Prediction Interface (Future Architecture)
========================================================================================
Architecture specification for Stage 2 integration of probabilistic road failure
prediction models (e.g., Random Forest, XGBoost, Graph Neural Networks).

Concept:
  In the full-scale CascadeBreak AI platform, road disruption states are NOT binary
  guesses. Instead, multi-source environmental and hydrological covariates feed into
  a predictive ML model to output failure probabilities P(Failure | X):

  [ NASA GPM Rainfall (mm/hr) ] ──┐
  [ Copernicus DEM Slope (deg)  ] ──┼──> [ ML Classifier / GNN ] ──> P(Road Failure) ──> [ Cascade Disruption Engine ]
  [ Copernicus DEM Elevation(m) ] ──┤     (Random Forest / XGBoost)
  [ Soil Moisture Index (SMAP)  ] ──┤
  [ Road Class & Pavement Type  ] ──┘

Note:
  This module defines the strict data schemas, interfaces, and validation contracts
  for future production models. The current MVP operates deterministically without
  requiring active ML weights.
"""

import math
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


def _is_finite_numeric(val: Any) -> bool:
    """
    Checks that val is a real numeric int or float, strictly not a bool, and finite
    (not NaN, not +inf, not -inf).
    """
    if isinstance(val, bool):
        return False
    if not isinstance(val, (int, float)):
        return False
    return math.isfinite(val)


@dataclass
class RoadFeatureVector:
    """Input features required for predictive road failure classification."""
    road_id: str
    length_km: float
    road_class: str                 # 'motorway', 'primary', 'secondary', 'bridge'
    elevation_m: float              # Copernicus DEM GLO-30
    slope_degrees: float            # Terrain slope from DEM
    soil_saturation_pct: float      # Soil moisture saturation percentage
    accumulated_rainfall_mm: float  # NASA GPM IMERG 6-hour rainfall accumulation
    river_proximity_m: float        # Distance to nearest natural river channel
    bridge_structure: bool          # Whether segment contains elevated bridge spans

    VALID_ROAD_CLASSES = {"motorway", "primary", "secondary", "bridge"}

    def __post_init__(self):
        if not isinstance(self.road_id, str) or not self.road_id.strip():
            raise ValueError(f"road_id must be a non-empty string, got {self.road_id!r}")
        if not _is_finite_numeric(self.length_km) or self.length_km <= 0.0:
            raise ValueError(f"length_km must be a finite positive number (non-bool), got {self.length_km!r}")
        if self.road_class not in self.VALID_ROAD_CLASSES:
            raise ValueError(
                f"road_class must be one of {sorted(self.VALID_ROAD_CLASSES)}, got {self.road_class!r}"
            )
        if not _is_finite_numeric(self.elevation_m):
            raise ValueError(f"elevation_m must be a finite numeric value (non-bool), got {self.elevation_m!r}")
        if not _is_finite_numeric(self.slope_degrees) or not (0.0 <= self.slope_degrees <= 90.0):
            raise ValueError(f"slope_degrees must be a finite number in range [0.0, 90.0] (non-bool), got {self.slope_degrees!r}")
        if not _is_finite_numeric(self.soil_saturation_pct) or not (0.0 <= self.soil_saturation_pct <= 100.0):
            raise ValueError(f"soil_saturation_pct must be a finite number in range [0.0, 100.0] (non-bool), got {self.soil_saturation_pct!r}")
        if not _is_finite_numeric(self.accumulated_rainfall_mm) or self.accumulated_rainfall_mm < 0.0:
            raise ValueError(f"accumulated_rainfall_mm must be a finite non-negative number (non-bool), got {self.accumulated_rainfall_mm!r}")
        if not _is_finite_numeric(self.river_proximity_m) or self.river_proximity_m < 0.0:
            raise ValueError(f"river_proximity_m must be a finite non-negative number (non-bool), got {self.river_proximity_m!r}")
        if not isinstance(self.bridge_structure, bool):
            raise ValueError(f"bridge_structure must be a boolean, got {self.bridge_structure!r}")


@dataclass
class MLPredictionOutput:
    """Output probability distribution for road disruption risk."""
    road_id: str
    failure_probability: float      # P(failure) in [0.0, 1.0]
    predicted_status: str           # 'passable', 'restricted', 'submerged'
    confidence_score: float         # Model uncertainty estimate
    key_risk_factor: str            # Explanatory feature (e.g., 'Excess rainfall on low elevation')

    VALID_STATUSES = {"passable", "restricted", "submerged"}

    def __post_init__(self):
        if not isinstance(self.road_id, str) or not self.road_id.strip():
            raise ValueError(f"road_id must be a non-empty string, got {self.road_id!r}")
        if not _is_finite_numeric(self.failure_probability) or not (0.0 <= self.failure_probability <= 1.0):
            raise ValueError(
                f"failure_probability must be a finite float in [0.0, 1.0] (non-bool), got {self.failure_probability!r}"
            )
        if self.predicted_status not in self.VALID_STATUSES:
            raise ValueError(
                f"predicted_status must be one of {sorted(self.VALID_STATUSES)}, got {self.predicted_status!r}"
            )
        if not _is_finite_numeric(self.confidence_score) or not (0.0 <= self.confidence_score <= 1.0):
            raise ValueError(
                f"confidence_score must be a finite float in [0.0, 1.0] (non-bool), got {self.confidence_score!r}"
            )
        if not isinstance(self.key_risk_factor, str):
            raise ValueError(f"key_risk_factor must be a string, got {self.key_risk_factor!r}")


class RoadFailurePredictorInterface:
    """
    Abstract interface for future trained ML disruption models (Random Forest / XGBoost).
    """

    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path
        self.is_trained = False

    def predict_disruptions(self, features: List[RoadFeatureVector]) -> List[MLPredictionOutput]:
        """
        Takes real-time remote sensing covariate features and outputs failure probabilities.
        """
        raise NotImplementedError(
            "RoadFailurePredictorInterface is an architectural placeholder for Stage 2. "
            "The V2 prototype currently operates with deterministic disaster scenarios."
        )

    def explain_prediction(self, road_id: str) -> Dict[str, float]:
        """
        Returns SHAP feature importances for individual road failure predictions.
        """
        raise NotImplementedError("SHAP explainability interface will be activated in Stage 2.")

