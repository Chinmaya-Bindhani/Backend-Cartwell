from .base import  *
import environ
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env()
environ.Env.read_env(BASE_DIR / ".env")

DATABASES = {
    'default': {
        'ENGINE': f'django.db.backends.{env("WHICH_DB")}',
        'NAME':env("DATABASE_NAME"),
        'USER':env("DATABASE_USER"),
        'PASSWORD':env("DATABASE_PASSWORD"),
    }
}


REDIS_URL = env("REDIS_URL", default="")

if REDIS_URL:
    CACHES = {"default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": REDIS_URL,
    }}
else:
    CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}
