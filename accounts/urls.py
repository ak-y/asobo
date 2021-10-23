from django.urls import path, include
from . import views

app_name= 'accounts'

urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    path('register/', views.SignUpView.as_view(), name='register'),
    # path('delete/', views.delete, name='delete'),
    path('delete/', views.UserDeleteView.as_view(), name='delete'),
]