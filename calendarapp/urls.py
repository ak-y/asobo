from django.urls import path
from . import views

# app_name = "calendarapp"
urlpatterns = [
    path('', views.index, name='index'),
    path('register', views.register, name='register'),
    path('signin', views.signin, name='signin'),
    path('main', views.main, name='main'),
    path('request', views.request, name='request'),
    path('signout', views.signout, name='signout'),
    path('requester_main/<str:crypted_id>', views.requester_main, name='requester_main'),
    path('authorize_requester', views.authorize_requester, name='authorize_requester'),
    path('authorize', views.authorize, name='authorize'),
    path('oauth2callback', views.oauth2callback, name='oauth2callback'),
]
