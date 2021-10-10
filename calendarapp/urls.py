from django.urls import path
from . import views

urlpatterns = [
    path('register', views.register, name='register'),
    path('signin', views.signin, name='signin'),
    path('main', views.main, name='main'),
    path('request', views.request, name='request'),
    path('signout', views.signout, name='signout'),
    path('requester_main', views.requester_main, name='requester_main'),
    path('authorize', views.authorize, name='authorize'),
    path('oauth2callback', views.oauth2callback, name='oauth2callback'),
    path('index', views.index, name='index'),
]
