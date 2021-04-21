from rest_framework.routers import DefaultRouter
from django.urls import path, include

from .views import ReviewRetrieveUpdateDestroyAPIView, CategoryViewSet, \
    GenreViewSet, TitleViewSet, CommentRetrieveUpdateDestroyAPIView, \
    ReviewListCreateSet, CommentListCreateSet

from .views import UserViewSet, get_jwt_token, send_confirm_code

router_v1 = DefaultRouter()
router_v1.register(r'users', UserViewSet, basename='users')
router_v1.register(r'categories', CategoryViewSet, basename='category')
router_v1.register(r'genres', GenreViewSet, basename='genre')
router_v1.register(r'titles', TitleViewSet, basename='title')
router_v1.register(r'titles/(?P<title_id>\d+)/reviews',
                   ReviewListCreateSet,
                   basename='comments')
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentListCreateSet,
    basename='comments')

v1_auth_patterns = [
    path('token/', get_jwt_token, name='get_token'),
    path('email/', send_confirm_code, name='send_email'),
]

urlpatterns = [
    path('v1/', include(router_v1.urls)),
    path('v1/auth/', include(v1_auth_patterns)),
]

urlpatterns += [
    path('v1/titles/<int:title_id>/reviews/<int:review_id>/',
         ReviewRetrieveUpdateDestroyAPIView.as_view(),
         name='review'),
    path(
        'v1/titles/<int:title_id>/reviews/<int:review_id>/'
        'comments/<int:comment_id>/',
        CommentRetrieveUpdateDestroyAPIView.as_view(),
        name='review'),
]
