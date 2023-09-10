from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

AUTHENTICATION_BACKENDS = [
    'account.authentication.ApiBackend',
    'django.contrib.auth.backends.ModelBackend',
    ]

SECRET_KEY = "django-insecure-vd#z%51p5n4!_2@!t$!4aair8r+$*^1$4!qp$=8rw78215aeg*"

DEBUG = True

swappable = 'AUTH_USER_MODEL'

AUTH_USER_MODEL = 'account.User'

ADMIN_URL = 'puma_trans/admin/'

ALLOWED_HOSTS = ['*']

CSRF_COOKIE_SECURE = False

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "account",
    "report",
    'bootstrap5',
    'fontawesomefree',
    'django_filters',
    'widget_tweaks',
    'django_extensions',
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "report_transport.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, 'account', 'templates', 'user'), os.path.join(BASE_DIR, 'account', 'templates', 'fragment'), 
                 os.path.join(BASE_DIR, 'account', 'templates', 'line'), os.path.join(BASE_DIR, 'report', 'templates', 'emplacement'), 
                 os.path.join(BASE_DIR, 'report', 'templates', 'fournisseur'), os.path.join(BASE_DIR, 'report', 'templates', 'price'), 
                 os.path.join(BASE_DIR, 'report', 'templates', 'tonnage'), os.path.join(BASE_DIR, 'report', 'templates', 'product'), 
                 os.path.join(BASE_DIR, 'report', 'templates', 'modal'), os.path.join(BASE_DIR, 'report', 'templates', 'report'), 
                 ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "report_transport.wsgi.application"


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'trans_report',
        'USER': 'puma_u',
        'PASSWORD': 'puma_u',
        'HOST': '192.168.135.1',
        'PORT': '5432',
    }
}


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


LANGUAGE_CODE = "fr"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

LOGIN_REDIRECT_URL = 'login_success'
LOGOUT_REDIRECT_URL = '/login'


STATIC_URL = '/static/'

STATICFILES_DIRS = [BASE_DIR / "static"]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
