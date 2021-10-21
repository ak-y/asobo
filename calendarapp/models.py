from django.db import models
from django.contrib.auth.models import User

class Request(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    requester_name = models.CharField(max_length=15)
    requester_mail_address = models.EmailField()
    message = models.CharField(max_length=100, blank=True)
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_accepted = models.BooleanField(null=True, blank=True)
    admin_message = models.CharField(max_length=100, blank=True)
    title = models.CharField(max_length=15)

    def __str__(self):
        return self.title


class Calendar(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    credentials = models.JSONField()


class Todolist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=15)
    url = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.title
