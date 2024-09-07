from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.ChatRoomListView.as_view(), name='room_list'),
    path('<int:pk>/', views.ChatRoomDetailView.as_view(), name='room_detail'),
    path('create/group/', views.CreateGroupChatView.as_view(), name='create_group'),
    path('search-users/', views.search_users, name='search_users'),
    path('create/', views.CreateChatView.as_view(), name='create_chat'),
]
