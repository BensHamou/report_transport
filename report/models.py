from django.db import models
from django.core.validators import MinValueValidator
from account.models import User, Site

class Emplacement(models.Model):
 
    REGION = [
        ('Ouest', 'Ouest'),
        ('Est', 'Est'),
        ('Centre', 'Centre'),
        ('Centre/Ouest', 'Centre/Ouest'),
    ]

    designation = models.CharField(max_length=100)
    region = models.CharField(choices=REGION, max_length=20, default='Ouest')

    def prices(self):
        return Price.objects.filter(destination=self)

    def __str__(self):
        return self.designation

class Tonnage(models.Model):
    designation = models.CharField(max_length=100)

    def __str__(self):
        return self.designation

class Fournisseur(models.Model):
    designation = models.CharField(max_length=100)

    def prices(self):
        return self.price_set.all()
    
    def __str__(self):
        return self.designation
    
class Product(models.Model):
    designation = models.CharField(max_length=100)
    
    def __str__(self):
        return self.designation

class Price(models.Model):

    destination = models.ForeignKey(Emplacement, on_delete=models.CASCADE)
    depart = models.ForeignKey(Site, on_delete=models.CASCADE)
    fournisseur = models.ForeignKey(Fournisseur, on_delete=models.CASCADE)
    tonnage = models.ForeignKey(Tonnage, on_delete=models.CASCADE)
    price = models.FloatField(default=0, validators=[MinValueValidator(0)])

    def __str__(self):
        return "De '" + self.depart.designation + "' au '" + self.destination.designation + "', par " + self.fournisseur.designation + " - " + self.tonnage.designation + " / " + str(self.price) + "DA"
    
class Report(models.Model):
 
    STATE_REPORT = [
        ('Brouillon', 'Brouillon'),
        ('Confirmé', 'Confirmé'),
        ('Annulé', 'Annulé'),
    ]

    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    state = models.CharField(choices=STATE_REPORT, max_length=40)
    prix = models.ForeignKey(Price, null=True, on_delete=models.SET_NULL)
    date_dep = models.DateField()
    chauffeur = models.CharField(max_length=100)
    immatriculation = models.CharField(max_length=100, null=True, blank=True)
    n_bl = models.IntegerField(default=1, validators=[MinValueValidator(0)], null=True, blank=True)
    n_btr = models.IntegerField(default=1, validators=[MinValueValidator(0)], null=True, blank=True)    
    n_bl_2 = models.IntegerField(default=1, validators=[MinValueValidator(0)], null=True, blank=True)
    observation = models.TextField(null=True, blank=True)

    def ptransporteds(self):
        return self.ptransported_set.all()

    def __str__(self):
        return str(self.n_bl) + " (" + str(self.date_created) +")"
    
class PTransported(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE)
    
    product = models.ForeignKey(Product, null=True, on_delete=models.CASCADE)
    qte_transported = models.FloatField(default=0, validators=[MinValueValidator(0)])
    observation = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.product.designation + " (" + str(self.qte_transported) +")"