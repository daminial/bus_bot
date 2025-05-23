"""The module contains the settings of the demo."""

import os

from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('TOKEN_BOT')
