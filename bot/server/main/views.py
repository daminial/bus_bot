"""Этот модуль реализует API для управления списком избранных маршрутов пользователей."""

from django.db import DatabaseError, transaction
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from bot.server.main.models import Bus, User, UserFavorite

@api_view(['GET'])
def get_all_users(request):
    """Возвращает список всех user_id из таблицы users."""
    try:
        user_ids = User.objects.values_list('user_id', flat=True)
        return Response({'user_ids': list(user_ids)})
    except DatabaseError:
        return Response(
            'Ошибка базы данных',
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

@api_view(['GET'])
def get_favorite(request, user_id):
    """Возвращает избранные маршруты конкретного пользователя."""
    try:
        favorites = UserFavorite.objects.filter(user__user_id=user_id).select_related('bus')
        
        result = [
            {
                'bus_number': fav.bus.bus_number,
                'favorite_time': fav.favorite_time,
            }
            for fav in favorites
        ]
        
        return Response({'favorites': result})
    
    except DatabaseError:
        return Response(
            'Ошибка базы данных',
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
@api_view(['PATCH'])
def update_favorite_time(request, user_id, bus_number):
    """Добавляет или обновляет время для избранного маршрута."""
    favorite_time = request.data.get('favorite_time', '')
    
    if not favorite_time:
        return Response(
            {'error': 'favorite_time обязателен'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    try:
        with transaction.atomic():
            favorite, created = UserFavorite.objects.get_or_create(
                user__user_id=user_id,
                bus__bus_number=bus_number,
                defaults={
                    'user_id': user_id,
                    'bus_id': bus_number,
                    'favorite_time': favorite_time
                }
            )
            
            if not created:
                favorite.favorite_time = favorite_time
                favorite.save()

            return Response({
                'status': 'added' if created else 'updated',
                'favorite_time': favorite_time,
            })

    except DatabaseError:
        return Response(
            'Ошибка базы данных',
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def get_favorite_status(request, user_id, bus_number):
    """Проверяет, есть ли маршрут в избранном."""
    try:
        exists = UserFavorite.objects.filter(
            user__user_id=user_id,
            bus__bus_number=bus_number,
        ).exists()

        if exists:
            favorite = UserFavorite.objects.get(
                user__user_id=user_id,
                bus__bus_number=bus_number,
            )
            return Response({
                'exists': True,
                'favorite_time': favorite.favorite_time,
            })
        return Response({'exists': False})

    except DatabaseError:
        return Response('Ошибка базы данных', status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def add_favorite_route(request):
    """Добавляет маршрут в избранное."""
    user_id = request.data.get('user_id')
    bus_number = request.data.get('bus_number')
    favorite_time = request.data.get('favorite_time', '')

    if not user_id or not bus_number:
        return Response(
            {'error': 'user_id и bus_number обязательны'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        with transaction.atomic():
            user, _ = User.objects.get_or_create(user_id=user_id)
            bus, _ = Bus.objects.get_or_create(bus_number=bus_number)

            UserFavorite.objects.create(
                user=user,
                bus=bus,
                favorite_time=favorite_time,
            )
            return Response(status=status.HTTP_201_CREATED)

    except DatabaseError:
        return Response('Ошибка базы данных', status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
def remove_favorite_route(request, user_id, bus_number):
    """Удаляет маршрут из избранного."""
    try:
        with transaction.atomic():
            deleted, _ = UserFavorite.objects.filter(
                user__user_id=user_id,
                bus__bus_number=bus_number,
            ).delete()

            return Response({
                'status': 'removed',
                'deleted': deleted,
            })

    except DatabaseError:
        return Response('Ошибка базы данных', status=status.HTTP_500_INTERNAL_SERVER_ERROR)
