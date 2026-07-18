from django.contrib import admin
from django.utils.html import format_html, mark_safe
from .models import Partner, SiteSettings


@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ['logo_preview', 'name', 'website', 'is_active', 'created_at']
    list_display_links = ['name']   # ← name is clickable → opens edit form
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    list_editable = ['is_active']
    readonly_fields = ['logo_preview_large', 'created_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'website', 'description', 'is_active')
        }),
        ('Logo', {
            'fields': ('logo', 'logo_preview_large'),
            'description': 'Upload a transparent PNG or SVG logo. Recommended size: 300×150px.',
        }),
    )

    def logo_preview(self, obj):
        """Small thumbnail in the list view."""
        if obj.logo:
            return format_html(
                '<img src="{}" style="height:36px;max-width:90px;'
                'object-fit:contain;border-radius:4px;'
                'background:#f8f9fa;padding:2px;" />',
                obj.logo.url
            )
        return mark_safe('<span style="color:#aaa;font-size:0.8rem;">No logo</span>')
    logo_preview.short_description = 'Logo'

    def logo_preview_large(self, obj):
        """Large preview inside the edit form."""
        if obj.logo:
            return format_html(
                '<div style="background:#1a1a2e;padding:16px;border-radius:8px;'
                'display:inline-block;margin-top:8px;">'
                '<img src="{}" style="max-height:80px;max-width:240px;'
                'object-fit:contain;" />'
                '</div>',
                obj.logo.url
            )
        return mark_safe('<span style="color:#aaa;">No logo uploaded yet.</span>')
    logo_preview_large.short_description = 'Current Logo Preview'


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('University Info', {
            'fields': ('university_name', 'tagline', 'logo')
        }),
        ('Contact', {
            'fields': ('contact_email', 'contact_phone', 'address')
        }),
        ('Social Media', {
            'fields': ('instagram', 'telegram', 'linkedin', 'facebook')
        }),
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()
