from .docker import *

# データベースに発行したSQLをログ出力する場合は次の行の「_LOGGING」を「LOGGING」にする
_LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "django.db.backends": {
            "handlers": ["console"],
            "level": "DEBUG",
        },
    },
}

# Google Login OAuth token
# .env に書くか、またはここに書く
# GOOGLE_OAUTH_CLIENT_ID = ""
# GOOGLE_OAUTH_CLIENT_SECRET = ""
