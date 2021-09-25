from django.db import models

# Create your models here.
class User(models.Model):
    user_id = models.IntegerField()
    name = models.CharField(max_length=15)
    password = models.CharField(max_length=15)
    mail_address = models.CharField(max_length=30)
