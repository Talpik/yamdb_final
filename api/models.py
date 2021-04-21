from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _


class UserRoles(models.TextChoices):
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'


class User(AbstractUser):
    """
    This is custom class for create User model, where email field instead
    username field.
    """

    username = models.CharField(_('username'),
                                max_length=30,
                                blank=True,
                                unique=True)
    email = models.EmailField(_('email address'), unique=True)
    bio = models.TextField(max_length=500, blank=True)
    role = models.CharField(
        verbose_name='Роль пользователя',
        max_length=10,
        choices=UserRoles.choices,
        default=UserRoles.USER,
    )
    confirmation_code = models.CharField(max_length=10, default='FOOBAR')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', )

    @property
    def is_admin(self):
        """
        Function for quick change property 'role' of User model.
        """
        return (self.role == UserRoles.ADMIN or self.is_superuser
                or self.is_staff)

    @property
    def is_moderator(self):
        """
        Function for quick change property 'role' of User model.
        """
        return self.role == UserRoles.MODERATOR

    def get_full_name(self):
        """
        Function for concatinate full name of user, use firlst and last name.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()


class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=300)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=300)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(max_length=200)
    year = models.PositiveIntegerField(null=True, blank=True, db_index=True)
    description = models.CharField(max_length=400, blank=True)
    genre = models.ManyToManyField(Genre, blank=True)
    category = models.ForeignKey(Category,
                                 blank=True,
                                 null=True,
                                 on_delete=models.SET_NULL,
                                 related_name='titles')

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.name

    @property
    def rating(self):
        reviews = self.reviews.all()
        score_avg = reviews.aggregate(models.Avg('score')).get('score__avg')
        return None if score_avg is None else int(score_avg)


class Review(models.Model):
    title = models.ForeignKey(Title,
                              on_delete=models.CASCADE,
                              related_name='reviews')
    text = models.TextField()
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='reviews')
    score = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0),
                    MaxValueValidator(10)])
    pub_date = models.DateTimeField('date published',
                                    auto_now_add=True,
                                    db_index=True)

    class Meta:
        ordering = ['pub_date']

    def __str__(self):
        return f'{self.title}, {self.score}, {self.author}'


class Comment(models.Model):
    review = models.ForeignKey(Review,
                               on_delete=models.CASCADE,
                               related_name='comments')
    text = models.TextField()
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='comments')
    pub_date = models.DateTimeField('date published',
                                    auto_now_add=True,
                                    db_index=True)

    class Meta:
        ordering = ['pub_date']

    def __str__(self):
        return f'{self.author}, {self.pub_date:%d.%m.%Y}, {self.text[:50]}'
