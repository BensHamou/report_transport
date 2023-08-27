from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):

    username = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    fullname = models.CharField(max_length=255)
    is_admin = models.BooleanField(default=False)

    fields = ('username', 'fullname', 'email', 'is_admin', 'first_name', 'last_name')
    
    def __str__(self):
        return self.fullname

    class Meta(AbstractUser.Meta):
       swappable = 'AUTH_USER_MODEL'