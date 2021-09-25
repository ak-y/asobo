from django.shortcuts import render
from .models import User

# Create your views here.
def register(request):
    return render(request, "calendarapp/register.html")

def index(request):
    all = User.objects.all()
    return render(request, "calendarapp/index.html", {
        "db": all
    })
