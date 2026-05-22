"""
Admin statistics views — powers the dashboard charts.
These are staff-only endpoints, not exposed to regular users.
"""
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count
from django.db.models.functions import TruncMonth, TruncDay
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.http import JsonResponse
from datetime import timedelta

from django.contrib.auth import get_user_model
from .models import Post

User = get_user_model()


@staff_member_required
def stats_json(request):
    """
    Returns all dashboard stats as JSON for the Chart.js graphs.
    GET /admin/stats-json/
    """
    now = timezone.now()
    twelve_months_ago = now - timedelta(days=365)
    thirty_days_ago = now - timedelta(days=30)

    # ── Monthly signups (last 12 months) ──
    monthly_signups = (
        User.objects
        .filter(date_joined__gte=twelve_months_ago)
        .annotate(month=TruncMonth('date_joined'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )
    signup_labels = [entry['month'].strftime('%b %Y') for entry in monthly_signups]
    signup_data = [entry['count'] for entry in monthly_signups]

    # ── Monthly posts (last 12 months) ──
    monthly_posts = (
        Post.objects
        .filter(created_at__gte=twelve_months_ago)
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )
    post_labels = [entry['month'].strftime('%b %Y') for entry in monthly_posts]
    post_data = [entry['count'] for entry in monthly_posts]

    # ── Daily signups (last 30 days) ──
    daily_signups = (
        User.objects
        .filter(date_joined__gte=thirty_days_ago)
        .annotate(day=TruncDay('date_joined'))
        .values('day')
        .annotate(count=Count('id'))
        .order_by('day')
    )
    daily_labels = [entry['day'].strftime('%d %b') for entry in daily_signups]
    daily_data = [entry['count'] for entry in daily_signups]

    # ── Summary cards ──
    total_users = User.objects.count()
    total_posts = Post.objects.count()
    new_users_30d = User.objects.filter(date_joined__gte=thirty_days_ago).count()
    new_posts_30d = Post.objects.filter(created_at__gte=thirty_days_ago).count()
    active_users = User.objects.filter(is_active=True).count()

    # ── Navigation suggestions pending ──
    try:
        from navigation.models import SuggestedLocation, PostLocationSuggestion
        pending_locations = SuggestedLocation.objects.filter(status='pending').count()
        pending_post_locations = PostLocationSuggestion.objects.filter(status='pending').count()
    except Exception:
        pending_locations = 0
        pending_post_locations = 0

    return JsonResponse({
        'summary': {
            'total_users': total_users,
            'total_posts': total_posts,
            'new_users_30d': new_users_30d,
            'new_posts_30d': new_posts_30d,
            'active_users': active_users,
            'pending_locations': pending_locations,
            'pending_post_locations': pending_post_locations,
        },
        'monthly_signups': {
            'labels': signup_labels,
            'data': signup_data,
        },
        'monthly_posts': {
            'labels': post_labels,
            'data': post_data,
        },
        'daily_signups': {
            'labels': daily_labels,
            'data': daily_data,
        },
    })