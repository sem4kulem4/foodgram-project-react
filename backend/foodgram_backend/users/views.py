import djoser.views
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import mixins

from .models import Follow, User
from .serializers import CreateUserSerializer, FollowSerializer, FollowOnUserSerializer, ExistingUserSerializer, \
    IsSubscribedSerializer


class UserViewSet(djoser.views.UserViewSet):
    queryset = User.objects.all()
    serializer_class = ExistingUserSerializer

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return ExistingUserSerializer
        return CreateUserSerializer


class FollowViewSet(viewsets.ModelViewSet):
    """Обработка подписок для GET-запросов."""
    serializer_class = FollowSerializer
    permission_classes = (permissions.IsAuthenticated,)
    http_method_names = ('get',)

    def get_queryset(self):
        current_user = self.request.user
        queryset = Follow.objects.filter(user=current_user)
        return queryset


class CreateDestroyViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    pass


class FollowOnUserViewSet(CreateDestroyViewSet):
    """Создание подписки."""
    serializer_class = FollowOnUserSerializer
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Follow.objects.all()

    def create(self, request, **kwargs):
        id = self.kwargs.get('user_id')
        author = get_object_or_404(User, id=id)
        if author == self.request.user:
            return Response('Невозможно подписаться на самого себя!', status=status.HTTP_400_BAD_REQUEST)
        if Follow.objects.filter(user=self.request.user, author=author).exists():
            return Response('Подписка уже существует', status=status.HTTP_400_BAD_REQUEST)
        Follow.objects.create(user=self.request.user, author=author)
        return Response('Подписка создана', status=status.HTTP_201_CREATED)

    @action(methods=['delete'], detail=False)
    def delete(self, request, **kwargs):
        id = self.kwargs.get('user_id')
        author = get_object_or_404(User, id=id)
        if not Follow.objects.filter(user=self.request.user, author=author).exists():
            return Response('Нечего удалять. Вы не подписаны на этого пользователя', status=status.HTTP_400_BAD_REQUEST)
        Follow.objects.filter(user=self.request.user, author=author).delete()
        return Response('Подписка отменена')
