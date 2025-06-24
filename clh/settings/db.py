from .base import *

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases



# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.sqlite3",
#         "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
#     }
# }


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'defaultdb',
        'HOST': 'mysql-pavi789-rootrk05-6427.b.aivencloud.com',  # or your MySQL host
        'PORT': '28822',       # default MySQL port
    }
}
import os
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
