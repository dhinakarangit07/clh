from .base import *
from .db import *
from .mail import *



# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-(mjh-3p)3az9g3dgn9fkcka-*^+$es*t*&)w1gd!soy&zs%zcr"

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ["*"]



CORS_ALLOW_CREDENTIALS = True


#change it in production!
CORS_ALLOW_ALL_ORIGINS = True

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8080",
    "http://localhost:8081",
    "https://clh-frontend-p2.vercel.app/",
    "https://clh-frontend-v2.vercel.app/",
    "https://clh-frontend.vercel.app/"
]


try:
    from .local import *
except ImportError:
    pass
