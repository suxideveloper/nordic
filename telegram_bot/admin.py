from django.contrib import admin
from .models import TelegramSubscriber


@admin.register(TelegramSubscriber)
class TelegramSubscriberAdmin(admin.ModelAdmin):
    list_display = ['chat_id', 'username', 'first_name', 'is_active', 'subscribed_at']
    list_filter = ['is_active']
    search_fields = ['username', 'first_name']
    list_editable = ['is_active']
    readonly_fields = ['subscribed_at']
