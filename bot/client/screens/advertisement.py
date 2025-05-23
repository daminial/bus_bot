"""Модуль для экранов объявлений."""

import json
from typing import TYPE_CHECKING, Any

from config import ADV_SCREEN_DESCRIPTION
from hammett.core import Button, Screen
from hammett.core.constants import RenderConfig, SourceTypes
from screens.base import BaseParse, BaseScreen

if TYPE_CHECKING:
    from typing import Self

    from hammett.types import Update
    from telegram.ext import CallbackContext
    from telegram.ext._utils.types import BD, BT, CD, UD


class AdvertisementScreen(BaseParse):
    """Класс реализует экран меню объявлений, а также передает данные в объявление."""

    description = ADV_SCREEN_DESCRIPTION

    _json_filename = 'krimscoe_atp_full_advertisement.json'

    @staticmethod
    def _transform_data(parsed_data: list[dict[str, Any]]) -> list[dict[str, str]]:
        """Преобразует список объявлений в нужный формат."""
        return [
            {
                'title': advertisement.get('title', ''),
                'text': advertisement.get('text', ''),
                'date': advertisement.get('date', ''),
            }
            for advertisement in parsed_data
        ]

    async def get_config(
        self: 'Self',
        _update: 'Update | None',
        _context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> 'RenderConfig':
        """Генерирует и возвращает конфигурацию с кнопками для выбора объявления."""
        self.load_data_from_json()

        keyboard = [
            [Button(
                advertisement['title'],
                SelectedAdvertisement,
                source_type=SourceTypes.MOVE_SOURCE_TYPE,
                payload=json.dumps({
                    'title': advertisement['title'],
                    'text': advertisement['text'],
                    'date': advertisement['date'],
                }),
            )]
            for advertisement in self._data
        ]

        return RenderConfig(
            keyboard=[
                *keyboard,
                [self._get_back_button()],
            ],
        )


class SelectedAdvertisement(BaseScreen):
    """Класс который реализует экрный объявлений."""

    async def get_config(
        self: 'Self',
        update: 'Update | None',
        context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> 'RenderConfig':
        """Возвращает надписи и кнопки маршрутов."""
        try:
            advertisement_data = await Screen.get_payload(update, context)
            advertisement_data = json.loads(advertisement_data)

        except (json.JSONDecodeError):
            return RenderConfig(
                description='⚠️ Произошла ошибка при загрузке объявления',
                keyboard=[[
                    self._get_back_button(),
                ]],
            )

        description = (
            f"📌 {advertisement_data.get('title', '')}\n\n"
            f"{advertisement_data.get('text', '')}\n\n"
            f"📅 Дата: {advertisement_data.get('date', '')}"
        )

        return RenderConfig(
            description=description,
            keyboard=[
                [
                    Button(
                        '⬅️ Назад к объявлениям',
                        AdvertisementScreen,
                        source_type=SourceTypes.MOVE_SOURCE_TYPE,
                    ),
                    self._get_back_button(),
                ],
            ],
        )
