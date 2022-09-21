import djoser.views
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import mixins

from .models import Follow, User
from .paginations import PagePagination
from .permissions import AuthorOrAdminOrReadOnly, Admin
from .serializers import (
    CreateUserSerializer,
    FollowSerializer,
    ExistingUserSerializer
)


class UserViewSet(djoser.views.UserViewSet):
    queryset = User.objects.all()
    serializer_class = ExistingUserSerializer
    pagination_class = PagePagination

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return (permissions.AllowAny(),)
        if self.action in ('destroy',):
            return (Admin(),)
        return (AuthorOrAdminOrReadOnly(),)

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return ExistingUserSerializer
        return CreateUserSerializer

    def destroy(self, request, *args, **kwargs):
        user_id = kwargs.get('id')
        User.objects.get(id=user_id).delete()
        return Response(status=status.HTTP_200_OK)


class ListCreateDestroyViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    pass


class FollowOnUserViewSet(ListCreateDestroyViewSet):
    """Создание подписки."""
    serializer_class = FollowSerializer
    permission_classes = (permissions.IsAuthenticated,)
    http_method_names = ['get', 'post', 'delete']

    def get_queryset(self):
        current_user = self.request.user
        queryset = Follow.objects.filter(user=current_user)
        return queryset

    def create(self, request, **kwargs):
        id = self.kwargs.get('user_id')
        author = get_object_or_404(User, id=id)
        if author == self.request.user:
            return Response(
                'Невозможно подписаться на самого себя!',
                status=status.HTTP_400_BAD_REQUEST
            )
        if Follow.objects.filter(user=self.request.user, author=author).exists():
            return Response(
                'Подписка уже существует',
                status=status.HTTP_400_BAD_REQUEST
            )
        Follow.objects.create(user=self.request.user, author=author)
        return Response(
            'Подписка создана',
            status=status.HTTP_201_CREATED
        )

    @action(methods=['delete'], detail=False)
    def delete(self, request, **kwargs):
        id = self.kwargs.get('user_id')
        author = get_object_or_404(User, id=id)
        if not Follow.objects.filter(user=self.request.user, author=author).exists():
            return Response(
                'Нечего удалять. Вы не подписаны на этого пользователя',
                status=status.HTTP_400_BAD_REQUEST
            )
        Follow.objects.filter(user=self.request.user, author=author).delete()
        return Response('Подписка отменена')
