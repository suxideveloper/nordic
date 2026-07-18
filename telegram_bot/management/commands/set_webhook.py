"""
Telegram bot webhook management commands.

Foydalanish:
    python manage.py set_webhook          — webhook o'rnatish
    python manage.py set_webhook --delete — webhook o'chirish
    python manage.py set_webhook --info   — webhook holati
"""

import asyncio
import hashlib

from django.conf import settings
from django.core.management.base import BaseCommand


def get_webhook_path() -> str:
    token = settings.TELEGRAM_BOT_TOKEN
    return hashlib.sha256(token.encode()).hexdigest()[:32]


class Command(BaseCommand):
    help = 'Telegram bot webhook ni o\'rnatadi yoki o\'chiradi'

    def add_arguments(self, parser):
        parser.add_argument(
            '--delete',
            action='store_true',
            help='Webhook ni o\'chiradi',
        )
        parser.add_argument(
            '--info',
            action='store_true',
            help='Webhook haqida ma\'lumot ko\'rsatadi',
        )

    def handle(self, *args, **options):
        asyncio.run(self._handle_async(*args, **options))

    async def _handle_async(self, *args, **options):
        from telegram import Bot
        token = settings.TELEGRAM_BOT_TOKEN
        bot = Bot(token=token)

        if options['info']:
            info = await bot.get_webhook_info()
            self.stdout.write(self.style.SUCCESS("📋 Webhook ma'lumotlari:"))
            self.stdout.write(f"  URL:              {info.url or '(o\'rnatilmagan)'}")
            self.stdout.write(f"  Pending updates:  {info.pending_update_count}")
            self.stdout.write(f"  Last error:       {info.last_error_message or '(yo\'q)'}")
            return

        if options['delete']:
            await bot.delete_webhook(drop_pending_updates=True)
            self.stdout.write(self.style.SUCCESS(
                "🗑️  Webhook o'chirildi. Bot endi polling rejimida ishlamaydi."
            ))
            return

        # Webhook o'rnatish
        host = getattr(settings, 'TELEGRAM_WEBHOOK_HOST', None)
        if not host:
            self.stderr.write(self.style.ERROR(
                "❌ settings.py da TELEGRAM_WEBHOOK_HOST belgilanmagan!\n"
                "   Misol: TELEGRAM_WEBHOOK_HOST = 'https://yourdomain.com'"
            ))
            return

        if not host.startswith('https://'):
            self.stderr.write(self.style.ERROR(
                f"❌ Webhook faqat HTTPS URL bilan ishlaydi!\n"
                f"   Siz kiritdingiz: {host}\n"
                f"   Development uchun ngrok ishlating: ngrok http 8000"
            ))
            return

        path = get_webhook_path()
        webhook_url = f"{host.rstrip('/')}/telegram/webhook/{path}/"

        await bot.set_webhook(
            url=webhook_url,
            drop_pending_updates=True,
        )

        self.stdout.write(self.style.SUCCESS(
            f"✅ Webhook muvaffaqiyatli o'rnatildi!\n"
            f"   URL: {webhook_url}"
        ))
