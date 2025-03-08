from django.db import models
from django.core.validators import MinValueValidator

class Driver(models.Model):
    
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    last_name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, null=True, blank=True)
    address = models.CharField(max_length=1000, null=True, blank=True)
    driving_license = models.CharField(max_length=100, null=True, blank=True)
    fournisseur = models.ForeignKey('report.Fournisseur', on_delete=models.CASCADE, limit_choices_to={'is_tracked': True}, related_name='drivers')
    
    def __str__(self):
        return f'{self.last_name} {self.first_name}'

class Vehicle(models.Model):
    
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    model = models.CharField(max_length=100, null=True, blank=True)
    mark = models.CharField(max_length=100, null=True, blank=True)
    immatriculation = models.CharField(max_length=100)
    year = models.IntegerField(validators=[MinValueValidator(1900)], null=True, blank=True)
    fournisseur = models.ForeignKey('report.Fournisseur', on_delete=models.CASCADE, limit_choices_to={'is_tracked': True}, related_name='vehicles')
    objectif = models.FloatField(validators=[MinValueValidator(0)])
    consommation_with = models.FloatField(validators=[MinValueValidator(0)])
    consommation_without = models.FloatField(validators=[MinValueValidator(0)])


    def __str__(self):
        return self.immatriculation
    
class Distance(models.Model):

    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    site = models.ForeignKey('account.Site', on_delete=models.CASCADE, related_name='distances')
    emplacement = models.ForeignKey('report.Emplacement', on_delete=models.CASCADE, related_name='distances')
    distance = models.FloatField(validators=[MinValueValidator(0)])

    def __str__(self):
        return f'{self.site.designation} to {self.emplacement.designation} - {self.distance}KM'
    
class Cost(models.Model):

    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    fournisseur = models.ForeignKey('report.Fournisseur', on_delete=models.CASCADE, limit_choices_to={'is_tracked': True}, related_name='costs')
    min_km = models.FloatField(validators=[MinValueValidator(0)])
    max_km = models.FloatField(validators=[MinValueValidator(0)])
    tarif = models.FloatField(validators=[MinValueValidator(0)])

    def __str__(self):
        return f'{self.min_km} to {self.max_km} - {self.tarif} DZD'
    