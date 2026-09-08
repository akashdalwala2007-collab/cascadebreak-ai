"""
CascadeBreak AI - Geospatial & Network Visualization Module (V2)
================================================================
Generates dark-themed climate-tech GIS maps for baseline flooded state,
counterfactual intervention states, and Before vs After comparison views.
"""

from typing import Dict, List, Any, Optional
import folium
from folium.features import DivIcon


def create_network_map(
    nodes: Dict[str, Dict[str, Any]],
    roads: List[Dict[str, Any]],
    node_status: Dict[str, Any],
    title: str = "Urban Road Network",
    highlight_roads: Optional[List[str]] = None,
    extra_edges: Optional[List[Dict[str, Any]]] = None,
) -> folium.Map:
    """
    Creates a dark tactical GIS Folium map representing the network state.

    Color Palette:
      - 🟢 Green (#22C55E): Passable / Accessible Road
      - 🔴 Red (#EF4444): Flooded / Impassable Road (Dashed)
      - 🔵 Cyan (#22D3EE): Restored / Selected Intervention / Tactical Bypass (Bold)
      - 🟠 Amber (#F59E0B): Partial Access / Warning
      - ⬛ Basemap: CartoDB dark_matter
    """
    avg_lat = sum(n["lat"] for n in nodes.values()) / len(nodes)
    avg_lon = sum(n["lon"] for n in nodes.values()) / len(nodes)

    m = folium.Map(
        location=[avg_lat, avg_lon],
        zoom_start=12,
        tiles="CartoDB dark_matter",
        control_scale=True,
    )

    highlight_set = set(highlight_roads or [])

    # 1. Draw regular roads
    for road in roads:
        u_node = nodes[road["u"]]
        v_node = nodes[road["v"]]
        coords = [[u_node["lat"], u_node["lon"]], [v_node["lat"], v_node["lon"]]]

        r_id = road["road_id"]
        is_flood = road.get("is_flooded", False)
        is_highlight = r_id in highlight_set

        if is_highlight:
            road_color = "#22D3EE"  # Electric Cyan for restored/selected intervention
            dash_array = None
            weight = 5.5
            opacity = 0.95
            status_text = "<span style='color:#22D3EE;font-weight:700;'>RESTORED BY INTERVENTION</span>"
        elif is_flood:
            road_color = "#EF4444"  # Semantic Red for flooded
            dash_array = "7, 7"
            weight = 4.0
            opacity = 0.90
            status_text = "<span style='color:#EF4444;font-weight:700;'>FLOODED (Impassable)</span>"
        else:
            road_color = "#22C55E"  # Semantic Green for open
            dash_array = None
            weight = 3.0
            opacity = 0.75
            status_text = "<span style='color:#22C55E;font-weight:700;'>OPEN (Accessible)</span>"

        tooltip_html = f"""
        <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    background: #111C2E; color: #F1F5F9; border: 1px solid #24344D;
                    padding: 8px 12px; border-radius: 6px; min-width: 180px; font-size: 12px;">
            <div style="font-weight: 700; color: #F1F5F9; margin-bottom: 2px;">{r_id}: {road['name']}</div>
            <div style="margin-bottom: 4px;">Status: {status_text}</div>
            <div style="color: #94A3B8; font-size: 11px;">Length: {road['length_km']} km | Effort: {road.get('effort_cost', 'N/A')} pts</div>
            <div style="color: #64748B; font-size: 10px; margin-top: 3px; font-style: italic;">{road.get('condition_note', '')}</div>
        </div>
        """

        folium.PolyLine(
            locations=coords,
            color=road_color,
            weight=weight,
            dash_array=dash_array,
            opacity=opacity,
            tooltip=folium.Tooltip(tooltip_html),
        ).add_to(m)

    # 2. Draw hypothetical temporary edges (Electric Cyan dashed)
    if extra_edges:
        for ex in extra_edges:
            u_node = nodes[ex["u"]]
            v_node = nodes[ex["v"]]
            coords = [[u_node["lat"], u_node["lon"]], [v_node["lat"], v_node["lon"]]]

            tooltip_html = f"""
            <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                        background: #111C2E; color: #F1F5F9; border: 1px solid #22D3EE;
                        padding: 8px 12px; border-radius: 6px; min-width: 180px; font-size: 12px;">
                <div style="font-weight: 700; color: #22D3EE; margin-bottom: 2px;">{ex.get('name', 'Temporary Emergency Link')}</div>
                <div style="margin-bottom: 4px; color: #22D3EE; font-weight: 600;">TEMPORARY ACCESS DEPLOYED</div>
                <div style="color: #94A3B8; font-size: 11px;">Length: {ex.get('length_km', 0.0)} km | Effort: {ex.get('effort_cost', 3.0)} pts</div>
                <div style="color: #64748B; font-size: 10px; margin-top: 3px; font-style: italic;">{ex.get('condition_note', '')}</div>
            </div>
            """

            folium.PolyLine(
                locations=coords,
                color="#22D3EE",
                weight=5.5,
                dash_array="5, 5",
                opacity=0.95,
                tooltip=folium.Tooltip(tooltip_html),
            ).add_to(m)

    # 3. Draw nodes
    for node_id, node in nodes.items():
        loc = [node["lat"], node["lon"]]
        ntype = node["type"]

        if ntype == "hospital":
            # Tactical HUD Hospital Icon
            icon_html = """
            <div style="background-color: #111C2E; border: 2px solid #EF4444; border-radius: 6px;
                        width: 28px; height: 28px; display: flex; align-items: center; justify-content: center;
                        box-shadow: 0 0 12px rgba(239, 68, 68, 0.4); font-size: 15px; cursor: pointer;">
                🏥
            </div>
            """
            folium.Marker(
                location=loc,
                tooltip=folium.Tooltip(
                    f"""
                    <div style="background:#111C2E; color:#F1F5F9; border:1px solid #EF4444; padding:8px 12px; border-radius:6px; font-size:12px;">
                        <b style="color:#EF4444;">🏥 {node['name']}</b><br>
                        <span style="color:#94A3B8;">Level-1 Trauma Center • {node.get('capacity_beds', 600)} Beds</span>
                    </div>
                    """
                ),
                icon=DivIcon(icon_size=(28, 28), icon_anchor=(14, 14), html=icon_html),
            ).add_to(m)

        elif ntype == "relief_centre":
            # Tactical HUD Relief Hub Icon
            icon_html = """
            <div style="background-color: #111C2E; border: 2px solid #22D3EE; border-radius: 6px;
                        width: 28px; height: 28px; display: flex; align-items: center; justify-content: center;
                        box-shadow: 0 0 12px rgba(34, 211, 238, 0.4); font-size: 15px; cursor: pointer;">
                🛡️
            </div>
            """
            folium.Marker(
                location=loc,
                tooltip=folium.Tooltip(
                    f"""
                    <div style="background:#111C2E; color:#F1F5F9; border:1px solid #22D3EE; padding:8px 12px; border-radius:6px; font-size:12px;">
                        <b style="color:#22D3EE;">🛡️ {node['name']}</b><br>
                        <span style="color:#94A3B8;">Relief Logistics Hub • {node.get('capacity_evacuees', 3000):,} Evacuees</span>
                    </div>
                    """
                ),
                icon=DivIcon(icon_size=(28, 28), icon_anchor=(14, 14), html=icon_html),
            ).add_to(m)

        elif ntype == "population":
            status = node_status.get(node_id, {})
            can_h = status.get("can_reach_hospital", False)
            can_r = status.get("can_reach_relief", False)

            if can_h and can_r:
                marker_color = "#22C55E"
                status_label = "<span style='color:#22C55E;font-weight:600;'>FULL ACCESS</span>"
            elif can_h or can_r:
                marker_color = "#F59E0B"
                status_label = "<span style='color:#F59E0B;font-weight:600;'>PARTIAL ACCESS</span>"
            else:
                marker_color = "#EF4444"
                status_label = "<span style='color:#EF4444;font-weight:700;'>ISOLATED</span>"

            folium.CircleMarker(
                location=loc,
                radius=9,
                color="#0B1220",
                weight=2,
                fill=True,
                fill_color=marker_color,
                fill_opacity=0.92,
                tooltip=folium.Tooltip(
                    f"""
                    <div style="background:#111C2E; color:#F1F5F9; border:1px solid #24344D; padding:8px 12px; border-radius:6px; font-size:12px;">
                        <b style="color:#F1F5F9;">👥 {node['name']} ({node_id})</b><br>
                        <span style="color:#94A3B8;">Population: {node['population']:,}</span><br>
                        <div style="margin-top:3px;">Status: {status_label}</div>
                        <div style="color:#94A3B8; font-size:11px; margin-top:2px;">
                            Hospital: {'✅ Reachable' if can_h else '❌ Blocked'} | Relief: {'✅ Reachable' if can_r else '❌ Blocked'}
                        </div>
                    </div>
                    """
                ),
            ).add_to(m)

        else:
            # Junction / Intersection: subtle muted node
            folium.CircleMarker(
                location=loc,
                radius=3.5,
                color="#0B1220",
                weight=1.5,
                fill=True,
                fill_color="#64748B",
                fill_opacity=0.7,
                tooltip=folium.Tooltip(
                    f"""
                    <div style="background:#111C2E; color:#F1F5F9; border:1px solid #24344D; padding:4px 8px; border-radius:4px; font-size:11px;">
                        <span style="color:#94A3B8;">Junction:</span> <b>{node['name']}</b> ({node_id})
                    </div>
                    """
                ),
            ).add_to(m)

    return m
