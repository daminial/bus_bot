"""Модуль для инициализации парсеров."""

from bot.server.data.advertisement_parse_content import parse_advertisements
from bot.server.data.routes_parse import parse_atp_routes

__all__ = [
    'parse_advertisements',
    'parse_atp_routes',
]
