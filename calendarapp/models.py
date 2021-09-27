from django.db import models

# Create your models here.
class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=15)
    password = models.CharField(max_length=15)
    mail_address = models.EmailField()

    def __str__(self):
        return self.name

class Request(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    request_id = models.AutoField(primary_key=True)
    requester_name = models.CharField(max_length=15)
    requester_mail_address = models.EmailField()
    message = models.CharField(max_length=100, blank=True)
    start_at = models.DateField()
    end_at = models.DateField()
    created_at = models.DateField(auto_now_add=True)
    is_accepted = models.BooleanField()
    admin_message = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.requester_name
