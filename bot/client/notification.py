"""Модуль реализует уведомления по избранным маршрутам."""

import ast
import re
from datetime import datetime, time

from db_manager import API_CLIENT
from hammett.core import Button, Screen
from hammett.core.constants import RenderConfig, SourceTypes
from typing import TYPE_CHECKING
from screens import main_menu
from config import MIN_NOTIFICATION_MINUTES
from config import MAX_NOTIFICATION_MINUTES

if TYPE_CHECKING:

    from telegram.ext import CallbackContext
    from telegram.ext._utils.types import BD, BT, CD, UD


class Notification(Screen):
    """Реализует экран оповещения."""

    description = 'Ваше оповещение.'


def format_route_data(route: dict) -> str:
    """Форматирует один маршрут из БД в читаемую строку."""
    bus_num = route['bus_number'].replace('\u2116', '№').strip()

    time_str = route['favorite_time'].strip('[]\'"')
    times = [t.strip() for t in time_str.split(',') if t.strip()]

    if not times:
        return f'🚍 {bus_num} (время не указано)'
    return f"🚍 {bus_num} - ⏱ {', '.join(times)}"


def prepare_notification_text(routes: list[dict]) -> str:
    """Подготавливает полный текст уведомления из данных БД."""
    routes_sorted = sorted(
        routes,
        key=lambda x: int(''.join(c for c in x['bus_number'] if c.isdigit()) or 0),
    )
    lines = [format_route_data(route) for route in routes_sorted]
    return '\n'.join(lines)


def parse_time(time_str: str) -> time:
    """Преобразует строку с временем в формате HH:MM, HH.MM, HH-MM или с дополнительным текстом
    в объект datetime.time. Возвращает None, если время некорректное.
    """
    if not time_str or not isinstance(time_str, str):
        return None

    match = re.search(r'(\d{1,2})[:.\-](\d{2})', time_str.strip())
    if not match:
        return None

    try:
        hours = int(match.group(1))
        minutes = int(match.group(2))

        if 0 <= hours < time.max.hour  and 0 <= minutes < time.max.minute:
            return time(hours, minutes)
        else:
            return None
    except (ValueError, IndexError):
        return None


def extract_time_list(time_data: str) -> list:
    """Преобразует строку вида "['14-00']" или "['5:30 ежед.', '8:35 будни']" в список."""
    if not time_data:
        return []

    try:
        time_list = ast.literal_eval(time_data.strip())
        if isinstance(time_list, list):
            return time_list
        if isinstance(time_list, str):
            return [time_list]
        else:
            return []
    except (ValueError, SyntaxError):
        return []


async def send_message_per_hour(context: 'CallbackContext[BT, UD, CD, BD]') -> None:
    """Реализует корректироваку данных и соблюдение условия для отправки оповещения."""
    users = await API_CLIENT.get_all_users()
    for user in users:
        times = await API_CLIENT.get_user_favorites(user)
        routes_sorted = sorted(
            times,
            key=lambda x: int(''.join(c for c in x['bus_number'] if c.isdigit()) or 0),
        )
        current_time = datetime.now().time()
        current_datetime = datetime.combine(datetime.today(), current_time)

        for user_favorite_route in routes_sorted:
            time_list = extract_time_list(user_favorite_route['favorite_time'])
            if not time_list:
                continue

            parsed_times = [parse_time(t) for t in time_list]
            valid_times = [t for t in parsed_times if t is not None]
            if not valid_times:
                continue

            bus_number = user_favorite_route['bus_number'].replace('\u2116', '№').strip()

            for bus_time in valid_times:
                bus_datetime = datetime.combine(datetime.today(), bus_time)
                time_diff = (bus_datetime - current_datetime).total_seconds() / 60

                if MIN_NOTIFICATION_MINUTES < time_diff <= MAX_NOTIFICATION_MINUTES:
                    config = RenderConfig(
                        description=f"🚍 Автобус {bus_number} через {int(time_diff)} мин. ({bus_time.strftime('%H:%M')})",
                        chat_id=user,
                        keyboard=[[
                            Button(
                                '⬅️ Main Menu',
                                main_menu.MainMenuScreen,
                                source_type=SourceTypes.MOVE_SOURCE_TYPE),
                        ]],
                    )
                    await Notification().send(context, config=config)
                    break
