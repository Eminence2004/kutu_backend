import math
from math import radians, sin, cos, sqrt, atan2

import networkx as nx
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .graph import G, NODES_DF, NAME_TO_ID, GATE_NODES, haversine
from .models import Washroom, SuggestedLocation, PostLocationSuggestion


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _resolve_location(param_name, param_id, name_str):
    """Returns (node_id, error_response) — one will be None."""
    if param_id:
        nid = int(param_id)
        if nid not in G.nodes:
            return None, Response({'error': f'ID {nid} not found'}, status=404)
        return nid, None
    if name_str:
        key = name_str.strip().lower()
        if key in NAME_TO_ID:
            return NAME_TO_ID[key], None
        matches = [k for k in NAME_TO_ID if key in k]
        if matches:
            return NAME_TO_ID[matches[0]], None
        return None, Response(
            {
                'error': f'Location "{name_str}" not found',
                'hint': 'Use /api/navigation/locations/ to see all locations',
            },
            status=404,
        )
    return None, Response({'error': f'Provide {param_name} or {param_name}_id'}, status=400)


def _build_route_response(start_id, end_id):
    """Core shortest-path logic. Returns a Response."""
    if start_id == end_id:
        return Response({'error': 'Start and destination are the same'}, status=400)
    try:
        path = nx.shortest_path(G, start_id, end_id, weight='weight')
        distance_m = nx.shortest_path_length(G, start_id, end_id, weight='weight')
    except nx.NetworkXNoPath:
        return Response({'error': 'No walking path found between these locations'}, status=404)
    except nx.NodeNotFound as e:
        return Response({'error': str(e)}, status=404)

    coordinates, steps = [], []
    for i, nid in enumerate(path):
        row = NODES_DF[NODES_DF['Id'] == nid].iloc[0]
        coordinates.append({
            'latitude': float(row['Latitude']),
            'longitude': float(row['Longitude']),
        })
        if i < len(path) - 1:
            nxt = NODES_DF[NODES_DF['Id'] == path[i + 1]].iloc[0]
            steps.append({
                'from': row['Name'].strip(),
                'to': nxt['Name'].strip(),
                'instruction': f'Head towards {nxt["Name"].strip()}',
            })

    return Response({
        'start': NODES_DF[NODES_DF['Id'] == start_id].iloc[0]['Name'].strip(),
        'end': NODES_DF[NODES_DF['Id'] == end_id].iloc[0]['Name'].strip(),
        'path_ids': path,
        'coordinates': coordinates,
        'steps': steps,
        'distance_m': round(distance_m, 2),
        'distance_km': round(distance_m / 1000, 3),
        'estimated_walk_minutes': round(distance_m / 80, 1),
    })


def _haversine_m(lat1, lon1, lat2, lon2):
    """Haversine distance in metres between two GPS points."""
    R = 6_371_000
    phi1, phi2 = radians(lat1), radians(lat2)
    dphi = radians(lat2 - lat1)
    dlambda = radians(lon2 - lon1)
    a = sin(dphi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(dlambda / 2) ** 2
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))


# ─────────────────────────────────────────────────────────────────────────────
# NAVIGATION ENDPOINTS
# ─────────────────────────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([AllowAny])
def get_locations(request):
    """
    All campus locations for dropdown/map markers.
    GET /api/navigation/locations/
    """
    locations = [
        {
            'id': int(row['Id']),
            'name': row['Name'].strip(),
            'latitude': float(row['Latitude']),
            'longitude': float(row['Longitude']),
            'type': str(row['Type']).strip() if str(row['Type']) != 'nan' else 'path',
        }
        for _, row in NODES_DF.iterrows()
    ]
    return Response({'locations': locations})


@api_view(['GET'])
@permission_classes([AllowAny])
def get_route(request):
    """
    Shortest walking route between two campus locations.
    GET /api/navigation/route/?start_id=1&end_id=23
    GET /api/navigation/route/?start=A Block&end=Canteen (cafetaria) Place
    """
    start_id, err = _resolve_location('start', request.GET.get('start_id'), request.GET.get('start'))
    if err:
        return err
    end_id, err = _resolve_location('end', request.GET.get('end_id'), request.GET.get('end'))
    if err:
        return err

    return _build_route_response(start_id, end_id)


@api_view(['GET'])
@permission_classes([AllowAny])
def search_locations(request):
    """
    Partial-name search for autocomplete.
    GET /api/navigation/search/?q=block
    """
    query = request.GET.get('q', '').strip().lower()
    if not query:
        return Response({'results': []})

    results = [
        {
            'id': int(row['Id']),
            'name': row['Name'].strip(),
            'latitude': float(row['Latitude']),
            'longitude': float(row['Longitude']),
            'type': str(row['Type']).strip() if str(row['Type']) != 'nan' else 'path',
        }
        for _, row in NODES_DF.iterrows()
        if query in row['Name'].strip().lower()
    ]
    return Response({'results': results})


@api_view(['GET'])
@permission_classes([AllowAny])
def nearest_gate(request):
    """
    For a user who is OFF-CAMPUS — returns the nearest campus gate
    plus the on-campus route from that gate to the desired destination.
    """
    try:
        user_lat = float(request.GET.get('lat'))
        user_lon = float(request.GET.get('lon'))
    except (TypeError, ValueError):
        return Response({'error': 'Provide lat and lon query parameters'}, status=400)

    dest_id, err = _resolve_location(
        'destination',
        request.GET.get('destination_id'),
        request.GET.get('destination'),
    )
    if err:
        return err

    nearest = None
    min_dist = float('inf')
    for gate in GATE_NODES:
        d = haversine(user_lat, user_lon, gate['lat'], gate['lon'])
        if d < min_dist:
            min_dist = d
            nearest = gate

    if not nearest:
        return Response({'error': 'No campus gates found in database'}, status=500)

    gmaps_url = (
        f"https://www.google.com/maps/dir/?api=1"
        f"&origin={user_lat},{user_lon}"
        f"&destination={nearest['lat']},{nearest['lon']}"
        f"&travelmode=walking"
    )

    campus_route_response = _build_route_response(nearest['id'], dest_id)
    campus_route_data = campus_route_response.data

    return Response({
        'mode': 'off_campus',
        'message': f'You are outside campus. Head to {nearest["name"]} first.',
        'nearest_gate': {
            'id': nearest['id'],
            'name': nearest['name'],
            'latitude': nearest['lat'],
            'longitude': nearest['lon'],
            'distance_to_gate_m': round(min_dist, 1),
            'distance_to_gate_km': round(min_dist / 1000, 2),
            'estimated_walk_to_gate_minutes': round(min_dist / 80, 1),
        },
        'google_maps_url': gmaps_url,
        'on_campus_route': campus_route_data,
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def get_gates(request):
    """Returns all campus gate locations."""
    return Response({'gates': GATE_NODES})


# ─────────────────────────────────────────────────────────────────────────────
# ITEM 2: WASHROOM ENDPOINTS
# ─────────────────────────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([AllowAny])
def nearby_washrooms(request):
    try:
        user_lat = float(request.GET.get('lat'))
        user_lon = float(request.GET.get('lon'))
    except (TypeError, ValueError):
        return Response({'error': 'lat and lon are required and must be valid numbers.'}, status=400)

    radius = float(request.GET.get('radius', 400))
    gender_filter = request.GET.get('gender', '').strip().lower()

    washrooms_qs = Washroom.objects.filter(is_active=True)
    if gender_filter == 'male':
        washrooms_qs = washrooms_qs.filter(gender__in=['male', 'unisex'])
    elif gender_filter == 'female':
        washrooms_qs = washrooms_qs.filter(gender__in=['female', 'unisex'])
    elif gender_filter == 'unisex':
        washrooms_qs = washrooms_qs.filter(gender='unisex')

    results = []
    for w in washrooms_qs:
        dist = _haversine_m(user_lat, user_lon, w.latitude, w.longitude)
        if dist <= radius:
            results.append({
                'id': w.id,
                'name': w.name,
                'gender': w.gender,
                'gender_display': w.get_gender_display(),
                'latitude': w.latitude,
                'longitude': w.longitude,
                'description': w.description,
                'distance_m': round(dist),
                'walk_seconds': round(dist / 1.2),
                'walk_minutes': round(dist / 1.2 / 60, 1),
            })

    results.sort(key=lambda x: x['distance_m'])
    return Response({
        'count': len(results),
        'user_location': {'latitude': user_lat, 'longitude': user_lon},
        'radius_m': radius,
        'washrooms': results,
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def all_washrooms(request):
    washrooms = Washroom.objects.filter(is_active=True)
    data = [{
        'id': w.id,
        'name': w.name,
        'gender': w.gender,
        'gender_display': w.get_gender_display(),
        'latitude': w.latitude,
        'longitude': w.longitude,
        'description': w.description,
    } for w in washrooms]
    return Response({'washrooms': data})


# ─────────────────────────────────────────────────────────────────────────────
# ITEM 4: STUDENT-SUGGESTED MAP LOCATIONS
# ─────────────────────────────────────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def suggest_location(request):
    """
    Student submits a new campus location for admin approval.
    POST /api/navigation/suggest-location/
    Body: { name, location_type, latitude, longitude, description }
    """
    name = request.data.get('name', '').strip()
    location_type = request.data.get('location_type', 'other')
    description = request.data.get('description', '').strip()

    try:
        latitude = float(request.data.get('latitude'))
        longitude = float(request.data.get('longitude'))
    except (TypeError, ValueError):
        return Response({'error': 'Valid latitude and longitude are required.'}, status=400)

    if not name:
        return Response({'error': 'Location name is required.'}, status=400)

    # Prevent duplicate pending submissions
    existing = SuggestedLocation.objects.filter(
        submitted_by=request.user,
        name__iexact=name,
        status='pending'
    ).first()
    if existing:
        return Response({'message': 'You already submitted this location. It is pending review.'})

    suggestion = SuggestedLocation.objects.create(
        submitted_by=request.user,
        name=name,
        location_type=location_type,
        latitude=latitude,
        longitude=longitude,
        description=description,
    )

    return Response({
        'message': 'Location submitted for admin approval. Thank you!',
        'id': suggestion.id,
        'status': suggestion.status,
    }, status=201)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_suggested_locations(request):
    """Returns all location suggestions submitted by the logged-in student."""
    suggestions = SuggestedLocation.objects.filter(submitted_by=request.user)
    data = [{
        'id': s.id,
        'name': s.name,
        'location_type': s.location_type,
        'latitude': s.latitude,
        'longitude': s.longitude,
        'status': s.status,
        'admin_note': s.admin_note,
        'submitted_at': s.submitted_at,
    } for s in suggestions]
    return Response({'suggestions': data})


@api_view(['GET'])
@permission_classes([AllowAny])
def approved_suggested_locations(request):
    """
    Returns all admin-approved student-suggested locations.
    Shown as purple markers on the map alongside Excel nodes.
    GET /api/navigation/suggest-location/approved/
    """
    locations = SuggestedLocation.objects.filter(status='approved')
    data = [{
        'id': f"s{loc.id}",
        'name': loc.name,
        'type': loc.location_type,
        'latitude': loc.latitude,
        'longitude': loc.longitude,
        'description': loc.description,
        'source': 'student_suggested',
    } for loc in locations]
    return Response({'locations': data})


# ─────────────────────────────────────────────────────────────────────────────
# ITEM 5: AUTO-LOG POST LOCATION FOR ADMIN REVIEW
# ─────────────────────────────────────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def report_post_location(request):
    """
    Called silently when a student creates a post.
    If their GPS is on campus but 30m+ from any known node,
    it gets logged for admin review.
    POST /api/navigation/report-post-location/
    Body: { latitude, longitude }
    """
    try:
        lat = float(request.data.get('latitude'))
        lon = float(request.data.get('longitude'))
    except (TypeError, ValueError):
        return Response({'error': 'Valid latitude and longitude required.'}, status=400)

    # Only log if on campus
    on_campus = (
        6.6895 <= lat <= 6.6925 and
        -1.6120 <= lon <= -1.6080
    )
    if not on_campus:
        return Response({'message': 'Off campus — not logged.'})

    # Find nearest known node
    min_dist = float('inf')
    nearest_name = ''
    for _, row in NODES_DF.iterrows():
        d = _haversine_m(lat, lon, float(row['Latitude']), float(row['Longitude']))
        if d < min_dist:
            min_dist = d
            nearest_name = row['Name'].strip()

    # Only log if genuinely far from known nodes
    if min_dist <= 30:
        return Response({'message': f'Near known node "{nearest_name}" — not logged.'})

    # Check if this spot already exists (within 10m)
    for suggestion in PostLocationSuggestion.objects.filter(status='pending'):
        d = _haversine_m(lat, lon, suggestion.latitude, suggestion.longitude)
        if d <= 10:
            suggestion.occurrence_count += 1
            suggestion.save()
            return Response({
                'message': 'Location already tracked.',
                'occurrence_count': suggestion.occurrence_count,
            })

    # Create new suggestion
    PostLocationSuggestion.objects.create(
        submitted_by=request.user,
        latitude=lat,
        longitude=lon,
        distance_from_nearest_node=round(min_dist, 1),
        nearest_node_name=nearest_name,
    )

    return Response({'message': 'New campus spot detected and logged for admin review.'}, status=201)