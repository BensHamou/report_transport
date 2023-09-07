from django.db import models
from django.contrib.auth.models import AbstractUser

class Line(models.Model):
    designation = models.CharField(max_length=100)
    
    def products(self):
        return self.product_set.all()

    def __str__(self):
        return self.designation

class User(AbstractUser):

    username = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    fullname = models.CharField(max_length=255)
    is_admin = models.BooleanField(default=False)
    lines = models.ManyToManyField(Line, blank=True)

    fields = ('username', 'fullname', 'email', 'is_admin', 'first_name', 'last_name', 'lines')
    
    def __str__(self):
        return self.fullname

    class Meta(AbstractUser.Meta):
       swappable = 'AUTH_USER_MODEL'