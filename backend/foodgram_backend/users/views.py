import djoser.views
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from .models import Follow, User
from .mixins import ListCreateDestroyViewSet
from .permissions import AuthorOrAdminOrReadOnly, Admin
from .serializers import (
    CreateUserSerializer,
    FollowSerializer,
    FollowCreateSerializer,
    FollowOutputSerializer,
    ExistingUserSerializer
)
from recipes.models import Recipe


class UserViewSet(djoser.views.UserViewSet):
    queryset = User.objects.all()
    pagination_class = PageNumberPagination

    def get_permissions(self):
        if self.action in ('list', 'retrieve', 'create'):
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


class FollowOnUserViewSet(ListCreateDestroyViewSet):
    """Создание подписки."""
    serializer_class = FollowSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = PageNumberPagination
    pagination_class.page_size = 6
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
        if Follow.objects.filter(
                user=self.request.user, author=author
        ).exists():
            return Response(
                'Подписка уже существует',
                status=status.HTTP_400_BAD_REQUEST
            )

        data = {
            'user': request.user.id,
            'author': author.id
        }
        serializer = FollowCreateSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        context = {
            'request': request,
            'id': id,
            'email': author.email,
            'username': author.username,
            'first_name': author.first_name,
            'last_name': author.last_name,
            'recipes_count': Recipe.objects.filter(author=author).count()
        }
        serializer_output = FollowOutputSerializer(
            data={'id': id},
            context=context
        )
        serializer_output.is_valid(raise_exception=True)

        return Response(
            data=serializer_output.data,
            status=status.HTTP_201_CREATED
        )

    @action(methods=['delete'], detail=False)
    def delete(self, request, **kwargs):
        id = self.kwargs.get('user_id')
        author = get_object_or_404(User, id=id)
        if not Follow.objects.filter(
                user=self.request.user, author=author
        ).exists():
            return Response(
                'Нечего удалять. Вы не подписаны на этого пользователя',
                status=status.HTTP_400_BAD_REQUEST
            )
        Follow.objects.filter(user=self.request.user, author=author).delete()
        return Response('Подписка отменена')
