from django.shortcuts import render
from .models import User

# Create your views here.
def index(request):
    all = User.objects.all()
    return render(request, "calendarapp/index.html", {
        "db": all
    })

def register(request):
    pass

def login(request):
    pass

def main(request):
    pass

def request(request):
    pass

def requester_main(request):
    pass
