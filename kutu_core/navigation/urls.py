from django.urls import path
from . import views

urlpatterns = [
    # Core navigation
    path('locations/', views.get_locations, name='nav_locations'),
    path('route/', views.get_route, name='nav_route'),
    path('search/', views.search_locations, name='nav_search'),
    path('nearest-gate/', views.nearest_gate, name='nav_nearest_gate'),
    path('gates/', views.get_gates, name='nav_gates'),

    # Washrooms (Item 2)
    path('washrooms/nearby/', views.nearby_washrooms, name='nav_nearby_washrooms'),
    path('washrooms/', views.all_washrooms, name='nav_all_washrooms'),

    # Item 4: Student-suggested locations
    path('suggest-location/', views.suggest_location, name='nav_suggest_location'),
    path('suggest-location/mine/', views.my_suggested_locations, name='nav_my_suggestions'),
    path('suggest-location/approved/', views.approved_suggested_locations, name='nav_approved_suggestions'),

    # Item 5: Auto-log post locations
    path('report-post-location/', views.report_post_location, name='nav_report_post_location'),
]