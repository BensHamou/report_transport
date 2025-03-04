from django.db import models
from django.core.validators import MinValueValidator

class Driver(models.Model):
    
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    last_name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=1000, null=True)
    driving_license = models.CharField(max_length=100)
    fournisseur = models.ForeignKey('report.Fournisseur', on_delete=models.CASCADE, limit_choices_to={'is_tracked': True})
    
    def __str__(self):
        return f'{self.last_name} {self.first_name}'

class Vehicle(models.Model):
    
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    model = models.CharField(max_length=100)
    mark = models.CharField(max_length=100)
    immatriculation = models.CharField(max_length=100)
    year = models.IntegerField(validators=[MinValueValidator(1900)])
    fournisseur = models.ForeignKey('report.Fournisseur', on_delete=models.CASCADE, limit_choices_to={'is_tracked': True})
    objectif = models.FloatField(validators=[MinValueValidator(0)])
    consommation_with = models.FloatField(validators=[MinValueValidator(0)])
    consommation_without = models.FloatField(validators=[MinValueValidator(0)])


    def __str__(self):
        return f'{self.mark} {self.model} - {self.immatriculation}'
    