"""
Telegram Webhook View

Telegram POST so'rovlarini qabul qilib, python-telegram-bot ga uzatadi.
URL: /telegram/webhook/<TOKEN_HASH>/
"""

import json
import hashlib
import logging
import asyncio

from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

logger = logging.getLogger(__name__)


def _get_webhook_path() -> str:
    """Token asosida noyob webhook path generatsiya qiladi."""
    token = settings.TELEGRAM_BOT_TOKEN
    return hashlib.sha256(token.encode()).hexdigest()[:32]


@csrf_exempt
@require_POST
def telegram_webhook(request, token_hash: str):
    """
    Telegram serveridan kelgan update'larni qabul qiladi.
    Faqat to'g'ri token hash bilan so'rov qabul qilinadi.
    """
    # Token hash tekshiruvi (xavfsizlik)
    expected_hash = _get_webhook_path()
    if token_hash != expected_hash:
        logger.warning(f"Noto'g'ri webhook token hash: {token_hash}")
        return HttpResponseForbidden("Forbidden")

    # JSON parse
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        logger.error("Webhook: JSON parse xatosi")
        return HttpResponseBadRequest("Invalid JSON")

    # Update'ni bot application ga uzatish
    try:
        from telegram import Update
        from telegram_bot.bot import get_application

        app = get_application()

        # Event loop orqali async ishlov berish
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            async def process():
                await app.initialize()
                update = Update.de_json(data, app.bot)
                await app.process_update(update)

            loop.run_until_complete(process())
        finally:
            loop.close()

    except Exception as e:
        logger.exception(f"Webhook update qayta ishlashda xato: {e}")
        # Telegram xato bo'lsa ham 200 kutadi, aks holda qayta yuboradi
        return HttpResponse("Error", status=200)

    return HttpResponse("OK", status=200)
