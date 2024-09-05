from django.urls import path
from .views import RoomListView

app_name = 'chat'

urlpatterns = [
    path('', RoomListView.as_view(), name='room_list'),
]
