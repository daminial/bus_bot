import json

from hammett.core import Button, Screen
from hammett.core.constants import RenderConfig, SourceTypes

from config import BUSES_SCREEN_DESCRIPTION
from screens import mainMenu


class BusesScreen(Screen):
    _routes = []

    @classmethod
    def set_routes(cls, routes):
        cls._routes = routes

    description=BUSES_SCREEN_DESCRIPTION

    async def get_config(self, update, context, **kwargs):
        keyboard = [
            [
                Button(
                    route['name'],
                    SelectedRoutes,
                    source_type=SourceTypes.MOVE_SOURCE_TYPE,
                    payload=json.dumps(route),
                ),
            ] for route in self._routes
        ]

        config = RenderConfig(
            description=BUSES_SCREEN_DESCRIPTION,
            keyboard=[
                *keyboard,
                [Button(
                    'На главную',
                    mainMenu.MainMenuScreen,
                    source_type=SourceTypes.MOVE_SOURCE_TYPE,
                )],
            ],
        )
        return config

class SelectedRoutes(Screen):
    async def get_config(self, update, context, **kwargs):

        route_data = await Screen.get_payload(update, context)
        route_data = json.loads(route_data)

        description = (
            f"🚌 <b>{route_data['name']}</b>\n\n"
            f"⏱ остановки: {route_data.get('path', 'не указано')}\n"
            f"Стоимость: {route_data.get('price', 'не указана')}"
        )

        keyboard = await self.add_default_keyboard(update, context, route_data)

        return RenderConfig(description=description, keyboard=keyboard)

    async def add_default_keyboard(self, update, context, route_data):
        return [
            [
                Button(
                    '🗺 Посмотреть на карте',
                    route_data['map_url'],
                    source_type=SourceTypes.URL_SOURCE_TYPE,
                ),
            ],
            [
                Button(
                    '⬅️ Назад к маршрутам',
                    BusesScreen,
                    source_type=SourceTypes.MOVE_SOURCE_TYPE,
                ),
                Button(
                    '🏠 На главную',
                    mainMenu.MainMenuScreen,
                    source_type=SourceTypes.MOVE_SOURCE_TYPE,
                ),
            ],
        ]
