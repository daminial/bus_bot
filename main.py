from hammett.core import Bot
from hammett.core.constants import DEFAULT_STATE

from screens import (
    advertisementScreen,
    BusesScreen,
    ContactScreen,
    HelpScreen,
    SelectedRoutes,
    MainMenuScreen,
)


def create_routes():
    return [
        {
            'id': '1',
            'name': '№450',
            'path': 'Центральный рынок - село Чалтырь',
            'map_url': 'https://example.com/map1',
        },
        {
            'id': '2',
            'name': '№150',
            'path': 'Центральный рынок - село Дружба',
            'map_url': 'https://example.com/map2',
        },
    ]

def main():
    routes = create_routes()
    BusesScreen.set_routes(routes)

    bot = Bot(
        'BusRoutesBot',
        entry_point=MainMenuScreen,
        states={
            DEFAULT_STATE: {
                HelpScreen,
                MainMenuScreen,
                BusesScreen,
                advertisementScreen,
                ContactScreen,
                SelectedRoutes,
            },
        },
        persistence=None,
    )

    bot.run()

if __name__ == '__main__':
    main()
