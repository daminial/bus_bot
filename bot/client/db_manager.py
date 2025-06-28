"""Модуль реализует взаимодействие клиента и сервера."""
import logging
from typing import TYPE_CHECKING
from rest_framework import status

import aiohttp

logger = logging.getLogger(__name__)

if TYPE_CHECKING:

    from typing import Self

HTTP_STATUS_OK = 200


class RequestFailed(Exception):
    """Исключение при неудачном HTTP-запросе."""
    def __init__(self, status: int, message: str = "Запрос к серверу завершился неудачно"):
        self.status = status
        self.message = message
        super().__init__(message)


class APIClient:
    """Класс реализует отправку запросов на сервер."""

    def __init__(self:'Self') -> None:
        """Иницализатор класса."""
        self.base_url = 'http://127.0.0.1:8000/api/main'
        self.timeout = aiohttp.ClientTimeout(total=3)

    async def get_all_users(self) -> list[int]:
        """Получает список всех user_id из базы данных."""
        url = f'{self.base_url}/users/all/'
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session, \
                    session.get(url) as response:
                if response.status == HTTP_STATUS_OK:
                    data = await response.json()
                    return data.get('user_ids', [])
                logger.error('Get users error: %s', response.status)
                return []
            raise RequestFailed(
                    status=response.status,
                    message=f'Get users error: {response.status}'
                )
        except aiohttp.ClientError as e:
            raise RequestFailed(
                status=0,
                message=f'Ошибка соединения с сервером: {str(e)}'
            ) from e

    async def get_favorite_status(
        self:'Self',
        user_id:int,
        bus_number:str,
    ) -> tuple:
        """Реализует запрос данных с бд."""
        url = f'{self.base_url}/favorites/{user_id}/{bus_number}/'
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session, \
                   session.get(url) as response:
                if response.status == HTTP_STATUS_OK:
                    data = await response.json()
                    return data.get('exists', False), data.get('favorite_time')
                logger.error('API error: %s', response.status)
                return False, None
        except aiohttp.ClientError:
            logger.exception('Connection error:')
            return False, None

    async def get_user_favorites(self, user_id: int) -> list[dict]:
        """Получает избранные маршруты пользователя."""
        url = f'{self.base_url}/favorites/user/{user_id}/'
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session, \
                    session.get(url) as response:
                if response.status == HTTP_STATUS_OK:
                    data = await response.json()
                    return data.get('favorites', [])
                logger.error('Get user favorites error: %s', response.status)
                return []
        except aiohttp.ClientError:
            logger.exception('Connection error:')
            return []

    async def add_favorite_route(
        self:'Self',
        user_id: int,
        bus_number: str,
        favorite_time: str = '',
    ) -> bool:
        """Реализует добавление маршрута в избранное."""
        url = f'{self.base_url}/favorites/add/'
        payload = {
            'user_id': user_id,
            'bus_number': bus_number,
            'favorite_time': favorite_time,
        }
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session, \
                    session.post(url, json=payload) as response:
                    if response.status == status.HTTP_201_CREATED:
                        return True
                    logger.error('Add favorite error: %s', response.status)
                    return False
        except aiohttp.ClientError:
            logger.exception('Connection error:')
            return False

    async def remove_favorite_route(
        self:'Self',
        user_id: int,
        bus_number: str,
    ) -> bool:
        """Реализует удаление маршрута из избранного."""
        url = f'{self.base_url}/favorites/remove/{user_id}/{bus_number}/'

        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session, \
                    session.delete(url) as response:
                    if response.status == HTTP_STATUS_OK:
                        return True
                    logger.error('Remove favorite error: %s', response.status)
                    return False
        except aiohttp.ClientError:
            logger.exception('Connection error:')
            return False

    async def update_favorite_time(
        self:'Self',
        user_id: int,
        bus_number: str,
        favorite_time: str,
    ) -> tuple[bool, str]:
        """Обновляет время для избранного маршрута (добавляет или обновляет)."""
        url = f'{self.base_url}/favorites/update/{user_id}/{bus_number}/'
        payload = {'favorite_time': favorite_time}

        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session, \
                    session.patch(url, json=payload) as response:

                if response.status == HTTP_STATUS_OK:
                    data = await response.json()
                    return True, data.get('status', 'updated')

                logger.error('Update favorite time error: %s', response.status)
                return False, 'error'

        except aiohttp.ClientError:
            logger.exception('Connection error:')
            return False, 'connection_error'

API_CLIENT = APIClient()
