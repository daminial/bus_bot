"""Модуль отвечает за создание моделей для приложения ()."""
from django.db import models


class User(models.Model):
    """Модель пользователей."""

    user_id = models.BigIntegerField(primary_key=True)

    class Meta:
        db_table = 'users'

    def __str__(self) -> str:
        """Возвращает строковое представление пользователя."""
        return f'User {self.user_id}'


class Bus(models.Model):
    """Модель автобусов."""

    bus_number = models.CharField(max_length=20, primary_key=True)

    class Meta:
        db_table = 'buses'

    def __str__(self) -> str:
        """Возвращает строковое представление автобуса."""
        return f'Bus: {self.bus_number}'


class UserFavorite(models.Model):
    """Модель избранных маршрутов пользователя."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id')
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, db_column='bus_number')
    favorite_time = models.CharField(max_length=300)

    class Meta:
        db_table = 'user_favorites'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'bus', 'favorite_time'],
                name='unique_user_bus_time'
            )
        ]


    def __str__(self) -> str:
        """Возвращает строковое представление избранного маршрута пользователя."""
        return (f'User {self.user.user_id}, favorite bus - {self.bus.bus_number} '
                f'at {self.favorite_time}')

