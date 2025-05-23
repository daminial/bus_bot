from django.urls import path

from . import views

app_name = 'main'

urlpatterns = [
    path('favorites/<int:user_id>/<str:bus_number>/', views.get_favorite_status),
    path('favorites/add/', views.add_favorite_route),
    path('favorites/remove/<int:user_id>/<str:bus_number>/', views.remove_favorite_route),
    path('favorites/update/<int:user_id>/<str:bus_number>/', views.update_favorite_time),
    path('favorites/user/<int:user_id>/', views.get_favorite),
    path('users/all/', views.get_all_users),
]
