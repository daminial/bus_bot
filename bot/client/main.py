"""Модуль запускает бота."""

import sys
from pathlib import Path

import notification
from hammett.core import Bot
from hammett.core.constants import DEFAULT_STATE
from hammett.core.persistence import RedisPersistence

sys.path.append(str(Path(__file__).parent.parent.parent))

from screens import (
    AdvertisementScreen,
    BusesList,
    FavoriteRoutesScreen,
    MainMenuScreen,
    SelectedAdvertisement,
    SelectedRoute,
    SelectedShedule,
)

from bot.server.data import (
    parse_advertisements,
    parse_atp_routes,
)


def main() -> None:
    """Запуск бота и парсинг информации при надобности."""
    data_dir = Path(__file__).parent.parent / 'server' / 'data'

    routes_path = data_dir / 'krimscoe_atp_routes.json'
    ads_input_path = data_dir / 'krimscoe_atp_advertisement.json'
    ads_output_path = data_dir / 'krimscoe_atp_full_advertisement.json'

    if not routes_path.exists():
        parse_atp_routes(str(routes_path))

    if not ads_output_path.exists():
        parse_advertisements(
            input_file=str(ads_input_path),
            output_file=str(ads_output_path),
        )

    bot = Bot(
        'BusRoutesBot',
        entry_point=MainMenuScreen,
        states={
            DEFAULT_STATE: {
                MainMenuScreen,
                BusesList,
                AdvertisementScreen,
                SelectedRoute,
                SelectedAdvertisement,
                SelectedShedule,
                FavoriteRoutesScreen,
            },
        },
        persistence=RedisPersistence(),
        job_configs=[
            {
                'callback': notification.send_message_per_hour,
                'job_kwargs': {
                    'trigger': 'interval',
                    'minutes': 5,
                },
            },
        ],
    )

    bot.run()

if __name__ == '__main__':
    main()
