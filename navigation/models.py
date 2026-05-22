from django.db import models
from django.conf import settings


class Washroom(models.Model):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('unisex', 'Unisex'),
    ]
    name = models.CharField(max_length=255, help_text="e.g. 'Engineering Block Washroom'")
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='unisex')
    latitude = models.FloatField()
    longitude = models.FloatField()
    description = models.TextField(blank=True, help_text="Optional notes e.g. 'Ground floor, near main entrance'")
    is_active = models.BooleanField(default=True, help_text="Uncheck to hide from app without deleting")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.get_gender_display()})"

    class Meta:
        ordering = ['name']


# ─── Item 4: Student-submitted map locations ───────────────────────────────
class SuggestedLocation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    TYPE_CHOICES = [
        ('building', 'Building'),
        ('gate', 'Gate'),
        ('hostel', 'Hostel'),
        ('sport', 'Sports Facility'),
        ('atm', 'ATM'),
        ('park', 'Parking'),
        ('other', 'Other'),
    ]

    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='suggested_locations'
    )
    name = models.CharField(max_length=255)
    location_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='other')
    latitude = models.FloatField()
    longitude = models.FloatField()
    description = models.TextField(blank=True, help_text="Any extra details about this location")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    # Admin fields
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='reviewed_locations'
    )
    admin_note = models.TextField(blank=True, help_text="Optional note from admin on approval/rejection")
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} [{self.status}] by {self.submitted_by}"

    class Meta:
        ordering = ['-submitted_at']
        verbose_name = 'Suggested Location'
        verbose_name_plural = 'Suggested Locations'


# ─── Item 5: Post location submissions ────────────────────────────────────
class PostLocationSuggestion(models.Model):
    """
    Auto-created when a student posts from a GPS location that isn't
    in the campus map yet. Admin can approve to add it to the map.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='post_location_suggestions'
    )
    latitude = models.FloatField()
    longitude = models.FloatField()
    # How far from nearest known node (metres)
    distance_from_nearest_node = models.FloatField(default=0)
    nearest_node_name = models.CharField(max_length=255, blank=True)
    # How many times this spot has been posted from
    occurrence_count = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    suggested_name = models.CharField(
        max_length=255, blank=True,
        help_text="Admin can fill this when approving"
    )
    admin_note = models.TextField(blank=True)
    first_seen = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Post location ({self.latitude:.4f}, {self.longitude:.4f}) x{self.occurrence_count} [{self.status}]"

    class Meta:
        ordering = ['-occurrence_count', '-first_seen']
        verbose_name = 'Post Location Suggestion'
        verbose_name_plural = 'Post Location Suggestions'