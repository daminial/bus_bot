"""Модуль реализует базовые модули для экранов."""

import json
import logging
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar

import screens
from hammett.core import Button, Screen
from hammett.core.constants import RenderConfig, SourceTypes

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from typing import Self

    from hammett.types import Keyboard, Update
    from telegram.ext import CallbackContext
    from telegram.ext._utils.types import BD, BT, CD, UD


class BaseScreen(Screen):
    """Базовый класс, реализует добавление кнопки возврата."""

    @staticmethod
    def _get_back_button() -> 'Button':
        return Button(
            '🏠 В главное меню',
            source=screens.main_menu.MainMenuScreen,
            source_type=SourceTypes.MOVE_SOURCE_TYPE,
        )

    async def add_default_keyboard(
        self: 'Self',
        _update: 'Update | None',
        _context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> 'Keyboard':
        """Метод добавляет кнопку возврата на стартовый экран."""
        return [[self._get_back_button()]]


class BaseParse(BaseScreen):
    """Базовый класс для экранов advertisement и buses_conf.
    Реализует загрузку и обработку json файла.
    """

    _data: ClassVar[list] = []
    _json_filename: ClassVar[str] = ''

    @classmethod
    def _json_path(cls) -> Path:
        """Возвращает путь к файлу JSON с данными."""
        return Path(__file__).parent.parent.parent / 'server' / 'data' / cls._json_filename

    @classmethod
    def load_data_from_json(cls) -> None:
        """Загружает данные из JSON файла и сохраняет их в класс."""
        path = cls._json_path()
        try:
            with path.open(encoding='utf-8') as f:
                data = json.load(f)
                cls._data = cls._transform_data(data)
        except json.JSONDecodeError:
            logger.exception('Ошибка при чтении JSON файла')

    @staticmethod
    def _transform_data(parsed_data: list) -> list:
        """Преобразует данные в нужный формат. Должен быть переопределен в подклассах."""

    async def get_config(
        self: 'Self',
        _update: 'Update | None',
        _context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> 'RenderConfig':
        """Генерирует и возвращает конфигурацию с кнопками.
        Должен быть переопределен в подклассах.
        """
        raise NotImplementedError
