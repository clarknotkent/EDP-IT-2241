"""Deployment settings. Fails loudly rather than falling back to a dev default."""
from .base import *  # noqa: F403
from .base import env, env_list

DEBUG = False

SECRET_KEY = env('DJANGO_SECRET_KEY', required=True)

ALLOWED_HOSTS = env_list('DJANGO_ALLOWED_HOSTS')
if not ALLOWED_HOSTS:
    raise RuntimeError('DJANGO_ALLOWED_HOSTS must be set when DEBUG is False')

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31_536_000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
