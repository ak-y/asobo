from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import Request
from django.db import IntegrityError
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


# Create your views here.

def index(request):
    return render(request, 'calendarapp/index.html')


def register(request):
    if request.method == "POST":
        username =  request.POST['username']
        password = request.POST['password']
        try:
            User.objects.create_user(username, '', password)
            return redirect('signin')
        except IntegrityError:
            return render(request, 'calendarapp/register.html', {
                'error': 'このユーザーは既に登録されています'
            })
    return render(request, 'calendarapp/register.html')


def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('main')
        else:
            return redirect('signin')
    return render(request, 'calendarapp/signin.html')


# @login_required
def main(request):
#     requests = Request.objects.all()
#     users = User.objects.all()
    return render(request, 'calendarapp/main.html', {
#         'requests': requests,
#         'users': users
    })


@login_required
def request(request):
    pass


def signout(request):
    logout(request)
    return redirect('signin')


def requester_main(request):
    pass
