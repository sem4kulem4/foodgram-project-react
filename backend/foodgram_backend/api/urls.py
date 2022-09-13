from django.urls import path, include
from rest_framework import routers

app_name = 'api'


urlpatterns = [
   path('', include('users.urls', namespace='users')),
   path('', include('recipes.urls', namespace='recipes'))
]
