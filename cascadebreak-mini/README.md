# CascadeBreak AI — V2 Decision-Support Prototype

> **“Don’t just map the flood. Find the intervention that breaks the cascade.”**
>
> *Where should responders act first to reduce the greatest downstream disruption with limited intervention effort?*

---

> **IMPORTANT DISCLAIMER:**
> *This prototype is an educational decision-support proof-of-concept using deterministic synthetic disaster scenarios to demonstrate the CascadeBreak AI decision-support workflow. It is NOT an autonomous disaster-command system, rescue dispatcher, or physical road repair tool. Real satellite (Sentinel-1 SAR), terrain (Copernicus DEM), road network (OpenStreetMap), and population (WorldPop) datasets are planned for the next development stage.*

---

## 1. What Is CascadeBreak AI?
**CascadeBreak AI** is an emergency-response decision-support intelligence platform. Traditional disaster GIS platforms typically focus on **damage mapping** (e.g., overlaying flooded zones on road maps). 

However, passively mapping water extent does not answer the commander's critical question: **“Where should responders deploy limited clearing and bridge resources first to restore the maximum downstream access?”**

CascadeBreak AI models flood disruptions as dynamic **topological cascades** across critical urban networks. By treating the city as an interconnected graph of roads, trauma hospitals, relief logistics centers, and residential clusters, the platform simulates counterfactual response interventions (*“What happens if we restore Road A versus Road B versus deploying a Temporary Pontoon Bridge?”*) and optimizes response actions for maximum humanitarian benefit per unit of intervention effort.

---

## 2. The Problem
During severe climate disasters (floods, hurricanes, storm surges):
1. **Network Disconnections Multiply:** A single flooded bridgehead or arterial road can isolate tens of thousands of residents from emergency healthcare and food supplies.
2. **Resource Scarcity:** Emergency engineering and disaster management crews have finite resources (bulldozers, pumps, Bailey bridges, rescue teams).
3. **Flawed Heuristics:** Traditional response approaches often prioritize the **most heavily damaged road** (which may be a non-critical peripheral route) or the **nearest road** (which may lead to a dead-end).
4. **Cascade Ignorance:** Simple proximity-based decisions fail to account for systemic network bottlenecks and downstream accessibility cascades.

---

## 3. Core Decision Workflow
The end-to-end decision-support pipeline operates as follows:

$$\text{Flood Hazard} \longrightarrow \text{Road Disruption} \longrightarrow \text{Network Cascade} \longrightarrow \text{Counterfactual Simulation} \longrightarrow \text{Utility Optimization} \longrightarrow \text{Actionable AI Recommendation}$$

---

## 4. The Cascade Definition
In CascadeBreak AI, a **cascade** is defined as a sequence of failure dependencies:

$$\text{Flooded / Blocked Road Edge} \longrightarrow \text{Network Graph Fragmentation} \longrightarrow \text{Critical Facility Inaccessibility} \longrightarrow \text{Population Cluster Isolation}$$

The system evaluates:
- Number of isolated graph components.
- Population cut off from Level-1 Trauma Hospital (`N6`).
- Population cut off from Central Disaster Relief Hub (`N7`).
- Population suffering total dual-critical service isolation.
- Detour path increases across surviving open corridors.

---

## 5. Counterfactual Simulation Engine
For every candidate response action $i$:
1. **Immutable Baseline:** Starts from the identical baseline flooded network without modifying the permanent state.
2. **Hypothetical Intervention:** Applies candidate action $i$ (restoring an edge, adding a temporary link, or executing a combined package).
3. **Graph Recalculation:** Recomputes all shortest paths, reachability matrices, and connected components.
4. **Access Delta Calculation:** Measures $\Delta\text{PopulationAccess}(i)$, $\Delta\text{HospitalAccess}(i)$, and $\Delta\text{ReliefAccess}(i)$.
5. **Effort Index Evaluation:** Computes required logistical effort.
6. **Utility Maximization:** Calculates the benefit-to-effort ratio.

---

## 6. Multi-Modal Intervention Types
CascadeBreak AI (V2) evaluates four candidate intervention modalities:

1. **Road Restoration:**
   - Clearing debris, pumping flood water, or executing emergency repairs on an existing flooded road segment (e.g., `Restore R5`).
2. **Traffic Rerouting:**
   - Identifying and validating viable surviving detour routes through open network corridors without physical construction.
3. **Temporary Access Deployment:**
   - Simulating the rapid installation of temporary tactical bridges, pontoons, or culvert crossings across severed corridors (e.g., `Deploy Emergency River Pontoon N4 to N6`).
4. **Combined Interventions:**
   - Evaluating curated packages of complementary dual-corridor restorations (e.g., `Dual Restore R5 + R6`).

---

## 7. Intervention Effort Index & Optimization Equation

### Intervention Effort Index
To model operational deployment difficulty realistically without pretending to compute exact currency costs, the synthetic MVP computes:

$$\text{Intervention Effort Index} = \text{Length}_{\text{km}} \times \text{Terrain Factor} \times \text{Damage Factor}$$

- **Terrain Factor:** $1.0$ (flat urban), $1.3$–$1.5$ (riverside, bridgeheads, mountain passes).
- **Damage Factor:** $1.0$ (minor wash), $1.5$–$2.5$ (severe submersion, embankment collapse).

### Objective Function (Utility)
$$\text{Utility}(i) = \frac{w_p \cdot \Delta\text{PopulationAccess}(i) + w_h \cdot \Delta\text{HospitalAccess}(i) + w_r \cdot \Delta\text{ReliefAccess}(i)}{\max(\text{Effort}(i), 0.1)}$$

- $w_p = 0.5$ (Demonstration weight for total population gaining dual critical access)
- $w_h = 0.3$ (Demonstration weight for trauma hospital access)
- $w_r = 0.2$ (Demonstration weight for relief shelter access)

> *Division-by-zero protection is strictly enforced with $\max(\text{Effort}, 0.1)$.*

---

## 8. Current MVP Scope & Features
- **10 Structured Sections in Streamlit Dashboard:**
  1. Flood Scenario Overview (Disruption KPIs & cluster breakdown).
  2. Current Network & Cascade (Folium map & cascade progression tracker).
  3. Candidate Interventions (Multi-modal action inventory).
  4. Counterfactual Simulation Lab (Interactive single-candidate & rerouting tester).
  5. Intervention Ranking Table (Dynamic sorting by Utility).
  6. Actionable AI Recommendation (Calculated winner with zero-benefit fallback).
  7. Before $\to$ After Visual Impact (Side-by-side comparative Folium maps).
  8. Explainability Panel ("Why did CascadeBreak choose this?").
  9. Baseline Heuristic Comparison (Damage First vs Pop Exposure First vs CascadeBreak AI).
  10. Prototype Scope, Reliability & Limitations.

---

## 9. Synthetic Data Explanation
- **Nodes (11 Total, 59,000 Total Population):**
  - `N1`: North Suburb (12,000 residents)
  - `N2`: North-East District (15,000 residents)
  - `N3`: West Hills (8,000 residents)
  - `N8`: East Industrial Zone (10,000 residents)
  - `N9`: South Riverside (14,000 residents)
  - `N6`: City General Hospital (Level-1 trauma center, 600 beds)
  - `N7`: Central Disaster Relief Centre (3,000 evacuee logistics capacity)
  - `N4`, `N5`, `N10`, `N11`: Strategic junctions & bridgeheads.
- **Roads (16 Total):** Parameterized by physical length, terrain difficulty, damage multiplier, and effort index.
- **Deterministic Scenarios:**
  - `Scenario 1: Urban Flood — Distributed Road Failures`
  - `Scenario 2: Critical Corridor Disruption` *(Demonstrates MOST DAMAGED ROAD != MOST VALUABLE INTERVENTION)*
  - `Scenario 3: Multi-Route Bottleneck` *(Demonstrates Temporary Bridges & Combined Packages)*
  - `Scenario 4: Baseline Clear (No Inundation / Zero Disruption)` *(Demonstrates NO BENEFICIAL INTERVENTION IDENTIFIED fallback)*

---

## 10. System Boundaries & Limitations
- **Human Decision-Maker:** The tool assists and informs responders; human commanders make final operational calls.
- **Selected Dependencies:** The MVP models road $\to$ hospital/relief $\to$ population accessibility. It does not yet model electrical grids, water treatment plants, or cellular base stations.
- **Deterministic Simulation:** Real-world traffic congestion dynamic assignment (DTA) is abstracted to shortest-path network reachability.

---

## 11. Future Real-Data Integration (Stage 2)
In the production-scale architecture, synthetic layers will be directly ingested from authoritative geospatial feeds:

| Synthetic Component | Production Ingestion Feed | Pipeline Tool / API |
| :--- | :--- | :--- |
| **Flood Water Extent** | **Copernicus Sentinel-1 SAR** (Cloud-penetrating GRD) | Google Earth Engine / ESA Copernicus Hub |
| **Terrain & Elevation** | **Copernicus DEM (GLO-30)** / NASA SRTM | Hydrodynamic 2D slope & depression modeling |
| **Road Network** | **OpenStreetMap (OSM)** | OSMnx road topology & bridge classification |
| **Population Distribution** | **WorldPop** / **Meta HRSL** (100m raster grids) | Spatial population raster zonal statistics |
| **Precipitation Context** | **NASA GPM (IMERG)** / NOAA GFS | Real-time & forecast rainfall accumulation |

---

## 12. Future Machine Learning Road-Failure Prediction (Stage 2)
Stage 2 will integrate an ML classifier predicting continuous road failure probabilities:

```
[ NASA GPM Rainfall (mm/hr) ] ──┐
[ Copernicus DEM Slope (deg)  ] ──┼──> [ ML Classifier / GNN ] ──> P(Road Failure) ──> [ Cascade Engine ]
[ Copernicus DEM Elevation(m) ] ──┤     (Random Forest / XGBoost)
[ Soil Moisture Index (SMAP)  ] ──┤
[ Road Class & Pavement Type  ] ──┘
```

The modular interface specification is already defined in `ml_prediction_interface.py`.

---

## 13. Project Structure
```
cascadebreak-mini/
├── app.py                      # Complete 10-section Streamlit decision-support dashboard
├── cascade_engine.py           # NetworkX topological cascade analysis engine
├── intervention_engine.py      # Multi-modal counterfactual simulator & optimizer
├── scenario.py                 # Synthetic urban road network & deterministic scenarios
├── visualization.py            # Folium network maps (Before vs After)
├── ml_prediction_interface.py  # Stage 2 ML road failure prediction contracts
├── test_cascadebreak.py        # Automated test suite
├── requirements.txt            # Virtual environment requirements
└── README.md                   # System documentation & architectural roadmap
```

---

## 14. How to Install & Run

### 1. Install Dependencies
```bash
cd cascadebreak-mini
pip install -r requirements.txt
```

### 2. Run Automated Test Suite
```bash
python test_cascadebreak.py
```

### 3. Launch Streamlit Application
```bash
streamlit run app.py
```

Access the interactive dashboard at **`http://localhost:8501`**.
