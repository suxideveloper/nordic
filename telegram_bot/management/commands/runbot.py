"""
python manage.py runbot          — polling rejimida bot (development)
python manage.py set_webhook     — webhook o'rnatish (production)
"""

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Telegram botni polling rejimida ishga tushiradi (development uchun)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS(
            '🤖 Nordic University Telegram Bot (polling) ishga tushmoqda...\n'
            'ℹ️  Bu development uchun. Production da: python manage.py set_webhook'
        ))
        from telegram_bot.bot import get_application
        app = get_application()
        self.stdout.write(self.style.SUCCESS(
            "✅ Bot ulandi! To'xtatish uchun Ctrl+C bosing."
        ))
        app.run_polling(drop_pending_updates=True)
