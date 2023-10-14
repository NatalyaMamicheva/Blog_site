from django.urls import path
from .views import change_moderator_status, ModeratorPage, Ban, Unban

app_name = 'moderation'


urlpatterns = [
    path('moderator_page', ModeratorPage.as_view(), name='moderator_page'),
    path('change_moderator_status/<int:pk>/', change_moderator_status, name='change_moderator_status'),
    path('ban/<str:model>/<int:pk>', Ban.as_view(), name='ban'),
    path('unban/<str:model>/<int:pk>', Unban.as_view(), name='unban'),
               ]