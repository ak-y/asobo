from django.contrib import admin
from .models import User, Request, Todolist

# Register your models here.

admin.site.register(Request)
admin.site.register(Todolist)
