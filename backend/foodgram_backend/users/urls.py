from django.urls import path, include
from rest_framework import routers

from .views import (
    FollowOnUserViewSet,
    UserViewSet
)

app_name = 'users'

router = routers.DefaultRouter()
router.register(
    'users/subscriptions',
    FollowOnUserViewSet,
    basename='subscriptions'
)
router.register('users', UserViewSet, basename='users')
router.register(
    r'users/(?P<user_id>\d+)/subscribe',
    FollowOnUserViewSet,
    basename='following'
)
urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),

]
