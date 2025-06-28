"""Модуль для работы с избранными маршрутами."""

from typing import TYPE_CHECKING

from db_manager import API_CLIENT
from hammett.core import Button
from hammett.core.constants import RenderConfig, SourceTypes
from hammett.core.handlers import register_button_handler
from screens.base import BaseScreen
from config import FAVORITE_SCREEN_DESCRIPTION

if TYPE_CHECKING:
    from typing import Self

    from hammett.types import Update
    from telegram.ext import CallbackContext
    from telegram.ext._utils.types import BD, BT, CD, UD


class FavoriteRoutesScreen(BaseScreen):
    """Экран для управления избранными маршрутами."""

    description = FAVORITE_SCREEN_DESCRIPTION

    async def get_config(
        self: 'Self',
        update: 'Update',
        _context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> 'RenderConfig':
        """Формирует список избранных маршрутов с кнопками удаления."""
        if not update or not update.effective_user:
            return self._error_config('Ошибка загрузки данных')

        user_id = update.effective_user.id
        routes = await API_CLIENT.get_user_favorites(user_id)

        keyboard = [
            [Button(
                f"❌ {route['bus_number']}",
                self._handle_delete_route,
                source_type=SourceTypes.HANDLER_SOURCE_TYPE,
                payload=route['bus_number'],
            )]
            for route in routes
        ]

        keyboard.append([self._get_back_button()])

        return RenderConfig(
            description=self.description,
            keyboard=keyboard,
        )

    @register_button_handler
    async def _handle_delete_route(
        self: 'Self',
        update: 'Update',
        context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> None:
        """Обработчик удаления маршрута из избранного."""
        if not update or not update.callback_query:
            return None

        user_id = update.effective_user.id
        route_id = await self.get_payload(update, context)

        success = await API_CLIENT.remove_favorite_route(user_id, route_id)
        if success:
            message = '🗑️ Маршрут удален из избранного'
            await update.callback_query.answer(message)
            await self.render(update, context)
            return await FavoriteRoutesScreen().move(update,context)
        else:
            return await update.callback_query.answer('⚠️ Не удалось удалить маршрут')
