from django.urls import path
from .views import UserDetailView, UserCreateView, UserUpdateView, UserDeleteView, UserLoginView
from django.contrib.auth.views import LogoutView


app_name = 'auth'

urlpatterns = [
    path('logout/', LogoutView.as_view(), name='logout'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('profile/<int:pk>/', UserDetailView.as_view(), name='users_detail'),
    path('reg/', UserCreateView.as_view(), name='users_create'),
    path('edit/', UserUpdateView.as_view(), name='users_update'),
    path('remove/', UserDeleteView.as_view(), name='users_remove'),
]
