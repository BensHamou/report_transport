from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator

class Site(models.Model):
    designation = models.CharField(max_length=100)
    address = models.CharField(max_length=250, null=True)
    prefix_site = models.CharField(max_length=6, blank=True, null=True)
    prefix_invocie_site = models.CharField(max_length=6, blank=True, null=True)
    btr_prefix_site = models.CharField(max_length=25, blank=True, null=True)
    planning_prefix = models.CharField(max_length=25, blank=True, null=True)
    include_cron = models.BooleanField(default=False)
    
    def products(self):
        return self.product_set.all()

    def __str__(self):
        return self.designation

class User(AbstractUser):

    ROLE_CHOICES = [
        ('Nouveau', 'Nouveau'),
        ('Logisticien', 'Logisticien'),
        ('Commercial', 'Commercial'),
        ('Observateur', 'Observateur'),
        ('Admin', 'Admin'),
    ]

    username = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    fullname = models.CharField(max_length=255)
    is_admin = models.BooleanField(default=False)
    role = models.CharField(choices=ROLE_CHOICES, max_length=30)
    sites = models.ManyToManyField(Site, blank=True)

    fields = ('username', 'fullname', 'email', 'is_admin', 'first_name', 'last_name', 'sites', 'role')
    
    def __str__(self):
        return self.fullname

    class Meta(AbstractUser.Meta):
       swappable = 'AUTH_USER_MODEL'