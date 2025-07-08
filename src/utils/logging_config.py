import os
import logging
from logging.config import dictConfig

# Получаем путь к директории, где лежит этот файл (logging_config.py)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
log_dir = os.path.join(BASE_DIR, "logs")
os.makedirs(log_dir, exist_ok=True)

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
            "filename": os.path.join(log_dir, "app.log"),  # 👈 здесь путь уже корректный
            "mode": "a",
        },
    },
    "loggers": {
        "app": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
        },
        "sqlalchemy.engine": {
            "handlers": ["console", "file"],
            "level": "CRITICAL",
            "propagate": False,
        },
    },
}

dictConfig(LOGGING_CONFIG)
logger = logging.getLogger("app")
