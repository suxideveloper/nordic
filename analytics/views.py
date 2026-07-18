import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from django.db.models import Count, Avg, Sum, Q
from django.shortcuts import render
from datetime import timedelta
from .models import PageVisit


@csrf_exempt
@require_POST
def track_time_spent(request):
    """
    JS sends a ping when user leaves page with time_spent (seconds).
    Matches by session_key + path and updates the latest record.
    """
    try:
        data = json.loads(request.body)
        path = data.get('path', '')
        time_spent = int(data.get('time_spent', 0))
        session_key = request.session.session_key or ''

        if path and time_spent > 0 and session_key:
            # Update most recent visit for this session+path
            visit = PageVisit.objects.filter(
                path=path,
                session_key=session_key,
            ).order_by('-visited_at').first()

            if visit and visit.time_spent == 0:
                visit.time_spent = min(time_spent, 3600)  # cap at 1 hour
                visit.left_at = timezone.now()
                visit.save(update_fields=['time_spent', 'left_at'])

        return JsonResponse({'ok': True})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=400)


@staff_member_required
def analytics_dashboard(request):
    """Analytics dashboard for admin."""
    # Time range filter
    range_days = int(request.GET.get('days', 7))
    since = timezone.now() - timedelta(days=range_days)

    base_qs = PageVisit.objects.filter(visited_at__gte=since, is_bot=False)

    # ── Top Pages ──────────────────────────────────────────
    top_pages = (
        base_qs
        .values('path', 'page_name')
        .annotate(
            visits=Count('id'),
            avg_time=Avg('time_spent'),
            total_time=Sum('time_spent'),
        )
        .order_by('-visits')[:15]
    )

    # ── Daily Visits ────────────────────────────────────────
    from django.db.models.functions import TruncDate
    daily_visits = (
        base_qs
        .annotate(date=TruncDate('visited_at'))
        .values('date')
        .annotate(count=Count('id'))
        .order_by('date')
    )

    # ── Summary Stats ───────────────────────────────────────
    total_visits = base_qs.count()
    unique_sessions = base_qs.values('session_key').distinct().count()
    unique_ips = base_qs.values('ip_address').distinct().count()
    avg_time_overall = base_qs.aggregate(avg=Avg('time_spent'))['avg'] or 0

    # ── Recent Visits ────────────────────────────────────────
    recent_visits = base_qs.select_related().order_by('-visited_at')[:20]

    # ── Hourly distribution ──────────────────────────────────
    from django.db.models.functions import ExtractHour
    hourly = (
        base_qs
        .annotate(hour=ExtractHour('visited_at'))
        .values('hour')
        .annotate(count=Count('id'))
        .order_by('hour')
    )
    hourly_data = {h: 0 for h in range(24)}
    for item in hourly:
        hourly_data[item['hour']] = item['count']

    # Format for chart
    daily_labels = [str(d['date']) for d in daily_visits]
    daily_data = [d['count'] for d in daily_visits]

    context = {
        'title': 'Analytics Dashboard',
        'range_days': range_days,
        'total_visits': total_visits,
        'unique_sessions': unique_sessions,
        'unique_ips': unique_ips,
        'avg_time_overall': int(avg_time_overall),
        'top_pages': top_pages,
        'recent_visits': recent_visits,
        'daily_labels': json.dumps(daily_labels),
        'daily_data': json.dumps(daily_data),
        'hourly_labels': json.dumps(list(range(24))),
        'hourly_data': json.dumps([hourly_data[h] for h in range(24)]),
    }
    return render(request, 'analytics/dashboard.html', context)
