from django.contrib import admin
from django.utils import timezone
from unfold.admin import ModelAdmin
from .models import Washroom, SuggestedLocation, PostLocationSuggestion


@admin.register(Washroom)
class WashroomAdmin(ModelAdmin):
    list_display = ['name', 'gender', 'latitude', 'longitude', 'is_active', 'created_at']
    list_filter = ['gender', 'is_active']
    search_fields = ['name', 'description']
    list_editable = ['is_active']
    fieldsets = (
        ('Location Info', {
            'fields': ('name', 'gender', 'description'),
        }),
        ('GPS Coordinates', {
            'fields': ('latitude', 'longitude'),
            'description': '💡 Long-press on Google Maps on campus to get coordinates.'
        }),
        ('Visibility', {
            'fields': ('is_active',),
        }),
    )


@admin.register(SuggestedLocation)
class SuggestedLocationAdmin(ModelAdmin):
    list_display = ['name', 'location_type', 'submitted_by', 'status', 'submitted_at']
    list_filter = ['status', 'location_type']
    search_fields = ['name', 'description', 'submitted_by__username']
    readonly_fields = ['submitted_by', 'submitted_at', 'reviewed_by', 'reviewed_at']
    list_editable = ['status']

    fieldsets = (
        ('Submitted Location', {
            'fields': ('name', 'location_type', 'description', 'latitude', 'longitude'),
        }),
        ('Submission Info', {
            'fields': ('submitted_by', 'submitted_at'),
        }),
        ('Admin Review', {
            'fields': ('status', 'admin_note', 'reviewed_by', 'reviewed_at'),
            'description': (
                '✅ Set status to Approved to make this location visible on the map. '
                'Add a note if rejecting.'
            ),
        }),
    )

    actions = ['approve_locations', 'reject_locations']

    def approve_locations(self, request, queryset):
        updated = queryset.update(
            status='approved',
            reviewed_by=request.user,
            reviewed_at=timezone.now()
        )
        self.message_user(request, f'{updated} location(s) approved.')
    approve_locations.short_description = '✅ Approve selected locations'

    def reject_locations(self, request, queryset):
        updated = queryset.update(
            status='rejected',
            reviewed_by=request.user,
            reviewed_at=timezone.now()
        )
        self.message_user(request, f'{updated} location(s) rejected.')
    reject_locations.short_description = '❌ Reject selected locations'

    def save_model(self, request, obj, form, change):
        if change and obj.status in ('approved', 'rejected') and not obj.reviewed_by:
            obj.reviewed_by = request.user
            obj.reviewed_at = timezone.now()
        super().save_model(request, obj, form, change)


@admin.register(PostLocationSuggestion)
class PostLocationSuggestionAdmin(ModelAdmin):
    list_display = [
        'coordinates', 'nearest_node_name', 'distance_from_nearest_node',
        'occurrence_count', 'submitted_by', 'status', 'first_seen'
    ]
    list_filter = ['status']
    search_fields = ['nearest_node_name', 'suggested_name', 'submitted_by__username']
    readonly_fields = [
        'submitted_by', 'latitude', 'longitude',
        'distance_from_nearest_node', 'nearest_node_name',
        'occurrence_count', 'first_seen', 'last_seen'
    ]
    list_editable = ['status']

    fieldsets = (
        ('Auto-Detected Location', {
            'fields': (
                'latitude', 'longitude',
                'nearest_node_name', 'distance_from_nearest_node',
                'occurrence_count', 'submitted_by', 'first_seen', 'last_seen'
            ),
        }),
        ('Admin Review', {
            'fields': ('status', 'suggested_name', 'admin_note'),
            'description': (
                '📍 Fill in "Suggested name" and set status to Approved '
                'to add this spot to the campus map.'
            ),
        }),
    )

    actions = ['approve_suggestions', 'reject_suggestions']

    def coordinates(self, obj):
        return f"({obj.latitude:.5f}, {obj.longitude:.5f})"
    coordinates.short_description = 'GPS Coordinates'

    def approve_suggestions(self, request, queryset):
        queryset.update(status='approved')
        self.message_user(request, f'{queryset.count()} suggestion(s) approved.')
    approve_suggestions.short_description = '✅ Approve selected suggestions'

    def reject_suggestions(self, request, queryset):
        queryset.update(status='rejected')
        self.message_user(request, f'{queryset.count()} suggestion(s) rejected.')
    reject_suggestions.short_description = '❌ Reject selected suggestions'