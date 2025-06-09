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
    designation = models.CharField(max_length=100, null=True, blank=True)
    model = models.CharField(max_length=100, null=True, blank=True)
    mark = models.CharField(max_length=100, null=True, blank=True)
    immatriculation = models.CharField(max_length=100)
    year = models.IntegerField(validators=[MinValueValidator(1900)], null=True, blank=True)
    fournisseur = models.ForeignKey('report.Fournisseur', on_delete=models.CASCADE, limit_choices_to={'is_tracked': True}, related_name='vehicles')
    objectif = models.FloatField(validators=[MinValueValidator(0)])
    consommation_with = models.FloatField(validators=[MinValueValidator(0)])
    consommation_without = models.FloatField(validators=[MinValueValidator(0)])
    dotation = models.FloatField(validators=[MinValueValidator(0)], default=0, blank=True, null=True)


    def __str__(self):
        if self.designation:
            return f'{self.immatriculation} - {self.designation}'
        
        return f'{self.immatriculation}'
    
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
    
class ReparationType(models.Model):

    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    designation = models.CharField(max_length=100)

    def __str__(self):
        return self.designation

class Reparation(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='reparations')
    reparation_type = models.ForeignKey(ReparationType, on_delete=models.CASCADE, related_name='reparations')
    reparation_date = models.DateField()
    amount = models.FloatField(validators=[MinValueValidator(0)], null=True, blank=True)
    observation = models.TextField(null=True, blank=True)

    def __str__(self):
        return f'{self.vehicle.immatriculation} - {self.reparation_type.designation} le {self.reparation_date}'

class FuelRefill(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='fuel_refills')
    driver = models.ForeignKey(Driver, null=True, on_delete=models.SET_NULL, blank=True, related_name='fuel_refills')
    refill_date = models.DateField()
    km = models.FloatField(validators=[MinValueValidator(0)])
    amount = models.FloatField(validators=[MinValueValidator(0)], null=True, blank=True)
    observation = models.TextField(null=True, blank=True)

    def __str__(self):
        return f'Recharge - {self.vehicle.immatriculation} le {self.refill_date}'

class Assurance(models.Model):

    INSUTANCE_CHOICES = [
        ('Assurance', 'Assurance'),
        ('Vignette', 'Vignette'),
        ('Contrôle Technique', 'Contrôle Technique')
    ]

    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    type = models.CharField(choices=INSUTANCE_CHOICES, max_length=20)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='assurances')
    assurance_date = models.DateField()
    assurance_expiry_date = models.DateField()
    observation = models.TextField(null=True, blank=True)

    def __str__(self):
        return f'{self.vehicle.immatriculation} - {self.type} du {self.assurance_date} au {self.assurance_expiry_date}'

class MissionCostType(models.Model):

    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    designation = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.designation
    
class MissionCost(models.Model):

    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    mission_date = models.DateField()
    driver = models.ForeignKey(Driver, null=True, on_delete=models.SET_NULL, blank=True, related_name='mission_costs')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='mission_costs')
    from_emplacement = models.ForeignKey('account.Site', on_delete=models.CASCADE, related_name='mission_costs_from')
    to_emplacement = models.ForeignKey('report.Emplacement', on_delete=models.CASCADE, related_name='mission_costs_to')
    types = models.ManyToManyField(MissionCostType, blank=True)
    amount = models.FloatField(validators=[MinValueValidator(0)], null=True, blank=True)
    observation = models.TextField(null=True, blank=True)

    def __str__(self):
        return f'Mission le {self.mission_date} - {self.vehicle.immatriculation} de {self.from_emplacement.designation} à {self.to_emplacement.designation}'

class MasseSalariale(models.Model):

    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='masse_salariales')
    month = models.DateField()
    amount = models.FloatField(validators=[MinValueValidator(0)], null=True, blank=True)

    def __str__(self):
        return f'Masse Salariale - {self.vehicle.immatriculation} pour le mois de {self.month.strftime("%B %Y")} - {self.amount} DZD'