"""Модуль для инициализации экранов."""

from screens.advertisement import AdvertisementScreen, SelectedAdvertisement
from screens.buses_conf import BusesList, SelectedRoute, SelectedShedule
from screens.favorite import FavoriteRoutesScreen
from screens.main_menu import MainMenuScreen

__all__ = [
    'AdvertisementScreen',
    'BusesList',
    'FavoriteRoutesScreen',
    'MainMenuScreen',
    'SelectedAdvertisement',
    'SelectedRoute',
    'SelectedShedule',
]
