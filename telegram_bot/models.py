from django.db import models


class TelegramSubscriber(models.Model):
    """Tracks users who subscribed to the bot for push notifications."""
    chat_id = models.BigIntegerField(unique=True)
    username = models.CharField(max_length=100, blank=True)
    first_name = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Telegram Subscriber'
        verbose_name_plural = 'Telegram Subscribers'

    def __str__(self):
        return f"@{self.username or self.first_name} ({self.chat_id})"
