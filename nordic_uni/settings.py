"""
Django settings for Nordic University Tashkent Portal
"""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-nordic-uni-tashkent-secret-key-2025'

DEBUG = False

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    # Jazzmin — must be BEFORE django.contrib.admin
    'jazzmin',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party
    'crispy_forms',
    'crispy_bootstrap5',
    'ckeditor',
    'ckeditor_uploader',

    # Local apps
    'core',
    'events',
    'opportunities',
    'articles',
    'telegram_bot',
    'analytics',
]

# ─── Telegram Bot ────────────────────────────────────────
TELEGRAM_BOT_TOKEN = '8735073529:AAE6GK5ESRAedM0uzvlifjPUltJM11AaAkg'

# Development uchun: ngrok yoki localhost.run URL
# Production uchun: https://yourdomain.com
SITE_URL = 'http://127.0.0.1:8000'

# Webhook URL (HTTPS talab qilinadi; development uchun ngrok ishlating)
# Misol: https://abcd1234.ngrok.io
TELEGRAM_WEBHOOK_HOST = SITE_URL  # Production da HTTPS URL qo'ying

# ─── CKEditor ─────────────────────────────────────────
CKEDITOR_UPLOAD_PATH = 'ckeditor_uploads/'
CKEDITOR_IMAGE_BACKEND = 'pillow'
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'Custom',
        'toolbar_Custom': [
            ['Bold', 'Italic', 'Underline', 'Strike', 'Subscript', 'Superscript'],
            ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent'],
            ['JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock'],
            ['Link', 'Unlink'],
            ['Image', 'Table', 'HorizontalRule', 'SpecialChar'],
            ['Styles', 'Format', 'Font', 'FontSize'],
            ['TextColor', 'BGColor'],
            ['Maximize', '-', 'Source'],
        ],
        'height': 300,
        'width': '100%',
        'extraPlugins': 'autogrow',
        'autoGrow_onStartup': True,
        'removePlugins': 'elementspath',
        'resize_enabled': True,
        'skin': 'moono-lisa',
    },
    'basic': {
        'toolbar': 'Basic',
        'toolbar_Basic': [
            ['Bold', 'Italic', 'Underline'],
            ['NumberedList', 'BulletedList'],
            ['Link', 'Unlink'],
            ['Source'],
        ],
        'height': 200,
        'width': '100%',
    },
}

# ─── Jazzmin Admin UI ─────────────────────────────────────
JAZZMIN_SETTINGS = {
    # Window title & branding
    "site_title": "Nordic University Admin",
    "site_header": "Nordic University",
    "site_brand": "Nordic Uni",
    "site_logo": "images/nordic_logo.png",
    "login_logo": "images/nordic_logo.png",
    "site_icon": "images/nordic_logo.png",
    "welcome_sign": "Welcome to Nordic University Admin Panel",
    "copyright": "Nordic University Tashkent © 2025",

    # Search across these models
    "search_model": ["auth.user", "events.event", "opportunities.vacancy",
                     "opportunities.internship", "opportunities.grant", "core.partner"],

    # User avatar field
    "user_avatar": None,

    # ── Top Menu ──
    "topmenu_links": [
        {"name": "🏠 Portal", "url": "/", "new_window": True},
        {"name": "📊 Analytics", "url": "/analytics/dashboard/"},
        {"name": "📅 Events", "url": "/events/", "new_window": True},
        {"name": "💼 Vacancies", "url": "/opportunities/vacancies/", "new_window": True},
        {"name": "🏆 Grants", "url": "/opportunities/grants/", "new_window": True},
        {"model": "auth.user"},
    ],

    # ── User Menu (top right) ──
    "usermenu_links": [
        {"name": "🌐 View Site", "url": "/", "new_window": True},
        {"model": "auth.user"},
    ],

    # ── Sidebar ──
    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": [],
    "hide_models": [],

    # Custom sidebar order
    "order_with_respect_to": [
        "analytics",
        "core",
        "events",
        "opportunities",
        "articles",
        "telegram_bot",
        "auth",
    ],

    # Custom sidebar icons (Font Awesome 5 Free)
    "icons": {
        # Analytics
        "analytics":                       "fas fa-chart-line",
        "analytics.pagevisit":             "fas fa-eye",
        # Auth
        "auth":                            "fas fa-shield-alt",
        "auth.user":                       "fas fa-user-circle",
        "auth.group":                      "fas fa-user-shield",
        # Core
        "core":                            "fas fa-university",
        "core.partner":                    "fas fa-handshake",
        "core.sitesettings":               "fas fa-sliders-h",
        # Events
        "events":                          "fas fa-calendar-check",
        "events.event":                    "fas fa-calendar-star",
        "events.eventcategory":            "fas fa-bookmark",
        # Opportunities
        "opportunities":                   "fas fa-rocket",
        "opportunities.vacancy":           "fas fa-user-tie",
        "opportunities.vacancycategory":   "fas fa-sitemap",
        "opportunities.internship":        "fas fa-graduation-cap",
        "opportunities.grant":             "fas fa-trophy",
        "opportunities.grantcategory":     "fas fa-folder-open",
        # Articles
        "articles":                        "fas fa-newspaper",
        "articles.article":                "fas fa-file-alt",
        "articles.category":               "fas fa-tags",
        "articles.articleview":            "fas fa-eye",
        # Telegram
        "telegram_bot":                    "fab fa-telegram-plane",
        "telegram_bot.telegramsubscriber": "fas fa-bell",
    },
    "default_icon_parents": "fas fa-angle-right",
    "default_icon_children": "fas fa-dot-circle",

    # Misc
    "related_modal_active": True,
    "custom_css": None,
    "custom_js": None,
    "use_google_fonts_cdn": True,
    "show_ui_builder": False,
    "changeform_format": "horizontal_tabs",
    "changeform_format_overrides": {
        "auth.user": "collapsible",
        "auth.group": "vertical_tabs",
    },
}

JAZZMIN_UI_TWEAKS = {
    # Dark sidebar + vibrant header
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-primary",
    "accent": "accent-primary",
    "navbar": "navbar-dark",
    "no_navbar_border": True,
    "navbar_fixed": True,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-dark-primary",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "darkly",           # Sleek dark theme
    "dark_mode_theme": "darkly",
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success",
    },
    "actions_sticky_top": True,
}

# ─── Middleware ────────────────────────────────────────────
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # Analytics — page visit tracker (must be last)
    'analytics.middleware.PageVisitMiddleware',
]

ROOT_URLCONF = 'nordic_uni.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.site_settings',
            ],
        },
    },
]

WSGI_APPLICATION = 'nordic_uni.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Tashkent'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'

LOGIN_URL = '/auth/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
