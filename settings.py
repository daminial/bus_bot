"""Модуль хранит настройки для бота."""

import os

from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('TOKEN_BOT')

REDIS_PERSISTENCE = {
    'HOST': '127.0.0.1',
    'PORT': 6379,
    'DB': 0,
    'PASSWORD': None,
}
