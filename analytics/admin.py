from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import PageVisit


@admin.register(PageVisit)
class PageVisitAdmin(admin.ModelAdmin):
    list_display = [
        'page_name', 'path_short', 'visited_at',
        'time_spent_badge', 'ip_address', 'is_bot'
    ]
    list_filter = ['is_bot', 'visited_at', 'page_name']
    search_fields = ['path', 'page_name', 'ip_address', 'session_key']
    readonly_fields = [
        'path', 'page_name', 'session_key', 'ip_address',
        'user_agent', 'referrer', 'time_spent', 'visited_at',
        'left_at', 'is_bot'
    ]
    date_hierarchy = 'visited_at'
    ordering = ['-visited_at']

    def path_short(self, obj):
        if len(obj.path) > 45:
            return obj.path[:45] + '…'
        return obj.path
    path_short.short_description = 'Path'

    def time_spent_badge(self, obj):
        s = obj.time_spent
        if s == 0:
            color = '#6c757d'
            label = '—'
        elif s < 30:
            color = '#dc3545'
            label = obj.time_spent_display
        elif s < 120:
            color = '#fd7e14'
            label = obj.time_spent_display
        elif s < 300:
            color = '#198754'
            label = obj.time_spent_display
        else:
            color = '#0d6efd'
            label = obj.time_spent_display
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;'
            'border-radius:12px;font-size:0.78rem;font-weight:600;">{}</span>',
            color, label
        )
    time_spent_badge.short_description = 'Time Spent'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
