from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
import os
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-1bc3dlo&@)a_ccz*19)5rru*+-%a8di-b1zxdhi6te%ctcr!&y')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

# Set allowed hosts based on environment
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '.onrender.com']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'whitenoise.runserver_nostatic',  # Added WhiteNoise
    'blog',
    'users',
    'backup',
    'projects',
    'django.contrib.sitemaps',
    'channels',  # For WebSocket support
]

INSTALLED_APPS += [
    'taggit',
    'seo',
    # 'notifications', # Removed as requested
]

# Social Authentication
INSTALLED_APPS += [
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.github',
]
SITE_ID = 1
INSTALLED_APPS += ['compressor']

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
]

COMPRESS_ENABLED = True
COMPRESS_CSS_FILTERS = [
    'compressor.filters.css_default.CssAbsoluteFilter',
    'compressor.filters.cssmin.rCSSMinFilter',
]
COMPRESS_JS_FILTERS = ['compressor.filters.jsmin.JSMinFilter']

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'blog.middleware.ImageOptimizationMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Added WhiteNoise middleware
]

WHITENOISE_USE_FINDERS = True
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

ROOT_URLCONF = 'PortfolioProject.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],  # Point to the templates folder
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'PortfolioProject.wsgi.application'

# Channels configuration
ASGI_APPLICATION = 'PortfolioProject.asgi.application'

# Channel layers for WebSocket real-time communication
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}

# Using SQLite database for both development and production
# With support for custom path on Render via environment variable
SQLITE_PATH = os.environ.get('SQLITE_PATH', os.path.join(BASE_DIR, 'db.sqlite3'))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': SQLITE_PATH,
    }
}

# Static and Media settings
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']  # Updated to use Path object

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

# Static files configuration
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Compression settings
COMPRESS_ROOT = STATIC_ROOT
COMPRESS_ENABLED = True
COMPRESS_OFFLINE = True
COMPRESS_OUTPUT_DIR = 'compressed'
COMPRESS_CSS_HASHING_METHOD = 'content'
COMPRESS_FILTERS = {
    'css': ['compressor.filters.css_default.CssAbsoluteFilter',  
            'compressor.filters.cssmin.rCSSMinFilter'],
    'js': ['compressor.filters.jsmin.JSMinFilter']
}

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Authentication Settings
LOGIN_REDIRECT_URL = 'profile'  # Where to redirect after login if no next parameter
ACCOUNT_LOGOUT_REDIRECT_URL = 'login'  # Where to redirect after logout
LOGIN_URL = 'login'  # Our custom login URL

# Email backend (for development, console output)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # For development

# Django Allauth Settings
AUTHENTICATION_BACKENDS = [
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',
    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',
]

# Provider specific settings
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    },
    'github': {
        'SCOPE': [
            'user',
            'repo',
            'read:org',
        ],
    }
}

# Additional AllAuth settings
ACCOUNT_AUTHENTICATION_METHOD = 'username_email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'none'  # Change to 'mandatory' in production
ACCOUNT_USERNAME_REQUIRED = True
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = True
ACCOUNT_LOGOUT_ON_GET = True  # Skip confirmation page on logout

# Cache settings
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': 'c:/Users/pinja/OneDrive/Desktop/Portf/PortfolioV2/django_cache',
    }
}

# Cache timeout in seconds (1 hour)
CACHE_MIDDLEWARE_SECONDS = 3600

# Backup settings
BACKUP_DIR = os.path.join(BASE_DIR, 'backups')
