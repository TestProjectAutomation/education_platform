from pathlib import Path
from django.utils.translation import gettext_lazy as _

BASE_DIR = Path(__file__).resolve().parent.parent

# ===========================
# SECURITY
# ===========================
SECRET_KEY = 'django-insecure-@2+s3+#awwel_e0u(j!e@==pl2d+xome9lz9^8$)goqeq6@685'
DEBUG = True
ALLOWED_HOSTS = []


# ===========================
# APPLICATIONS
# ===========================
INSTALLED_APPS = [
    'jazzmin',
    'accounts',

    # Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    # Allauth
    'allauth',
    'allauth.account',
    'allauth.socialaccount',

    # Third party
    'crispy_forms',
    'crispy_tailwind',
    'ckeditor',
    'modeltranslation',
    'hitcount',

    # Local apps
    'core',
    'articles',
    'scholarships',
    'books',
    # 'dashboard',
    'advertisements',
    'pages',
]

SITE_ID = 1


# ===========================
# MIDDLEWARE
# ===========================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'allauth.account.middleware.AccountMiddleware',
]


# ===========================
# URLS & TEMPLATES
# ===========================
ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

                # Custom
                'core.context_processors.site_settings',
                'core.context_processors.language_processor',
                'core.context_processors.dark_mode_processor',
                'core.context_processors.theme_settings',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# ===========================
# DATABASE
# ===========================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# ===========================
# AUTHENTICATION
# ===========================
AUTH_USER_MODEL = 'accounts.CustomUser'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

AUTH_USER_MODEL = 'accounts.CustomUser'
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/accounts/dashboard/'
LOGOUT_REDIRECT_URL = '/'



# ===========================
# PASSWORDS
# ===========================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ===========================
# INTERNATIONALIZATION
# ===========================
LANGUAGE_CODE = 'ar'

LANGUAGES = [
    ('ar', _('Arabic')),
    ('en', _('English')),
]

LOCALE_PATHS = [BASE_DIR / "locale"]

TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# ===========================
# STATIC & MEDIA
# ===========================
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


# ===========================
# CRISPY
# ===========================
CRISPY_ALLOWED_TEMPLATE_PACKS = "tailwind"
CRISPY_TEMPLATE_PACK = "tailwind"


# ===========================
# EMAIL
# ===========================
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"


# ===========================
# CKEDITOR
# ===========================
CKEDITOR_UPLOAD_PATH = "uploads/"
CKEDITOR_CONFIGS = {
    "default": {
        "toolbar": "full",
        "height": 300,
        "width": "100%",
    }
}


# ===========================
# DEFAULT PK
# ===========================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
