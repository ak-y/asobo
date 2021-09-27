from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register', views.register, name='register'),
    path('login', views.login, name='login'),
    path('main', views.main, name='main'),
    path('request', views.request, name='request'),
    path('requester_main', views.requester_main, name='requester_main'),
]
