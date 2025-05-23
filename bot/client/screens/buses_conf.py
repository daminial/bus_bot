"""Модуль для экранов маршрутов автобусов."""

import json
import logging
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from hammett.core import Button
from hammett.core.constants import RenderConfig, SourceTypes
from hammett.core.handlers import register_button_handler
from hammett.widgets import MultiChoiceWidget

sys.path.append(str(Path(__file__).parent))

from config import BUSES_SCREEN_DESCRIPTION
from db_manager import API_CLIENT
from screens.base import BaseParse, BaseScreen

logger = logging.getLogger(__name__)

if TYPE_CHECKING:

    from typing import Self

    from hammett.types import Choice, InitializedChoices, Update
    from telegram.ext import CallbackContext
    from telegram.ext._utils.types import BD, BT, CD, UD


class BusesList(BaseParse):
    """Класс реаилизует экран-меню маршрутов и передает данные в концретный маршрут."""

    description = BUSES_SCREEN_DESCRIPTION

    _json_filename = 'krimscoe_atp_routes.json'

    @staticmethod
    def _transform_data(parsed_data: list) -> list:
        """Преобразует данные маршрутов в нужный формат."""
        return [
            {
                'id': route.get('number', str(idx)),
                'name': f"Маршрут {route.get('number', str(idx))}",
                'title': route.get('title', 'Без названия'),
                'path': BusesList._extract_path(route),
                'schedule': route.get('schedule', []),
                'description': route.get('description', ''),
            }
            for idx, route in enumerate(parsed_data, 1)
        ]

    @staticmethod
    def _extract_path(route: dict) -> str:
        """Извлекает путь маршрута из его названия."""
        title = route.get('title', '')
        return title.replace('Маршрут', '').strip()

    async def get_config(
        self: 'Self',
        _update: 'Update | None',
        context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> 'RenderConfig':
        """Генерирует и возвращает конфигурацию с кнопками для выбора маршрута."""
        self.load_data_from_json()

        context.user_data['all_routes'] = {
            route['id']: {
                'id': route['id'],
                'name': route['name'],
                'path': route['path'],
                'schedule': route['schedule'],
            }
            for route in self._data
        }

        buttons = [
            Button(
                route['name'],
                SelectedRoute,
                source_type=SourceTypes.MOVE_SOURCE_TYPE,
                payload=route['id'],
            )
            for route in self._data
        ]

        keyboard = [buttons[i:i+2] for i in range(0, len(buttons), 2)]

        return RenderConfig(
            keyboard=[
                *keyboard,
                [self._get_back_button()],
            ],
        )


class SelectedRoute(BaseScreen):
    """Класс для экранов маршрутов с интеграцией API клиента."""

    async def clear_all_selected_times(self, context: 'CallbackContext'):
        """Полностью очищает все выбранные времена."""
        if 'selected_times' in context.user_data:
            context.user_data['selected_times'] = {}

    async def get_config(
        self: 'Self',
        update: 'Update | None',
        context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> 'RenderConfig':
        """Формирует конфигурацию экрана маршрута с избранным статусом."""
        try:
            route_number = await self.get_payload(update, context)
            route_data = context.user_data['all_routes'].get(route_number, {})

            schedule_dict = {
                item['departure_info']: item['times']
                for item in route_data.get('schedule', [])
                if 'departure_info' in item and 'times' in item
            }

            context.user_data['selected_routes'] = [
                route_number,
                schedule_dict,
            ]

            is_favorite, _ = await API_CLIENT.get_favorite_status(
                update.effective_user.id,
                route_number,
            )

            keyboard = [
                [Button(
                    departure_info,
                    SelectedShedule,
                    source_type=SourceTypes.MOVE_SOURCE_TYPE,
                    payload=[departure_info, schedule_dict, route_number],
                )]
                for departure_info in schedule_dict
            ]

            return RenderConfig(
                description=f'🚌 Маршрут: {route_number}\n\n',
                keyboard=[
                    *keyboard,
                    [
                        Button(
                            '⬅️ Назад к маршрутам',
                            BusesList,
                            source_type=SourceTypes.MOVE_SOURCE_TYPE,
                        ),
                        self._get_back_button(),
                    ],
                    [
                        Button(
                            '❌ Удалить из избранного' if is_favorite
                            else '⭐️ Добавить в избранное',
                            self.favorite_button,
                            source_type=SourceTypes.HANDLER_SOURCE_TYPE,
                        ),
                    ],
                ],
            )

        except json.JSONDecodeError:
            logger.exception('JSON decode error in route data')
            return self._error_config('Ошибка формата данных маршрута')

    @register_button_handler
    async def favorite_button(
        self: 'Self',
        update: 'Update | None',
        context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> None:
        """Обработчик для управления избранными маршрутами через API."""
        if not update or not update.callback_query:
            return

        user_id = update.effective_user.id
        route_num = context.user_data['selected_routes'][0]
        is_favorite, _ = await API_CLIENT.get_favorite_status(user_id, route_num)

        if is_favorite:
            success = await API_CLIENT.remove_favorite_route(user_id, route_num)
            message = '🗑️ Удалено из избранного' if success else '⚠️ Ошибка удаления'
        else:
            success = await API_CLIENT.add_favorite_route(user_id, route_num)
            message = '⭐ Добавлено в избранное' if success else '⚠️ Ошибка добавления'

        await update.callback_query.answer(message)
        await self.get_config(update, context)

    def _error_config(self, message: str) -> 'RenderConfig':
        """Генерирует конфиг для состояния ошибки."""
        return RenderConfig(
            description=f'⚠️ {message}',
            keyboard=[[self._get_back_button()]],
        )


class SelectedShedule(BaseScreen, MultiChoiceWidget):
    """Класс реализует экран расписания маршрутов."""

    async def get_choices(
        self: 'Self',
        update: 'Update | None',
        context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> tuple:
        """Возвращает выбронное время в расписании."""
        self.schedule_dict = await self.get_payload(update, context)
        departer_info = self.schedule_dict[0]
        times_dict = self.schedule_dict[1]
        self.route_number = self.schedule_dict[2]

        if times_dict[departer_info]:
            result = [(time, time) for time in times_dict[departer_info]]

        return tuple(result)

    async def switch(
        self: 'Self',
        update: 'Update | None',
        context: 'CallbackContext[BT, UD, CD, BD]',
        selected_choice: 'Choice',
    ) -> 'InitializedChoices':
        """Сохраняет выбранное время и повторно отображает экран с обновленным эмодзи
        нажатой кнопки.
        """
        selected_times, _ = selected_choice
        if isinstance(context.user_data.get('selected_times'), list):
            if selected_times in context.user_data['selected_times']:
                context.user_data['selected_times'].remove(selected_times)
            else:
                context.user_data['selected_times'].append(selected_times)
        else:
            context.user_data['selected_times'] = [selected_times]

        return await super().switch(update, context, selected_choice)

    async def get_description(
        self: 'Self',
        _update: 'Update | None',
        _context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> str:
        """Возвращает заголовки экрана."""
        return(
            f'🚌 Расписание маршрута:{self.route_number}\n{self.schedule_dict[0]}\n\n'
            f'⏱ Время отправления:\n'
        )

    async def add_extra_keyboard(
        self: 'Self',
        _update: 'Update | None',
        _context: 'CallbackContext[BT, UD, CD, BD]',
        ) -> list:
        """Добаляет в клавиатуру кнопку возврата на главный экран и на предыдущий экран."""
        return [[
            Button(
                '⬅️ Назад к маршруту',
                SelectedRoute,
                source_type=SourceTypes.MOVE_SOURCE_TYPE,
                payload=self.route_number),
                self._get_back_button(),
        ],
        [
            Button(
                'Получить оповещение на это время',
                self.favorite_button,
                source_type=SourceTypes.HANDLER_SOURCE_TYPE,
            ),
        ]]

    @register_button_handler
    async def favorite_button(
        self: 'Self',
        update: 'Update | None',
        context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> None:
        """Обработчик для управления избранными маршрутами через API."""
        if not update or not update.callback_query:
            return

        user_id = update.effective_user.id
        route_num = self.route_number
        favotite_time = context.user_data['selected_times']
        is_favorite, _ = await API_CLIENT.get_favorite_status(user_id, route_num)

        if is_favorite:
            success, status = await API_CLIENT.update_favorite_time(
                user_id,
                route_num,
                favotite_time,
            )
            if success:
                message = '⏱ Время обновлено' if status == 'updated' else '⭐ Добавлено в избранное'
            else:
                message = '⚠️ Ошибка обновления'
        else:
            success = await API_CLIENT.add_favorite_route(
                user_id,
                route_num,
                favotite_time,
            )
            message = '⭐ Добавлено в избранное' if success else '⚠️ Ошибка добавления'

        context.user_data['selected_times'] = []

        await update.callback_query.answer(message)
        await self.get_config(update, context)

    def _error_config(self, message: str) -> 'RenderConfig':
        """Генерирует конфиг для состояния ошибки."""
        return RenderConfig(
            description=f'⚠️ {message}',
            keyboard=[[self._get_back_button()]],
        )
