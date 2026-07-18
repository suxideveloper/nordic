from django.contrib import admin
from django.contrib import messages
from django.core.management import call_command
from django.utils.html import format_html, mark_safe
from .models import (
    Vacancy, VacancyCategory,
    Internship,
    Grant, GrantCategory
)


# ─── Global cleanup action ────────────────────────────────

@admin.action(description='🧹 Run cleanup: delete all expired records')
def run_cleanup(modeladmin, request, queryset):
    from io import StringIO
    out = StringIO()
    call_command('cleanup_expired', grace_days=0, stdout=out)
    modeladmin.message_user(request, '✅ Cleanup complete. Expired records deleted.', messages.SUCCESS)


# ─── Vacancy Category ─────────────────────────────────────

@admin.register(VacancyCategory)
class VacancyCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'icon']
    prepopulated_fields = {'slug': ('name',)}


# ─── Vacancy ──────────────────────────────────────────────

@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = [
        'cover_thumb', 'title', 'partner_logo', 'category',
        'employment_type', 'salary_info', 'deadline_badge', 'is_active', 'is_featured'
    ]
    list_display_links = ['title']   # ← click title to edit
    list_filter = ['is_active', 'is_featured', 'employment_type', 'category', 'partner']
    search_fields = ['title', 'short_description', 'partner__name']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['is_active', 'is_featured']
    readonly_fields = ['cover_thumb_large', 'views_count', 'created_at', 'updated_at']
    actions = [run_cleanup]

    fieldsets = (
        ('Basic Info', {
            'fields': ('title', 'slug', 'partner', 'category',
                       'short_description', 'description')
        }),
        ('Cover Image', {'fields': ('cover_image', 'cover_thumb_large')}),
        ('Job Details', {
            'fields': ('employment_type', 'location', 'salary_min',
                       'salary_max', 'salary_currency', 'is_for_students')
        }),
        ('Requirements', {'fields': ('requirements',)}),
        ('Publishing', {'fields': ('is_active', 'is_featured', 'deadline', 'apply_url', 'tags')}),
        ('Stats', {'fields': ('views_count', 'created_at', 'updated_at'), 'classes': ('collapse',)}),
    )

    def cover_thumb(self, obj):
        if obj.cover_image:
            return format_html(
                '<img src="{}" style="height:36px;width:56px;object-fit:cover;border-radius:4px;" />',
                obj.cover_image.url)
        return '—'
    cover_thumb.short_description = ''

    def cover_thumb_large(self, obj):
        if obj.cover_image:
            return format_html(
                '<img src="{}" style="max-height:160px;max-width:320px;'
                'object-fit:cover;border-radius:8px;margin-top:8px;" />',
                obj.cover_image.url)
        return mark_safe('<span style="color:#aaa;">No image.</span>')
    cover_thumb_large.short_description = 'Preview'

    def partner_logo(self, obj):
        if obj.partner.logo:
            return format_html(
                '<img src="{}" style="height:28px;max-width:72px;'
                'object-fit:contain;border-radius:3px;" title="{}" />',
                obj.partner.logo.url, obj.partner.name)
        return format_html('<span style="color:#aaa;font-size:0.8rem;">{}</span>', obj.partner.name)
    partner_logo.short_description = 'Partner'

    def salary_info(self, obj):
        return obj.salary_display()
    salary_info.short_description = 'Salary'

    def deadline_badge(self, obj):
        if not obj.deadline:
            return '—'
        from datetime import date
        today = date.today()
        delta = (obj.deadline - today).days
        if delta < 0:
            color, label = '#dc3545', f'Expired ({obj.deadline})'
        elif delta <= 7:
            color, label = '#fd7e14', f'{delta}d left'
        else:
            color, label = '#198754', str(obj.deadline)
        return format_html(
            '<span style="color:{};font-weight:600;font-size:0.8rem;">{}</span>',
            color, label)
    deadline_badge.short_description = 'Deadline'


# ─── Internship ───────────────────────────────────────────

@admin.register(Internship)
class InternshipAdmin(admin.ModelAdmin):
    list_display = [
        'cover_thumb', 'title', 'partner_logo',
        'duration', 'paid_badge', 'deadline_badge', 'is_active', 'is_featured'
    ]
    list_display_links = ['title']   # ← click title to edit
    list_filter = ['is_active', 'is_featured', 'is_paid', 'duration', 'partner']
    search_fields = ['title', 'short_description', 'partner__name']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['is_active', 'is_featured']
    readonly_fields = ['cover_thumb_large', 'views_count', 'created_at', 'updated_at']
    actions = [run_cleanup]

    fieldsets = (
        ('Basic Info', {'fields': ('title', 'slug', 'partner', 'short_description', 'description')}),
        ('Cover Image', {'fields': ('cover_image', 'cover_thumb_large')}),
        ('Internship Details', {
            'fields': ('location', 'duration', 'start_date',
                       'field_of_study', 'is_paid', 'stipend', 'stipend_currency')
        }),
        ('Publishing', {'fields': ('is_active', 'is_featured', 'deadline', 'apply_url', 'tags')}),
        ('Stats', {'fields': ('views_count', 'created_at', 'updated_at'), 'classes': ('collapse',)}),
    )

    def cover_thumb(self, obj):
        if obj.cover_image:
            return format_html(
                '<img src="{}" style="height:36px;width:56px;object-fit:cover;border-radius:4px;" />',
                obj.cover_image.url)
        return '—'
    cover_thumb.short_description = ''

    def cover_thumb_large(self, obj):
        if obj.cover_image:
            return format_html(
                '<img src="{}" style="max-height:160px;max-width:320px;'
                'object-fit:cover;border-radius:8px;margin-top:8px;" />',
                obj.cover_image.url)
        return mark_safe('<span style="color:#aaa;">No image.</span>')
    cover_thumb_large.short_description = 'Preview'

    def partner_logo(self, obj):
        if obj.partner.logo:
            return format_html(
                '<img src="{}" style="height:28px;max-width:72px;object-fit:contain;" title="{}" />',
                obj.partner.logo.url, obj.partner.name)
        return format_html('<span style="color:#aaa;font-size:0.8rem;">{}</span>', obj.partner.name)
    partner_logo.short_description = 'Partner'

    def paid_badge(self, obj):
        if obj.is_paid:
            return mark_safe('<span style="color:#198754;font-weight:600;">✅ Paid</span>')
        return mark_safe('<span style="color:#aaa;">Unpaid</span>')
    paid_badge.short_description = 'Paid'

    def deadline_badge(self, obj):
        if not obj.deadline:
            return '—'
        from datetime import date
        delta = (obj.deadline - date.today()).days
        color = '#dc3545' if delta < 0 else ('#fd7e14' if delta <= 7 else '#198754')
        label = f'Expired' if delta < 0 else (f'{delta}d left' if delta <= 7 else str(obj.deadline))
        return format_html('<span style="color:{};font-weight:600;font-size:0.8rem;">{}</span>', color, label)
    deadline_badge.short_description = 'Deadline'


# ─── Grant Category ───────────────────────────────────────

@admin.register(GrantCategory)
class GrantCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'icon']
    prepopulated_fields = {'slug': ('name',)}


# ─── Grant ────────────────────────────────────────────────

@admin.register(Grant)
class GrantAdmin(admin.ModelAdmin):
    list_display = [
        'cover_thumb', 'title', 'partner_logo', 'grant_type',
        'amount_info', 'country', 'deadline_badge', 'is_active', 'is_featured'
    ]
    list_display_links = ['title']   # ← click title to edit
    list_filter = ['is_active', 'is_featured', 'grant_type', 'is_fully_funded', 'partner']
    search_fields = ['title', 'short_description', 'partner__name', 'country']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['is_active', 'is_featured']
    readonly_fields = ['cover_thumb_large', 'views_count', 'created_at', 'updated_at']
    actions = [run_cleanup]

    fieldsets = (
        ('Basic Info', {
            'fields': ('title', 'slug', 'partner', 'category',
                       'short_description', 'description')
        }),
        ('Cover Image', {'fields': ('cover_image', 'cover_thumb_large')}),
        ('Grant Details', {
            'fields': ('grant_type', 'amount', 'currency',
                       'is_fully_funded', 'country', 'eligibility')
        }),
        ('Publishing', {'fields': ('is_active', 'is_featured', 'deadline', 'apply_url', 'tags')}),
        ('Stats', {'fields': ('views_count', 'created_at', 'updated_at'), 'classes': ('collapse',)}),
    )

    def cover_thumb(self, obj):
        if obj.cover_image:
            return format_html(
                '<img src="{}" style="height:36px;width:56px;object-fit:cover;border-radius:4px;" />',
                obj.cover_image.url)
        return '—'
    cover_thumb.short_description = ''

    def cover_thumb_large(self, obj):
        if obj.cover_image:
            return format_html(
                '<img src="{}" style="max-height:160px;max-width:320px;'
                'object-fit:cover;border-radius:8px;margin-top:8px;" />',
                obj.cover_image.url)
        return format_html('<span style="color:#aaa;">No image.</span>')
    cover_thumb_large.short_description = 'Preview'

    def partner_logo(self, obj):
        if obj.partner.logo:
            return format_html(
                '<img src="{}" style="height:28px;max-width:72px;object-fit:contain;" title="{}" />',
                obj.partner.logo.url, obj.partner.name)
        return format_html('<span style="color:#aaa;font-size:0.8rem;">{}</span>', obj.partner.name)
    partner_logo.short_description = 'Partner'

    def amount_info(self, obj):
        return obj.amount_display()
    amount_info.short_description = 'Amount'

    def deadline_badge(self, obj):
        if not obj.deadline:
            return '—'
        from datetime import date
        delta = (obj.deadline - date.today()).days
        color = '#dc3545' if delta < 0 else ('#fd7e14' if delta <= 7 else '#198754')
        label = 'Expired' if delta < 0 else (f'{delta}d left' if delta <= 7 else str(obj.deadline))
        return format_html('<span style="color:{};font-weight:600;font-size:0.8rem;">{}</span>', color, label)
    deadline_badge.short_description = 'Deadline'
