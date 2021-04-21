from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import filters, status, viewsets, mixins
from rest_framework.permissions import IsAuthenticatedOrReadOnly, \
    IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.decorators import action, api_view, permission_classes

from .models import Category, Genre, Title, Review, User

from .permissions import IsAdmin, IsAnon, IsModerator, IsAdminOrReadOnly, \
    RetrieveUpdateDestroyPermission, MyCustomPermissionClass, \
    IsAdminPermissions

from .filters import TitlesFilter

from .serializers import CategorySerializer, GenreSerializer, \
    ReviewSerializer, CommentSerializer, TitleSerializer, UserSerializer, \
    ConfirmationCodeSerializer, UserCreationSerializer

EMAIL_AUTH = 'authorization@yamdb.fake'


@api_view(['POST'])
@permission_classes([AllowAny])
def get_jwt_token(request):
    """
    Receiving a JWT token in exchange for email and confirmation_code.
    """
    serializer = ConfirmationCodeSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    email = serializer.data.get('email')
    confirmation_code = serializer.data.get('confirmation_code')
    user = get_object_or_404(User, email=email)
    if default_token_generator.check_token(user, confirmation_code):
        token = default_token_generator.make_token(user)
        return Response({'token': str(token)}, status=status.HTTP_200_OK)
    return Response({'confirmation_code': 'Неверный код подтверждения'},
                    status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def send_confirm_code(request):
    """
    Sending confirmation_code to the transmitted email.
    Get or Creating an User object.
    """

    serializer = UserCreationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.data['email']
    username = serializer.data['username']
    user = User.objects.get_or_create(
        email=email,
        username=username,
    )
    confirmation_code = default_token_generator.make_token(user)
    send_mail(subject='Yours confirmation code',
              message=f'confirmation_code: {confirmation_code}',
              from_email=EMAIL_AUTH,
              recipient_list=(email, ),
              fail_silently=False)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    """
    1) [GET] Get list of users objects. [POST] Create user object. 'users/'
    2) [GET]Get user object by username. [PATCH] Patch user data by username.
    [DELETE] Delete user object by username. 'users/{username}/'
    3) [GET] Get your account details. [PATCH] Change your account details.
    'users/me/'
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminPermissions]
    lookup_field = 'username'

    @action(methods=['GET', 'PATCH'],
            detail=False,
            permission_classes=(IsAuthenticated, ),
            url_path='me')
    def me(self, request):
        user_profile = get_object_or_404(User, email=self.request.user.email)
        if request.method == 'GET':
            serializer = UserSerializer(user_profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = UserSerializer(user_profile,
                                    data=request.data,
                                    partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class CategoryViewSet(viewsets.ModelViewSet):
    permission_classes = (
        MyCustomPermissionClass,
        IsAuthenticatedOrReadOnly,
    )
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    def get_queryset(self):
        categories = Category.objects.all()
        return categories

    def retrieve(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def partial_update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class GenreViewSet(viewsets.ModelViewSet):
    permission_classes = (
        MyCustomPermissionClass,
        IsAuthenticatedOrReadOnly,
    )
    serializer_class = GenreSerializer
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    def get_queryset(self):
        genres = Genre.objects.all()
        return genres

    def retrieve(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def partial_update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all().annotate(ratings=Avg('reviews__score'))
    serializer_class = TitleSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = TitlesFilter


class ReviewListCreateSet(mixins.ListModelMixin, mixins.CreateModelMixin,
                          viewsets.GenericViewSet):
    permission_classes = [IsAnon | IsAdmin | IsModerator | IsAuthenticated]
    serializer_class = ReviewSerializer

    def perform_create(self, serializer):
        author = self.request.user
        text = self.request.data.get('text')

        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)

        reviews = Review.objects.filter(author=author, title=title)
        if reviews.count() > 0:
            return True

        serializer.save(title=title, author=author, text=text)

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        queryset = title.reviews.all()
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        not_create_success = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        if not_create_success:
            return Response(serializer.data,
                            status=status.HTTP_400_BAD_REQUEST,
                            headers=headers)
        else:
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED,
                            headers=headers)


class ReviewRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [
        RetrieveUpdateDestroyPermission,
    ]

    def get_object(self):
        obj = get_object_or_404(self.get_queryset(),
                                pk=self.kwargs['review_id'])
        self.check_object_permissions(self.request, obj)
        return obj

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        queryset = title.reviews.all()
        return queryset


class CommentListCreateSet(mixins.ListModelMixin, mixins.CreateModelMixin,
                           viewsets.GenericViewSet):
    permission_classes = [IsAnon | IsAdmin | IsModerator | IsAuthenticated]
    serializer_class = CommentSerializer

    def perform_create(self, serializer):
        author = self.request.user
        text = self.request.data.get('text')

        title_id = self.kwargs.get('title_id')
        review_id = self.kwargs.get('review_id')
        title = get_object_or_404(Title, id=title_id)
        review = get_object_or_404(title.reviews, id=review_id)
        serializer.save(review=review, author=author, text=text)

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        review_id = self.kwargs.get('review_id')
        title = get_object_or_404(Title, id=title_id)
        review = get_object_or_404(title.reviews.all(), id=review_id)
        queryset = review.comments.all()
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        not_create_success = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        if not_create_success:
            return Response(serializer.data,
                            status=status.HTTP_400_BAD_REQUEST,
                            headers=headers)
        else:
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED,
                            headers=headers)


class CommentRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = CommentSerializer
    permission_classes = [
        RetrieveUpdateDestroyPermission,
    ]

    def get_object(self):
        obj = get_object_or_404(self.get_queryset(),
                                pk=self.kwargs['comment_id'])
        self.check_object_permissions(self.request, obj)
        return obj

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        review_id = self.kwargs.get('review_id')
        title = get_object_or_404(Title, id=title_id)
        review = get_object_or_404(title.reviews.all(), id=review_id)
        queryset = review.comments.all()
        return queryset
