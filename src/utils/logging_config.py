import logging
from logging.config import dictConfig

import os

os.makedirs("logs", exist_ok=True)

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,

    "formatters": {
        "default": {
            "format": "[%(asctime)s] [%(levelname)s] %(name)s - %(message)s",
        },
    },
    "handlers": {
        "console": {
            "formatter": "default",
            "class": "logging.StreamHandler",
        },
        "file": {
            "formatter": "default",
            "class": "logging.FileHandler",
            "filename": "logs/app.log",
            "mode": "a",
        },
    },
    "loggers": {
        # 👇 твой логгер приложения
        "app": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
        },

        # 👇 SQLAlchemy — отключаем или ставим WARNING
        "sqlalchemy.engine": {
            "handlers": ["console", "file"],
            "level": "CRITICAL",  # INFO → WARNING
            "propagate": False,
        },
    },
}


dictConfig(LOGGING_CONFIG)
logger = logging.getLogger("app")
