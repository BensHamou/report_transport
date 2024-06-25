from django.db import models
from django.core.validators import MinValueValidator
from account.models import User, Site
from report.models import Fournisseur, Product, Tonnage, Emplacement

class Setting(models.Model):
    name = models.CharField(max_length=50)
    value = models.CharField(max_length=250)

    def __str__(self):
        return self.name + ' : ' + self.value

class Livraison(models.Model):
    designation = models.CharField(max_length=50)

    def __str__(self):
        return self.designation

class Planning(models.Model):
 
    STATE_PLANNING = [
        ('Brouillon', 'Brouillon'),
        ('Planning', 'Planning'),
        ('Planning en Attente', 'Planning en Attente'),
        ('Planning Confirmé', 'Planning Confirmé'),
        ('Livraison Confirmé', 'Livraison Confirmé'),
        ('Raté', 'Raté'),
        ('Annulé', 'Annulé')
    ]

    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    state = models.CharField(choices=STATE_PLANNING, max_length=40)

    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    date_planning = models.DateField()

    distributeur_id = models.IntegerField()
    distributeur = models.CharField(max_length=255)

    client_id = models.IntegerField()
    client = models.CharField(max_length=255)

    tonnage = models.ForeignKey(Tonnage, on_delete=models.CASCADE, null=True, blank=True)
    destination = models.ForeignKey(Emplacement, on_delete=models.CASCADE)
    livraison = models.ForeignKey(Livraison, on_delete=models.CASCADE)
    observation_comm = models.TextField(null=True, blank=True)

    fournisseur = models.ForeignKey(Fournisseur, on_delete=models.CASCADE, null=True)
    chauffeur = models.CharField(max_length=100, null=True, blank=True)
    immatriculation = models.CharField(max_length=100, null=True, blank=True)
    date_honored = models.DateField(null=True, blank=True)
    n_bl = models.CharField(max_length=100, null=True, blank=True)
    is_marked = models.BooleanField(default=False)
    observation_logi = models.TextField(null=True, blank=True)

    def pplanneds(self):
        return self.pplanned_set.all()
    
    def validations(self):
        return self.validation_set.all()

    def __str__(self):
        return f"{self.site.planning_prefix}{self.id:05d}/{self.date_planning.strftime('%y')}"
    
class PPlanned(models.Model):
    planning = models.ForeignKey(Planning, on_delete=models.CASCADE)
    
    product = models.ForeignKey(Product, null=True, on_delete=models.CASCADE)
    palette = models.FloatField(default=0, validators=[MinValueValidator(0)])

    def __str__(self):
        return self.product.designation + " (" + str(self.palette) +")"
    
class Validation(models.Model):

    STATE_PLANNING = [
        ('Brouillon', 'Brouillon'),
        ('Planning', 'Planning'),
        ('Planning en Attente', 'Planning en Attente'),
        ('Planning Confirmé', 'Planning Confirmé'),
        ('Livraison Confirmé', 'Livraison Confirmé'),
        ('Raté', 'Raté'),
        ('Annulé', 'Annulé')
    ]

    old_state = models.CharField(choices=STATE_PLANNING, max_length=40)
    new_state = models.CharField(choices=STATE_PLANNING, max_length=40)
    date = models.DateTimeField(auto_now_add=True) 
    actor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    miss_reason = models.TextField()
    planning = models.ForeignKey(Planning, on_delete=models.CASCADE)

    def __str__(self):
        return "Validation - " + str(self.planning.id) + " - " + str(self.date)