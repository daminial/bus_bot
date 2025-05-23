from hammett.core import Button
from hammett.core.constants import SourceTypes
from hammett.core.mixins import StartMixin

import screens.buses_conf as buses
from config import START_SCREEN_DESCRIPTION
from screens import advertisement, contacts


class MainMenuScreen(StartMixin):

    description = START_SCREEN_DESCRIPTION

    async def add_default_keyboard(self, _update, _context):
        return [
            [Button(
                '🚌 Маршруты автобусов',
                buses.BusesScreen,
                source_type=SourceTypes.MOVE_SOURCE_TYPE,
            )],
            [Button(
                '📄 Объявления',
                advertisement.advertisementScreen,
                source_type=SourceTypes.MOVE_SOURCE_TYPE,
            )],
            [Button(
                '📞 Контакты',
                contacts.ContactScreen,
                source_type=SourceTypes.MOVE_SOURCE_TYPE,
            )],
        ]
