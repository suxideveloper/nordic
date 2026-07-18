"""
Auto-notify Telegram subscribers when new Event/Vacancy/Internship/Grant is published.
"""
import asyncio
import logging
import threading
from django.db.models.signals import post_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)


def _notify_all(text: str):
    """Send a message to all active subscribers (synchronous wrapper).

    Alohida threadda yangi event loop ochib ishlatiladi,
    chunki bot allaqachon o'z event loop'ini ishlatmoqda.
    asyncio.run() bot loop'i bilan konflikt qilmasligi uchun
    threading ishlatiladi.
    """
    def run_in_thread():
        try:
            from django.conf import settings
            from telegram import Bot
            from telegram_bot.models import TelegramSubscriber

            subscribers = list(TelegramSubscriber.objects.filter(is_active=True))
            if not subscribers:
                return

            bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)

            async def _send():
                async with bot:
                    for sub in subscribers:
                        try:
                            await bot.send_message(
                                chat_id=sub.chat_id,
                                text=text,
                                parse_mode='Markdown',
                                disable_web_page_preview=True
                            )
                        except Exception as e:
                            logger.warning(f"Notify failed for {sub.chat_id}: {e}")

            # Yangi, mustaqil event loop — bot loop'i bilan konflikt yo'q
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(_send())
            finally:
                loop.close()

        except Exception as e:
            logger.error(f"Signal notify error: {e}")

    # Background threadda ishga tushir — Django request'ini bloklamaydi
    t = threading.Thread(target=run_in_thread, daemon=True)
    t.start()


@receiver(post_save, sender='events.Event')
def notify_new_event(sender, instance, created, **kwargs):
    if created and instance.is_published:
        from django.conf import settings
        site = getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000')
        text = (
            f"📅 *Yangi tadbir!*\n\n"
            f"*{instance.title}*\n"
            f"📆 {instance.start_date.strftime('%d.%m.%Y %H:%M')}\n"
            f"{'📍 ' + instance.location + chr(10) if instance.location else ''}"
            f"{'🆓 Bepul' if instance.is_free else '💳 Pullik'}\n\n"
            f"🔗 [Batafsil]({site}/events/{instance.slug}/)"
        )
        _notify_all(text)


@receiver(post_save, sender='opportunities.Vacancy')
def notify_new_vacancy(sender, instance, created, **kwargs):
    if created and instance.is_active:
        from django.conf import settings
        site = getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000')
        text = (
            f"💼 *Yangi vakansiya!*\n\n"
            f"*{instance.title}*\n"
            f"🏢 {instance.partner.name}\n"
            f"📋 {instance.get_employment_type_display()}\n"
            f"💰 {instance.salary_display()}\n\n"
            f"🔗 [Ko'rish]({site}/opportunities/vacancies/{instance.slug}/)"
        )
        _notify_all(text)


@receiver(post_save, sender='opportunities.Internship')
def notify_new_internship(sender, instance, created, **kwargs):
    if created and instance.is_active:
        from django.conf import settings
        site = getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000')
        paid = "✅ Haq to'lanadi" if instance.is_paid else "🔶 Haqi yo'q"
        text = (
            f"💻 *Yangi stajirovka!*\n\n"
            f"*{instance.title}*\n"
            f"🏢 {instance.partner.name}\n"
            f"⏳ {instance.get_duration_display()}  |  {paid}\n\n"
            f"🔗 [Ko'rish]({site}/opportunities/internships/{instance.slug}/)"
        )
        _notify_all(text)


@receiver(post_save, sender='opportunities.Grant')
def notify_new_grant(sender, instance, created, **kwargs):
    if created and instance.is_active:
        from django.conf import settings
        site = getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000')
        funded = "🌟 To'liq moliyalashtiriladi!" if instance.is_fully_funded else instance.amount_display()
        text = (
            f"🏆 *Yangi grant!*\n\n"
            f"*{instance.title}*\n"
            f"🏢 {instance.partner.name}\n"
            f"{'🌍 ' + instance.country + chr(10) if instance.country else ''}"
            f"💰 {funded}\n\n"
            f"🔗 [Ko'rish]({site}/opportunities/grants/{instance.slug}/)"
        )
        _notify_all(text)
