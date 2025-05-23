from hammett.core import Button, Screen
from hammett.core.constants import SourceTypes

from config import CONTACT_SCREEN_DESCRIPTION
from screens import mainMenu


class ContactScreen(Screen):
    """The class implements ContactScreen, which is always sent as a new message."""

    description = CONTACT_SCREEN_DESCRIPTION

    async def add_default_keyboard(self, _update, _context):
        """Set up the default keyboard for the screen."""
        return [[
            Button(
                '🏠 На главную',
                mainMenu.MainMenuScreen,
                source_type=SourceTypes.MOVE_SOURCE_TYPE,
            ),
        ]]
