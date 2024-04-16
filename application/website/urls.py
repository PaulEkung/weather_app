from django.urls import path
from . import views

urlpatterns = [
    path('', views.WeatherData),
    path('chat/', views.chatBot),
]