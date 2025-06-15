from django.urls import path
from . import views

urlpatterns = [
    path('', views.getRoute),
    path('rooms/', views.getRooms),
    path('room/<str:pk>', views.getRoom)
]
