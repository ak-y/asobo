from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('main', views.main, name='main'),
    path('request', views.request, name='request'),
    path('todolist', views.todolist, name='todolist'),
    path('delete/<int:pk>', views.delete, name='delete'),
    path('requester_main/<str:crypted_id>', views.requester_main, name='requester_main'),
    path('authorize_requester', views.authorize_requester, name='authorize_requester'),
    path('authorize', views.authorize, name='authorize'),
    path('oauth2callback', views.oauth2callback, name='oauth2callback'),
]
