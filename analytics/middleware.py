import re
import time
from .models import PageVisit

# Skip these paths from tracking
SKIP_PATTERNS = [
    re.compile(r'^/static/'),
    re.compile(r'^/media/'),
    re.compile(r'^/favicon\.ico'),
    re.compile(r'^/admin/jsi18n/'),
    re.compile(r'^/admin/autocomplete/'),
    re.compile(r'^/ckeditor/'),
    re.compile(r'\.map$'),
    re.compile(r'\.js$'),
    re.compile(r'\.css$'),
    re.compile(r'\.png$'),
    re.compile(r'\.jpg$'),
    re.compile(r'\.ico$'),
    re.compile(r'\.woff'),
    re.compile(r'^/analytics/track/'),  # skip our own tracking endpoint
]

BOT_AGENTS = [
    'bot', 'crawler', 'spider', 'slurp', 'bingbot', 'googlebot',
    'yandexbot', 'baiduspider', 'facebookexternalhit', 'twitterbot',
    'curl', 'wget', 'python-requests', 'scrapy',
]


def _is_bot(user_agent: str) -> bool:
    ua_lower = user_agent.lower()
    return any(bot in ua_lower for bot in BOT_AGENTS)


def _should_skip(path: str) -> bool:
    return any(p.match(path) for p in SKIP_PATTERNS)


class PageVisitMiddleware:
    """
    Records every real page visit to PageVisit model.
    Also tracks time_spent via a follow-up AJAX ping (handled in view).
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.monotonic()
        response = self.get_response(request)

        path = request.path
        method = request.method

        # Only track GET requests for real HTML pages
        if method != 'GET':
            return response
        if _should_skip(path):
            return response
        if response.status_code not in (200, 301, 302):
            return response

        try:
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            is_bot = _is_bot(user_agent)

            # Get IP
            x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded:
                ip = x_forwarded.split(',')[0].strip()
            else:
                ip = request.META.get('REMOTE_ADDR', '')

            # Session key
            if not request.session.session_key:
                request.session.create()
            session_key = request.session.session_key or ''

            # Referrer
            referrer = request.META.get('HTTP_REFERER', '')
            if len(referrer) > 500:
                referrer = referrer[:500]

            # Page name
            page_name = PageVisit.get_friendly_name(path)

            # Server-side elapsed time (rough, just for reference)
            elapsed = int((time.monotonic() - start_time) * 1000)  # ms

            PageVisit.objects.create(
                path=path,
                page_name=page_name,
                session_key=session_key,
                ip_address=ip or None,
                user_agent=user_agent[:500],
                referrer=referrer,
                is_bot=is_bot,
                time_spent=0,  # updated later via JS ping
            )
        except Exception:
            # Never break the site due to analytics error
            pass

        return response
