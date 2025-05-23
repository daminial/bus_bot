"""Реализует стартовый экран."""

from typing import TYPE_CHECKING

import screens.buses_conf as buses
from config import START_SCREEN_DESCRIPTION
from hammett.core import Button
from hammett.core.constants import SourceTypes
from hammett.core.mixins import StartMixin
from screens import advertisement, favorite

if TYPE_CHECKING:
    from typing import Self

    from hammett.types import Keyboard, Update
    from telegram.ext import CallbackContext
    from telegram.ext._utils.types import BD, BT, CD, UD


class MainMenuScreen(StartMixin):
    """Реализует класс меню всего приложения."""

    description = START_SCREEN_DESCRIPTION

    async def add_default_keyboard(
        self: 'Self',
        _update: 'Update | None',
        _context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> 'Keyboard':
        """Создает клавиатуру."""
        return [
            [Button(
                '🚌 Маршруты автобусов',
                buses.BusesList,
                source_type=SourceTypes.MOVE_SOURCE_TYPE,
            )],
            [Button(
                '📄 Объявления',
                advertisement.AdvertisementScreen,
                source_type=SourceTypes.MOVE_SOURCE_TYPE,
            )],
            [Button(
                '⭐️ Избранное',
                favorite.FavoriteRoutesScreen,
                source_type=SourceTypes.MOVE_SOURCE_TYPE,
            )],
        ]
