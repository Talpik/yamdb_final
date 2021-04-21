from rest_framework import serializers

from .models import Comment, Review, Title, Category, Genre
from .models import User


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for view-class, who work with next end-points:
    1)'api/v1/users/', [GET, POST], permission=(AllowAny)
    2)'api/v1/users/{username}/', [GET, PATCH, DELETE], permission=(IsAdmin)
    3)'api/v1/users/me/', [GET, PATCH], permission=(IsOwner)
    """
    class Meta:
        model = User
        fields = (
            'bio',
            'first_name',
            'last_name',
            'username',
            'email',
            'role',
        )


class UserCreationSerializer(serializers.Serializer):
    """
    Serializer for view-class, who work with next end-points:
    'api/v1/auth/email/', [POST], permissions=(AllowAny)
    Sending confirmation_code to the transmitted email.
    """

    email = serializers.CharField()
    username = serializers.CharField()

    class Meta:
        model = User
        fields = (
            'username',
            'email',
        )


class ConfirmationCodeSerializer(serializers.Serializer):
    """
    Serializer for view-class, who work with next end-points:
    'api/v1/auth/token/', [POST], permissions=(AllowAny)
    Receiving a JWT token in exchange for email and confirmation_code.
    """
    email = serializers.CharField()
    confirmation_code = serializers.CharField(allow_blank=False,
                                              write_only=True)

    class Meta:
        model = User
        fields = (
            'confirmation_code',
            'email',
        )


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        exclude = ('id', )


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        exclude = ('id', )


class CategoryField(serializers.SlugRelatedField):
    def to_representation(self, value):
        serializer = CategorySerializer(value)
        return serializer.data


class GenreField(serializers.SlugRelatedField):
    def to_representation(self, value):
        serializer = GenreSerializer(value)
        return serializer.data


class TitleSerializer(serializers.ModelSerializer):
    category = CategoryField(slug_field='slug',
                             queryset=Category.objects.all(),
                             required=False)
    genre = GenreField(slug_field='slug',
                       queryset=Genre.objects.all(),
                       many=True)

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'rating', 'description', 'genre',
                  'category')


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
    )
    review = serializers.PrimaryKeyRelatedField(read_only=True, )
    title = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
    )
    title = serializers.SlugRelatedField(slug_field='name', read_only=True)

    def validate_score(self, score):
        if score < 1 or score > 10:
            raise serializers.ValidationError('Оценка должна между 1 и 10.')
        return score

    def validate_review(self, text):
        if text == "":
            raise serializers.ValidationError("Отзыв не может быть пустым.")

    class Meta:
        model = Review
        fields = '__all__'
