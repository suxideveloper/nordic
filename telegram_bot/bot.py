"""
Nordic University Tashkent — Telegram Bot (Webhook mode)
Barcha Django ORM chaqiruvlari sync_to_async bilan o'ralgan.
Polling yo'q — Telegram webhook orqali Django viewga POST yuboradi.
"""

import os
import logging
from datetime import date

from django.conf import settings
from asgiref.sync import sync_to_async
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler,
    ContextTypes, MessageHandler, filters, CallbackQueryHandler
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def get_site_url():
    return getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000')

# ─── Tugma matni konstantalari ────────────────────────────
BTN_EVENTS      = "📅 Tadbirlar"
BTN_VACANCIES   = "💼 Vakansiyalar"
BTN_INTERNSHIPS = "💻 Stajirovkalar"
BTN_GRANTS      = "🏆 Grantlar"
BTN_SUBSCRIBE   = "🔔 Obuna bo'lish"
BTN_UNSUBSCRIBE = "🔕 Obunani bekor qilish"
BTN_HELP        = "ℹ️ Yordam"


# ─── Klaviatura ───────────────────────────────────────────

def main_reply_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(BTN_EVENTS),      KeyboardButton(BTN_VACANCIES)],
            [KeyboardButton(BTN_INTERNSHIPS),  KeyboardButton(BTN_GRANTS)],
            [KeyboardButton(BTN_SUBSCRIBE),    KeyboardButton(BTN_HELP)],
        ],
        resize_keyboard=True,
        input_field_placeholder="Bo'limni tanlang...",
    )

def site_link_keyboard(label: str, path: str):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"🌐 {label}", url=f"{get_site_url()}{path}")]
    ])

import math

def get_pagination_keyboard(category: str, current_page: int, total_count: int, limit: int = 5, extra_url: str = None, url_text: str = None):
    total_pages = max(1, math.ceil(total_count / limit))
    buttons = []
    
    if total_pages > 1:
        prev_page = current_page - 1 if current_page > 1 else total_pages
        next_page = current_page + 1 if current_page < total_pages else 1
        
        buttons.append([
            InlineKeyboardButton("⬅️", callback_data=f"page_{category}_{prev_page}"),
            InlineKeyboardButton(f"{current_page}/{total_pages}", callback_data="ignore"),
            InlineKeyboardButton("➡️", callback_data=f"page_{category}_{next_page}")
        ])
        
    if extra_url and url_text:
        buttons.append([InlineKeyboardButton(f"🌐 {url_text}", url=f"{get_site_url()}{extra_url}")])
        
    return InlineKeyboardMarkup(buttons)


# ─── Yordamchi ───────────────────────────────────────────

def format_deadline(deadline):
    if not deadline:
        return "—"
    today = date.today()
    delta = (deadline - today).days
    if delta < 0:
        return "❌ Muddati o'tgan"
    elif delta == 0:
        return "⚠️ Bugun!"
    elif delta <= 7:
        return f"⚠️ {delta} kun qoldi ({deadline.strftime('%d.%m.%Y')})"
    return deadline.strftime('%d.%m.%Y')


# ─── DB funksiyalari (sync, keyin sync_to_async bilan chaqiriladi) ───────────

def _get_events(page=1, limit=5):
    from django.utils import timezone
    from events.models import Event
    qs = Event.objects.filter(
        is_published=True,
        start_date__gte=timezone.now()
    ).order_by('start_date')
    count = qs.count()
    offset = (page - 1) * limit
    return list(qs.select_related('organizer')[offset:offset+limit]), count

def _get_vacancies(page=1, limit=5):
    from opportunities.models import Vacancy
    qs = Vacancy.objects.filter(is_active=True).order_by('-created_at')
    count = qs.count()
    offset = (page - 1) * limit
    return list(qs.select_related('partner')[offset:offset+limit]), count

def _get_internships(page=1, limit=5):
    from opportunities.models import Internship
    qs = Internship.objects.filter(is_active=True).order_by('-created_at')
    count = qs.count()
    offset = (page - 1) * limit
    return list(qs.select_related('partner')[offset:offset+limit]), count

def _get_grants(page=1, limit=5):
    from opportunities.models import Grant
    qs = Grant.objects.filter(is_active=True).order_by('deadline')
    count = qs.count()
    offset = (page - 1) * limit
    return list(qs.select_related('partner')[offset:offset+limit]), count

def _subscribe_user(chat_id, username, first_name):
    from telegram_bot.models import TelegramSubscriber
    sub, created = TelegramSubscriber.objects.get_or_create(
        chat_id=chat_id,
        defaults={'username': username, 'first_name': first_name, 'is_active': True}
    )
    if not created and not sub.is_active:
        sub.is_active = True
        sub.username = username
        sub.first_name = first_name
        sub.save()
        return 'reactivated'
    return 'created' if created else 'exists'

def _unsubscribe_user(chat_id):
    from telegram_bot.models import TelegramSubscriber
    try:
        sub = TelegramSubscriber.objects.get(chat_id=chat_id)
        sub.is_active = False
        sub.save()
        return True
    except TelegramSubscriber.DoesNotExist:
        return False


# ─── /start ───────────────────────────────────────────────

LOGO_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'images', '123.png')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    caption = (
        f"👋 Assalomu alaykum, *{user.first_name}*!\n\n"
        f"🎓 *Nordic International University* — Talabalar portali botiga xush kelibsiz!\n\n"
        f"Bu bot orqali siz:\n"
        f"• 📅 Kelgusi tadbirlarni ko'rishingiz\n"
        f"• 💼 Ochiq vakansiyalarni topishingiz\n"
        f"• 💻 Stajirovka imkoniyatlarini bilishingiz\n"
        f"• 🏆 Grant va stipendiyalar haqida ma'lumot olishingiz\n\n"
        f"👇 Pastdagi tugmalardan birini bosing:"
    )
    try:
        with open(LOGO_PATH, 'rb') as logo_file:
            await update.message.reply_photo(
                photo=logo_file,
                caption=caption,
                parse_mode='Markdown',
                reply_markup=main_reply_keyboard()
            )
    except Exception as e:
        logger.warning(f"Logo yuborishda xato: {e}")
        await update.message.reply_text(
            caption, parse_mode='Markdown', reply_markup=main_reply_keyboard()
        )


# ─── Tadbirlar ────────────────────────────────────────────

async def events_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, page: int = 1, is_callback: bool = False):
    events, total_count = await sync_to_async(_get_events)(page=page)

    if not events:
        text = "📅 Hozircha kelgusi tadbirlar yo'q.\n\nTez orada yangilari e'lon qilinadi!"
        markup = site_link_keyboard("Barcha tadbirlar", "/events/")
    else:
        text = "📅 *Kelgusi tadbirlar:*\n\n"
        for e in events:
            fmt_emoji = {"online": "🌐", "offline": "📍", "hybrid": "🔀"}.get(e.format, "📍")
            free_label = "🆓 Bepul" if e.is_free else "💳 Pullik"
            text += (
                f"*{e.title}*\n"
                f"{fmt_emoji} {e.get_format_display()}  •  {free_label}\n"
                f"📆 {e.start_date.strftime('%d.%m.%Y %H:%M')}\n"
                f"{'📍 ' + e.location + chr(10) if e.location else ''}"
                f"🔗 [Batafsil]({get_site_url()}/events/{e.slug}/)\n"
                f"{'─' * 30}\n"
            )
        markup = get_pagination_keyboard("events", page, total_count, extra_url="/events/", url_text="Barcha tadbirlar")

    if is_callback:
        await update.callback_query.edit_message_text(text, parse_mode='Markdown', reply_markup=markup, disable_web_page_preview=True)
    else:
        await update.message.reply_text(text, parse_mode='Markdown', reply_markup=markup, disable_web_page_preview=True)


# ─── Vakansiyalar ─────────────────────────────────────────

async def vacancies_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, page: int = 1, is_callback: bool = False):
    vacancies, total_count = await sync_to_async(_get_vacancies)(page=page)

    if not vacancies:
        text = "💼 Hozircha ochiq vakansiyalar yo'q."
        markup = site_link_keyboard("Barcha vakansiyalar", "/opportunities/vacancies/")
    else:
        text = "💼 *Ochiq vakansiyalar:*\n\n"
        for v in vacancies:
            stud = "  •  🎓 Talabalar uchun" if v.is_for_students else ""
            text += (
                f"*{v.title}*\n"
                f"🏢 {v.partner.name if v.partner else 'Nordic University'}\n"
                f"{'📍 ' + v.location + chr(10) if v.location else ''}"
                f"📋 {v.get_employment_type_display()}{stud}\n"
                f"💰 {v.salary_display()}\n"
                f"⏰ Muddati: {format_deadline(v.deadline)}\n"
                f"🔗 [Ariza topshirish]({get_site_url()}/opportunities/vacancies/{v.slug}/)\n"
                f"{'─' * 30}\n"
            )
        markup = get_pagination_keyboard("vacancies", page, total_count, extra_url="/opportunities/vacancies/", url_text="Barcha vakansiyalar")

    if is_callback:
        await update.callback_query.edit_message_text(text, parse_mode='Markdown', reply_markup=markup, disable_web_page_preview=True)
    else:
        await update.message.reply_text(text, parse_mode='Markdown', reply_markup=markup, disable_web_page_preview=True)


# ─── Stajirovkalar ────────────────────────────────────────

async def internships_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, page: int = 1, is_callback: bool = False):
    internships, total_count = await sync_to_async(_get_internships)(page=page)

    if not internships:
        text = "💻 Hozircha faol stajirovkalar yo'q."
        markup = site_link_keyboard("Barcha stajirovkalar", "/opportunities/internships/")
    else:
        text = "💻 *Faol stajirovkalar:*\n\n"
        for i in internships:
            paid = "✅ Haq to'lanadi" if i.is_paid else "🔶 Haqi yo'q"
            text += (
                f"*{i.title}*\n"
                f"🏢 {i.partner.name}\n"
                f"⏳ {i.get_duration_display()}  •  {paid}\n"
                f"{'💵 ' + i.stipend_display() + chr(10) if i.is_paid else ''}"
                f"⏰ Muddati: {format_deadline(i.deadline)}\n"
                f"🔗 [Batafsil]({get_site_url()}/opportunities/internships/{i.slug}/)\n"
                f"{'─' * 30}\n"
            )
        markup = get_pagination_keyboard("internships", page, total_count, extra_url="/opportunities/internships/", url_text="Barcha stajirovkalar")

    if is_callback:
        await update.callback_query.edit_message_text(text, parse_mode='Markdown', reply_markup=markup, disable_web_page_preview=True)
    else:
        await update.message.reply_text(text, parse_mode='Markdown', reply_markup=markup, disable_web_page_preview=True)


# ─── Grantlar ─────────────────────────────────────────────

async def grants_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, page: int = 1, is_callback: bool = False):
    grants, total_count = await sync_to_async(_get_grants)(page=page)

    if not grants:
        text = "🏆 Hozircha faol grantlar yo'q."
        markup = site_link_keyboard("Barcha grantlar", "/opportunities/grants/")
    else:
        text = "🏆 *Grant va stipendiyalar:*\n\n"
        for g in grants:
            funded = "🌟 To'liq moliyalashtiriladi!" if g.is_fully_funded else g.amount_display()
            text += (
                f"*{g.title}*\n"
                f"🏢 {g.partner.name if g.partner else 'Nordic University'}\n"
                f"{'🌍 ' + g.country + chr(10) if g.country else ''}"
                f"📋 {g.get_grant_type_display()}  •  💰 {funded}\n"
                f"⏰ Muddati: {format_deadline(g.deadline)}\n"
                f"🔗 [Batafsil]({get_site_url()}/opportunities/grants/{g.slug}/)\n"
                f"{'─' * 30}\n"
            )
        markup = get_pagination_keyboard("grants", page, total_count, extra_url="/opportunities/grants/", url_text="Barcha grantlar")

    if is_callback:
        await update.callback_query.edit_message_text(text, parse_mode='Markdown', reply_markup=markup, disable_web_page_preview=True)
    else:
        await update.message.reply_text(text, parse_mode='Markdown', reply_markup=markup, disable_web_page_preview=True)

# ─── Pagination Callback ───────────────────────────────────

async def pagination_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    if data == "ignore":
        return
        
    parts = data.split('_')
    if len(parts) == 3 and parts[0] == "page":
        category = parts[1]
        page = int(parts[2])
        
        if category == "events":
            await events_handler(update, context, page=page, is_callback=True)
        elif category == "vacancies":
            await vacancies_handler(update, context, page=page, is_callback=True)
        elif category == "internships":
            await internships_handler(update, context, page=page, is_callback=True)
        elif category == "grants":
            await grants_handler(update, context, page=page, is_callback=True)


# ─── Obuna ────────────────────────────────────────────────

async def subscribe_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id

    result = await sync_to_async(_subscribe_user)(
        chat_id, user.username or '', user.first_name or ''
    )

    if result in ('created', 'reactivated'):
        text = (
            "🔔 *Obuna muvaffaqiyatli faollashtirildi!*\n\n"
            "Endi yangi tadbirlar, vakansiyalar, stajirovkalar va grantlar "
            "haqida birinchilardan bo'lib xabar olasiz! 🎉"
        )
    else:
        text = (
            "✅ Siz allaqachon obuna bo'lgansiz!\n\n"
            f"🔕 Bekor qilish uchun *\"{BTN_UNSUBSCRIBE}\"* tugmasini bosing."
        )

    await update.message.reply_text(
        text, parse_mode='Markdown', reply_markup=main_reply_keyboard()
    )


# ─── Obunani bekor qilish ─────────────────────────────────

async def unsubscribe_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    removed = await sync_to_async(_unsubscribe_user)(chat_id)

    if removed:
        text = f"🔕 Obuna bekor qilindi.\n\nQayta obuna bo'lish uchun *\"{BTN_SUBSCRIBE}\"* tugmasini bosing."
    else:
        text = f"Siz hali obuna bo'lmagansiz.\n\n*\"{BTN_SUBSCRIBE}\"* tugmasini bosing."

    await update.message.reply_text(
        text, parse_mode='Markdown', reply_markup=main_reply_keyboard()
    )


# ─── Yordam ───────────────────────────────────────────────

async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "ℹ️ *Nordic University Portal Bot*\n\n"
        f"• {BTN_EVENTS} — Kelgusi tadbirlar\n"
        f"• {BTN_VACANCIES} — Ochiq ish o'rinlari\n"
        f"• {BTN_INTERNSHIPS} — Stajirovka imkoniyatlari\n"
        f"• {BTN_GRANTS} — Grantlar va stipendiyalar\n"
        f"• {BTN_SUBSCRIBE} — Yangi e'lonlarga obuna\n\n"
        f"🌐 *Sayt:* {get_site_url()}\n"
        "🎓 *Nordic University Tashkent*"
    )
    await update.message.reply_text(
        text, parse_mode='Markdown',
        reply_markup=site_link_keyboard("Saytga o'tish", "/"),
        disable_web_page_preview=True
    )


# ─── Matn xabarlari dispatcher ────────────────────────────

async def text_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    dispatch = {
        BTN_EVENTS:      events_handler,
        BTN_VACANCIES:   vacancies_handler,
        BTN_INTERNSHIPS: internships_handler,
        BTN_GRANTS:      grants_handler,
        BTN_SUBSCRIBE:   subscribe_handler,
        BTN_UNSUBSCRIBE: unsubscribe_handler,
        BTN_HELP:        help_handler,
    }
    handler = dispatch.get(text)
    if handler:
        await handler(update, context)
    else:
        await update.message.reply_text(
            "❓ Tugmalardan birini bosing 👇",
            reply_markup=main_reply_keyboard()
        )


# ─── App builder ─────────────────────────────────────────

# Singleton — har bir Django request uchun qayta yaratmaslik uchun
_application = None

def get_application() -> Application:
    """
    Application singleton qaytaradi.
    Webhook rejimida Django view bu ob'ektni ishlatadi.
    Polling rejimida runbot management command ishlatadi.
    """
    global _application
    if _application is None:
        token = settings.TELEGRAM_BOT_TOKEN
        _application = Application.builder().token(token).build()

        _application.add_handler(CommandHandler("start",       start))
        _application.add_handler(CommandHandler("events",      events_handler))
        _application.add_handler(CommandHandler("vacancies",   vacancies_handler))
        _application.add_handler(CommandHandler("internships", internships_handler))
        _application.add_handler(CommandHandler("grants",      grants_handler))
        _application.add_handler(CommandHandler("subscribe",   subscribe_handler))
        _application.add_handler(CommandHandler("unsubscribe", unsubscribe_handler))
        _application.add_handler(CommandHandler("help",        help_handler))
        _application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_message_handler))
        _application.add_handler(CallbackQueryHandler(pagination_callback, pattern="^page_|^ignore$"))

    return _application


# ─── Development: to'g'ridan-to'g'ri ishga tushirish ─────
# Faqat: python telegram_bot/bot.py
# Production da: webhook orqali Django view ishlatiladi

if __name__ == '__main__':
    import os
    import sys
    import django

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if BASE_DIR not in sys.path:
        sys.path.insert(0, BASE_DIR)

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nordic_uni.settings')
    try:
        from django.apps import apps
        if not apps.ready:
            django.setup()
    except Exception:
        django.setup()

    app = get_application()
    logger.info("🤖 Bot polling rejimida ishga tushdi (development)...")
    logger.info("ℹ️  Production da webhook ishlating: python manage.py set_webhook")
    app.run_polling(drop_pending_updates=True)
