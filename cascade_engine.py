"""
CascadeBreak AI - Cascade Mechanics & Network Evaluation Engine (V2)
===================================================================
Implements the core topological cascade analysis across the urban road network:

Cascade Chain:
  FLOOD EVENT
    ↓
  ROAD DISRUPTION (Submerged / Impassable Edges)
    ↓
  NETWORK FRAGMENTATION (Disconnected Subgraphs)
    ↓
  CRITICAL FACILITY INACCESSIBILITY (Hospital / Relief Isolation)
    ↓
  POPULATION ACCESS LOSS (Residents Severed from Services)

Non-destructive Counterfactual Principle:
  The baseline flooded network remains strictly immutable. Every candidate
  intervention is evaluated on an independent hypothetical clone.
"""

import copy
from typing import Dict, List, Tuple, Any, Optional
import networkx as nx


class CascadeEngine:
    """
    Manages the urban network graph, quantifies cascade disruption metrics,
    and provides non-destructive graph simulation interfaces.
    """

    def __init__(self, nodes: Dict[str, Dict[str, Any]], roads: List[Dict[str, Any]]):
        self.nodes = copy.deepcopy(nodes)
        self.roads = copy.deepcopy(roads)

        # Categorize node sets
        self.hospital_nodes = [nid for nid, attr in self.nodes.items() if attr.get("type") == "hospital"]
        self.relief_nodes = [nid for nid, attr in self.nodes.items() if attr.get("type") == "relief_centre"]
        self.population_nodes = [nid for nid, attr in self.nodes.items() if attr.get("type") == "population"]
        self.junction_nodes = [nid for nid, attr in self.nodes.items() if attr.get("type") == "junction"]

        # Exact total city population
        self.total_city_population = sum(self.nodes[nid]["population"] for nid in self.population_nodes)

        # Baseline graphs
        self.full_graph = self._build_graph(filter_flooded=False)
        self.flooded_graph = self._build_graph(filter_flooded=True)

    def _build_graph(
        self,
        filter_flooded: bool = False,
        custom_roads: Optional[List[Dict[str, Any]]] = None,
        extra_edges: Optional[List[Dict[str, Any]]] = None,
    ) -> nx.Graph:
        """
        Constructs a NetworkX Graph from nodes and road definitions.
        If filter_flooded is True, flooded roads are excluded from the topology.
        """
        G = nx.Graph()

        # Add all nodes with complete metadata
        for node_id, data in self.nodes.items():
            G.add_node(node_id, **data)

        # Add regular roads
        road_list = custom_roads if custom_roads is not None else self.roads
        for r in road_list:
            if filter_flooded and r.get("is_flooded", False):
                continue
            G.add_edge(
                r["u"],
                r["v"],
                road_id=r["road_id"],
                name=r["name"],
                length_km=r["length_km"],
                terrain_factor=r.get("terrain_factor", 1.0),
                damage_factor=r.get("damage_factor", 1.0),
                effort_cost=r.get("effort_cost", 1.0),
                is_flooded=r.get("is_flooded", False),
                is_accessible=r.get("is_accessible", True),
                condition_note=r.get("condition_note", ""),
                is_temporary=False,
            )

        # Add any hypothetical temporary links
        if extra_edges:
            for ex in extra_edges:
                G.add_edge(
                    ex["u"],
                    ex["v"],
                    road_id=ex.get("road_id", f"TEMP_{ex['u']}_{ex['v']}"),
                    name=ex.get("name", "Temporary Emergency Bypass"),
                    length_km=ex.get("length_km", 1.0),
                    effort_cost=ex.get("effort_cost", 3.0),
                    is_flooded=False,
                    is_accessible=True,
                    condition_note=ex.get("condition_note", "Hypothetical temporary link"),
                    is_temporary=True,
                )

        return G

    def evaluate_network_state(self, G: nx.Graph) -> Dict[str, Any]:
        """
        Calculates holistic accessibility metrics for a given network topology:
          - Population reachability to trauma hospitals and relief centres
          - Total population with full (dual) vs partial vs zero access
          - Disconnected critical facilities count
          - Network fragmentation (connected components)
          - Node-by-node accessibility and routing details
        """
        node_status = {}
        pop_with_hospital = 0
        pop_with_relief = 0
        pop_with_both = 0
        pop_fully_isolated = 0

        # Evaluate population clusters
        for p_node in self.population_nodes:
            p_pop = self.nodes[p_node]["population"]
            p_name = self.nodes[p_node]["name"]

            # Hospital reachability
            can_reach_hosp = False
            nearest_hosp_dist = float("inf")
            hosp_path = []
            for h_node in self.hospital_nodes:
                if nx.has_path(G, p_node, h_node):
                    can_reach_hosp = True
                    dist = nx.shortest_path_length(G, p_node, h_node, weight="length_km")
                    if dist < nearest_hosp_dist:
                        nearest_hosp_dist = dist
                        hosp_path = nx.shortest_path(G, p_node, h_node, weight="length_km")

            # Relief centre reachability
            can_reach_relief = False
            nearest_relief_dist = float("inf")
            relief_path = []
            for r_node in self.relief_nodes:
                if nx.has_path(G, p_node, r_node):
                    can_reach_relief = True
                    dist = nx.shortest_path_length(G, p_node, r_node, weight="length_km")
                    if dist < nearest_relief_dist:
                        nearest_relief_dist = dist
                        relief_path = nx.shortest_path(G, p_node, r_node, weight="length_km")

            if can_reach_hosp:
                pop_with_hospital += p_pop
            if can_reach_relief:
                pop_with_relief += p_pop
            if can_reach_hosp and can_reach_relief:
                pop_with_both += p_pop
            if not can_reach_hosp and not can_reach_relief:
                pop_fully_isolated += p_pop

            node_status[p_node] = {
                "name": p_name,
                "population": p_pop,
                "can_reach_hospital": can_reach_hosp,
                "hospital_distance_km": nearest_hosp_dist if can_reach_hosp else None,
                "hospital_path": hosp_path,
                "can_reach_relief": can_reach_relief,
                "relief_distance_km": nearest_relief_dist if can_reach_relief else None,
                "relief_path": relief_path,
                "has_dual_access": (can_reach_hosp and can_reach_relief),
                "is_isolated": (not can_reach_hosp and not can_reach_relief),
            }

        # Check facility reachability (how many population nodes can reach each facility)
        facilities_status = {}
        disconnected_facilities = 0

        for h_node in self.hospital_nodes:
            h_pop_reachable = sum(
                self.nodes[p]["population"] for p in self.population_nodes if nx.has_path(G, p, h_node)
            )
            facilities_status[h_node] = {
                "name": self.nodes[h_node]["name"],
                "type": "hospital",
                "reachable_population": h_pop_reachable,
                "is_operational": h_pop_reachable > 0,
            }
            if h_pop_reachable == 0:
                disconnected_facilities += 1

        for r_node in self.relief_nodes:
            r_pop_reachable = sum(
                self.nodes[p]["population"] for p in self.population_nodes if nx.has_path(G, p, r_node)
            )
            facilities_status[r_node] = {
                "name": self.nodes[r_node]["name"],
                "type": "relief_centre",
                "reachable_population": r_pop_reachable,
                "is_operational": r_pop_reachable > 0,
            }
            if r_pop_reachable == 0:
                disconnected_facilities += 1

        num_components = nx.number_connected_components(G)

        return {
            "total_population": self.total_city_population,
            "pop_with_hospital": pop_with_hospital,
            "pop_without_hospital": self.total_city_population - pop_with_hospital,
            "pop_with_relief": pop_with_relief,
            "pop_without_relief": self.total_city_population - pop_with_relief,
            "pop_with_both": pop_with_both,
            "pop_without_both": self.total_city_population - pop_with_both,
            "pop_fully_isolated": pop_fully_isolated,
            "disconnected_facilities_count": disconnected_facilities,
            "facilities_status": facilities_status,
            "node_status": node_status,
            "num_connected_components": num_components,
            "active_road_count": G.number_of_edges(),
        }

    def get_baseline_summary(self) -> Dict[str, Any]:
        """
        Returns pre-flood (ideal) vs flooded baseline evaluation with complete cascade details.
        """
        pre_flood = self.evaluate_network_state(self.full_graph)
        flooded = self.evaluate_network_state(self.flooded_graph)
        flooded_roads = [r for r in self.roads if r.get("is_flooded", False)]

        cascade_progression = {
            "step_1_flood_disruption": f"{len(flooded_roads)} road corridors submerged or blocked.",
            "step_2_network_fragmentation": f"Network fragmented into {flooded['num_connected_components']} isolated component(s).",
            "step_3_facility_impact": f"{flooded['pop_without_hospital']:,} pop cut off from Hospital; {flooded['pop_without_relief']:,} pop cut off from Relief Centre.",
            "step_4_population_isolation": f"{flooded['pop_without_both']:,} residents lose dual critical access ({flooded['pop_fully_isolated']:,} completely isolated).",
        }

        return {
            "total_roads": len(self.roads),
            "total_population": self.total_city_population,
            "flooded_road_count": len(flooded_roads),
            "flooded_roads": flooded_roads,
            "pre_flood_metrics": pre_flood,
            "flooded_metrics": flooded,
            "cascade_progression": cascade_progression,
        }

    def find_rerouting_path(self, origin: str, destination: str, use_flooded_graph: bool = True) -> Optional[Dict[str, Any]]:
        """
        Finds the shortest accessible path between origin and destination.
        """
        G = self.flooded_graph if use_flooded_graph else self.full_graph
        if not nx.has_path(G, origin, destination):
            return None

        path = nx.shortest_path(G, origin, destination, weight="length_km")
        distance = nx.shortest_path_length(G, origin, destination, weight="length_km")

        segments = []
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            edge_data = G.get_edge_data(u, v)
            segments.append({
                "from_node": u,
                "from_name": self.nodes[u]["name"],
                "to_node": v,
                "to_name": self.nodes[v]["name"],
                "road_id": edge_data.get("road_id", "N/A"),
                "road_name": edge_data.get("name", "N/A"),
                "length_km": edge_data.get("length_km", 0.0),
            })

        return {
            "path_nodes": path,
            "total_distance_km": round(distance, 2),
            "hop_count": len(path) - 1,
            "segments": segments,
        }
