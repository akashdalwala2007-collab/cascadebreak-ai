"""
CascadeBreak AI - Synthetic City & Flood Scenario Module (V2)
============================================================
Defines the synthetic road network, critical facility locations, population
clusters, and deterministic flood hazard scenarios.

Key Concept:
  - Nodes represent population clusters, hospitals, relief centres, and junctions.
  - Edges represent road corridors with length, terrain factor, damage factor, and
    calculated Intervention Effort Index.
  - Deterministic scenarios demonstrate diverse cascade phenomena, including cases
    where "Most Damaged Road != Most Valuable Intervention" and Multi-Route Bottlenecks.
"""

from typing import Dict, List, Any


def get_synthetic_city_nodes() -> Dict[str, Dict[str, Any]]:
    """
    Generates deterministic synthetic city nodes.

    Total population across all clusters: 59,000 residents.
      - N1: North Suburb (12,000)
      - N2: North-East District (15,000)
      - N3: West Hills (8,000)
      - N8: East Industrial Zone (10,000)
      - N9: South Riverside (14,000)
      - N6: City General Hospital (Critical Facility)
      - N7: Central Disaster Relief Centre (Critical Facility)
      - N4, N5, N10, N11: Key Intersections & Bridgeheads
    """
    nodes = {
        "N1": {
            "name": "North Suburb (Sector 1)",
            "type": "population",
            "lat": 13.0820,
            "lon": 80.2200,
            "population": 12000,
            "description": "High-density residential neighborhood in the north.",
        },
        "N2": {
            "name": "North-East District (Sector 2)",
            "type": "population",
            "lat": 13.0850,
            "lon": 80.2600,
            "population": 15000,
            "description": "Dense urban community near eastern commercial zone.",
        },
        "N3": {
            "name": "West Hills (Sector 3)",
            "type": "population",
            "lat": 13.0450,
            "lon": 80.1900,
            "population": 8000,
            "description": "Foothill township with limited egress corridors.",
        },
        "N4": {
            "name": "Central Transit Junction",
            "type": "junction",
            "lat": 13.0500,
            "lon": 80.2350,
            "population": 0,
            "description": "Major multi-lane city intersection north of the river.",
        },
        "N5": {
            "name": "River Bridge Hub",
            "type": "junction",
            "lat": 13.0350,
            "lon": 80.2450,
            "population": 0,
            "description": "Key river crossing bridgehead connecting North and South sectors.",
        },
        "N6": {
            "name": "City General Hospital",
            "type": "hospital",
            "lat": 13.0250,
            "lon": 80.2300,
            "population": 0,
            "capacity_beds": 600,
            "description": "Level-1 emergency trauma center and regional hospital.",
        },
        "N7": {
            "name": "Central Disaster Relief Centre",
            "type": "relief_centre",
            "lat": 13.0650,
            "lon": 80.2500,
            "population": 0,
            "capacity_evacuees": 3000,
            "description": "Main logistics warehouse for food, potable water, and rescue staging.",
        },
        "N8": {
            "name": "East Industrial Zone",
            "type": "population",
            "lat": 13.0300,
            "lon": 80.2750,
            "population": 10000,
            "description": "Mixed commercial-worker housing area along eastern river basin.",
        },
        "N9": {
            "name": "South Riverside (Sector 4)",
            "type": "population",
            "lat": 13.0050,
            "lon": 80.2400,
            "population": 14000,
            "description": "Dense riverside residential zone south of the river.",
        },
        "N10": {
            "name": "South-West Junction",
            "type": "junction",
            "lat": 13.0100,
            "lon": 80.2050,
            "population": 0,
            "description": "Peripheral arterial junction connecting southern roads to West Hills.",
        },
        "N11": {
            "name": "North Metro Hub",
            "type": "junction",
            "lat": 13.0650,
            "lon": 80.2150,
            "population": 0,
            "description": "Northern interchange linking North Suburb with Central ring.",
        },
    }
    return nodes


def get_base_road_catalog() -> List[Dict[str, Any]]:
    """
    Returns the physical catalog of roads with baseline geometric and terrain attributes.
    Intervention Effort Index = length_km * terrain_factor * damage_factor
    """
    return [
        {"road_id": "R1", "u": "N1", "v": "N11", "name": "North Suburb Expressway", "length_km": 2.1, "terrain_factor": 1.0, "base_damage": 1.0},
        {"road_id": "R2", "u": "N11", "v": "N7", "name": "Relief Centre North Link", "length_km": 3.5, "terrain_factor": 1.0, "base_damage": 1.0},
        {"road_id": "R3", "u": "N2", "v": "N7", "name": "North-East Relief Corridor", "length_km": 2.4, "terrain_factor": 1.0, "base_damage": 1.0},
        {"road_id": "R4", "u": "N3", "v": "N4", "name": "West Hills Central Highway", "length_km": 4.8, "terrain_factor": 1.3, "base_damage": 1.2},
        {"road_id": "R5", "u": "N4", "v": "N5", "name": "Grand River Arterial Bridge", "length_km": 2.0, "terrain_factor": 1.5, "base_damage": 1.0},
        {"road_id": "R6", "u": "N5", "v": "N6", "name": "Hospital Main Approach Boulevard", "length_km": 1.8, "terrain_factor": 1.1, "base_damage": 1.0},
        {"road_id": "R7", "u": "N4", "v": "N11", "name": "Metro Inner Ring Road", "length_km": 2.2, "terrain_factor": 1.0, "base_damage": 1.0},
        {"road_id": "R8", "u": "N4", "v": "N7", "name": "Central-to-Relief Link Road", "length_km": 2.0, "terrain_factor": 1.0, "base_damage": 1.0},
        {"road_id": "R9", "u": "N5", "v": "N8", "name": "East Industrial Riverside Way", "length_km": 3.2, "terrain_factor": 1.2, "base_damage": 1.0},
        {"road_id": "R10", "u": "N8", "v": "N2", "name": "East Coastal Bypass", "length_km": 6.5, "terrain_factor": 1.4, "base_damage": 1.5},
        {"road_id": "R11", "u": "N5", "v": "N9", "name": "South Riverside Connector", "length_km": 3.4, "terrain_factor": 1.2, "base_damage": 1.0},
        {"road_id": "R12", "u": "N10", "v": "N9", "name": "South-West Perimeter Ave", "length_km": 3.8, "terrain_factor": 1.0, "base_damage": 1.0},
        {"road_id": "R13", "u": "N10", "v": "N6", "name": "Hospital West Access Spur", "length_km": 3.0, "terrain_factor": 1.1, "base_damage": 1.0},
        {"road_id": "R14", "u": "N3", "v": "N10", "name": "West Ridge Mountain Pass", "length_km": 4.2, "terrain_factor": 1.5, "base_damage": 1.2},
        {"road_id": "R15", "u": "N1", "v": "N4", "name": "North-Central Direct Arterial", "length_km": 3.8, "terrain_factor": 1.0, "base_damage": 1.0},
        {"road_id": "R16", "u": "N9", "v": "N6", "name": "South Hospital Underpass", "length_km": 2.5, "terrain_factor": 1.4, "base_damage": 1.4},
    ]


def get_synthetic_city_roads(scenario_name: str = "Scenario 1: Urban Flood — Distributed Road Failures") -> List[Dict[str, Any]]:
    """
    Generates synthetic road edges with distances, damage states, and calculated
    Intervention Effort Index based on the selected scenario.

    Formula:
      Intervention Effort Index = round(length_km * terrain_factor * damage_factor, 1)
    """
    base_catalog = get_base_road_catalog()

    # Scenario Flood Profiles with specific damage factors and hazard context
    scenario_profiles = {
        "Scenario 1: Urban Flood — Distributed Road Failures": {
            "R4": {"damage_factor": 1.6, "note": "Mudflow & debris on West Highway"},
            "R5": {"damage_factor": 1.5, "note": "Major River Surge submerge Grand River Arterial Bridge"},
            "R10": {"damage_factor": 1.8, "note": "Storm Surge inundates East Coastal Bypass"},
            "R16": {"damage_factor": 2.0, "note": "Localized deep water submersion in South Underpass"},
        },
        "Scenario 2: Critical Corridor Disruption": {
            # In this scenario, R10 has massive damage (very high effort), but R3 or R1 has lower effort
            # Demonstrates: MOST DAMAGED ROAD != MOST VALUABLE INTERVENTION
            "R1": {"damage_factor": 1.2, "note": "Minor standing water near North Metro interchange"},
            "R3": {"damage_factor": 1.2, "note": "Localized street flooding on NE Relief Corridor"},
            "R10": {"damage_factor": 2.5, "note": "Catastrophic coastal embankment collapse (High Damage)"},
            "R15": {"damage_factor": 1.4, "note": "Culvert overflow on North-Central Arterial"},
        },
        "Scenario 3: Multi-Route Bottleneck": {
            # Simultaneous failure of all access corridors to Hospital N6 and central river
            "R5": {"damage_factor": 1.5, "note": "Grand River Bridge submerged by cresting river"},
            "R6": {"damage_factor": 1.4, "note": "Hospital Main Approach Boulevard inundated"},
            "R13": {"damage_factor": 1.3, "note": "Hospital West Access Spur blocked by wash"},
            "R16": {"damage_factor": 1.8, "note": "South Hospital Underpass deeply inundated"},
        },
        "Scenario 4: Baseline Clear (No Inundation / Zero Disruption)": {
            # Edge case scenario: zero flooded roads
        }
    }

    active_floods = scenario_profiles.get(scenario_name, scenario_profiles["Scenario 1: Urban Flood — Distributed Road Failures"])

    roads = []
    for base in base_catalog:
        r_id = base["road_id"]
        is_flooded = r_id in active_floods
        
        if is_flooded:
            flood_info = active_floods[r_id]
            damage_factor = flood_info.get("damage_factor", base["base_damage"])
            condition_note = flood_info.get("note", "Road flooded and impassable.")
        else:
            damage_factor = 1.0
            condition_note = "Road clear and passable."

        # Intervention Effort Index calculation
        effort_index = round(base["length_km"] * base["terrain_factor"] * damage_factor, 1)

        roads.append({
            "road_id": r_id,
            "u": base["u"],
            "v": base["v"],
            "name": base["name"],
            "length_km": base["length_km"],
            "terrain_factor": base["terrain_factor"],
            "damage_factor": damage_factor,
            "effort_cost": effort_index,
            "is_flooded": is_flooded,
            "is_accessible": not is_flooded,
            "condition_note": condition_note,
        })

    return roads


def get_available_scenarios() -> List[str]:
    """Returns list of preset scenario names."""
    return [
        "Scenario 1: Urban Flood — Distributed Road Failures",
        "Scenario 2: Critical Corridor Disruption",
        "Scenario 3: Multi-Route Bottleneck",
        "Scenario 4: Baseline Clear (No Inundation / Zero Disruption)",
    ]


def get_scenario_metadata(scenario_name: str) -> Dict[str, str]:
    """Returns educational contextual descriptions for each scenario."""
    descriptions = {
        "Scenario 1: Urban Flood — Distributed Road Failures": (
            "A distributed river surge cuts across central and western corridors. "
            "Evaluates multi-modal options: bridge restorations vs temporary culvert links."
        ),
        "Scenario 2: Critical Corridor Disruption": (
            "A storm surge batters the east coast while peripheral flash floods hit the north. "
            "Crucially demonstrates that the **Most Damaged Road (R10)** is NOT the most valuable intervention "
            "because restoring R3/R1 yields higher access restoration for far less intervention effort."
        ),
        "Scenario 3: Multi-Route Bottleneck": (
            "All primary corridors to the Trauma Hospital (R6, R13, R16) and Central River (R5) are inundated. "
            "Demonstrates the power of **Temporary Access Bridges (TEMP_N4_N6)** or **Combined Packages (R5+R6)** "
            "when single-edge road repairs are blocked by upstream cuts."
        ),
        "Scenario 4: Baseline Clear (No Inundation / Zero Disruption)": (
            "All roads are operational. Used to verify that the decision-support system cleanly detects "
            "when no intervention is required without generating fake or zero-benefit recommendations."
        ),
    }
    return {
        "title": scenario_name,
        "description": descriptions.get(scenario_name, "Standard urban flood scenario."),
    }
