import os
import math
import pandas as pd
import networkx as nx

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')


def haversine(lat1, lon1, lat2, lon2):
    """Distance in meters between two GPS coordinates."""
    R = 6371000
    p = math.pi / 180
    a = (math.sin((lat2 - lat1) * p / 2) ** 2
         + math.cos(lat1 * p) * math.cos(lat2 * p)
         * math.sin((lon2 - lon1) * p / 2) ** 2)
    return 2 * R * math.asin(math.sqrt(a))


def build_graph():
    nodes = pd.read_excel(
        os.path.join(DATA_DIR, 'Nodes_sheet - 1.xlsx'),
        sheet_name='Nodes'
    )
    edges = pd.read_excel(
        os.path.join(DATA_DIR, 'Edges_with_distance.xlsx')
    )

    nodes = nodes.dropna(subset=['Id', 'Name', 'Latitude', 'Longitude'])
    edges = edges.dropna(subset=['From', 'To', 'Distance_m'])

    nodes['Id'] = nodes['Id'].astype(int)
    edges['From'] = edges['From'].astype(int)
    edges['To'] = edges['To'].astype(int)

    G = nx.Graph()

    for _, row in nodes.iterrows():
        G.add_node(
            row['Id'],
            name=row['Name'].strip(),
            lat=float(row['Latitude']),
            lon=float(row['Longitude']),
            node_type=str(row['Type']).strip() if pd.notna(row['Type']) else 'unknown'
        )

    for _, row in edges.iterrows():
        G.add_edge(row['From'], row['To'], weight=float(row['Distance_m']))

    
    for u, v, w in [(6, 4, 38.1), (35, 9, 50.1), (37, 36, 11.4)]:
        if not G.has_edge(u, v):
            G.add_edge(u, v, weight=w)

    # Name → ID lookup (lowercase)
    name_to_id = {
        row['Name'].strip().lower(): int(row['Id'])
        for _, row in nodes.iterrows()
    }

    # Campus gates — used for off-campus routing
    gate_nodes = [
        {
            'id': int(row['Id']),
            'name': row['Name'].strip(),
            'lat': float(row['Latitude']),
            'lon': float(row['Longitude']),
        }
        for _, row in nodes.iterrows()
        if str(row.get('Type', '')).strip().lower() == 'gate'
    ]

    return G, nodes, name_to_id, gate_nodes


# Loaded once at Django startup — reused for every request
G, NODES_DF, NAME_TO_ID, GATE_NODES = build_graph()