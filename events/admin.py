from django.contrib import admin
from django.contrib import messages
from django.utils import timezone
from django.utils.html import format_html, mark_safe
from .models import Event, EventCategory


# ─── Shared admin action ──────────────────────────────────

@admin.action(description='✅ Mark selected as Published')
def make_published(modeladmin, request, queryset):
    updated = queryset.update(is_published=True)
    modeladmin.message_user(request, f'{updated} event(s) published.', messages.SUCCESS)


@admin.action(description='🚫 Mark selected as Unpublished')
def make_unpublished(modeladmin, request, queryset):
    updated = queryset.update(is_published=False)
    modeladmin.message_user(request, f'{updated} event(s) unpublished.', messages.WARNING)


# ─── Event Category ───────────────────────────────────────

@admin.register(EventCategory)
class EventCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'icon', 'color_preview']
    prepopulated_fields = {'slug': ('name',)}

    def color_preview(self, obj):
        return format_html(
            '<span style="display:inline-block;width:20px;height:20px;'
            'border-radius:4px;background:{};border:1px solid #ccc;"></span>',
            obj.color
        )
    color_preview.short_description = 'Color'


# ─── Event ────────────────────────────────────────────────

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = [
        'cover_thumb', 'title', 'category', 'organizer',
        'start_date', 'format_badge', 'is_published', 'is_featured', 'views_count'
    ]
    list_display_links = ['title']   # ← click title to edit
    list_filter = ['is_published', 'is_featured', 'format', 'category', 'organizer']
    search_fields = ['title', 'short_description']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['is_published', 'is_featured']
    date_hierarchy = 'start_date'
    readonly_fields = ['cover_thumb_large', 'views_count', 'created_at', 'updated_at']
    actions = [make_published, make_unpublished]

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'category', 'organizer',
                       'short_description', 'description')
        }),
        ('Cover Image', {
            'fields': ('cover_image', 'cover_thumb_large'),
        }),
        ('Date & Location', {
            'fields': ('start_date', 'end_date', 'location', 'format')
        }),
        ('Registration', {
            'fields': ('registration_url', 'seats_available', 'is_free', 'price')
        }),
        ('Publishing', {
            'fields': ('is_published', 'is_featured', 'tags')
        }),
        ('Stats', {
            'fields': ('views_count', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def cover_thumb(self, obj):
        if obj.cover_image:
            return format_html(
                '<img src="{}" style="height:40px;width:64px;object-fit:cover;'
                'border-radius:4px;" />',
                obj.cover_image.url
            )
        return '—'
    cover_thumb.short_description = ''

    def cover_thumb_large(self, obj):
        if obj.cover_image:
            return format_html(
                '<img src="{}" style="max-height:180px;max-width:360px;'
                'object-fit:cover;border-radius:8px;margin-top:8px;" />',
                obj.cover_image.url
            )
        return mark_safe('<span style="color:#aaa;">No image uploaded.</span>')
    cover_thumb_large.short_description = 'Preview'

    def format_badge(self, obj):
        colors = {'online': '#00D4AA', 'offline': '#6C63FF', 'hybrid': '#FFD166'}
        color = colors.get(obj.format, '#aaa')
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;'
            'border-radius:10px;font-size:0.75rem;">{}</span>',
            color, obj.get_format_display()
        )
    format_badge.short_description = 'Format'
