"""Local development. Never used for a deployment."""
from .base import *  # noqa: F403
from .base import env, env_bool, env_list

DEBUG = env_bool('DJANGO_DEBUG', True)

# A throwaway default keeps `git clone && runserver` working without a .env,
# while prod.py refuses to start without a real key.
SECRET_KEY = env('DJANGO_SECRET_KEY', 'dev-only-insecure-key-do-not-deploy')

ALLOWED_HOSTS = env_list('DJANGO_ALLOWED_HOSTS', '127.0.0.1,localhost,testserver')
