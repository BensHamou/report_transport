from django.db import models
from django.core.validators import MinValueValidator
from account.models import User

class Emplacement(models.Model):
    DESTINATION_CHOICES = (
        ('Déstination', 'Déstination'),
        ('Départ', 'Départ'),
    )

    designation = models.CharField(max_length=100)
    categ = models.CharField(max_length=20, choices=DESTINATION_CHOICES)

    def __str__(self):
        return self.designation

class Tonnage(models.Model):
    designation = models.CharField(max_length=100)

    def __str__(self):
        return self.designation

class Fournisseur(models.Model):
    designation = models.CharField(max_length=100)

    def __str__(self):
        return self.designation

class Price(models.Model):

    destination = models.ForeignKey(Emplacement, on_delete=models.CASCADE, limit_choices_to={'categ': 'Déstination'}, related_name='destination_prices')
    depart = models.ForeignKey(Emplacement, on_delete=models.CASCADE, limit_choices_to={'categ': 'Départ'}, related_name='depart_prices')
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
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    state = models.CharField(choices=STATE_REPORT, max_length=40)
    prix = models.ForeignKey(Price, null=True, on_delete=models.SET_NULL)
    date_dep = models.DateField()
    chauffeur = models.CharField(max_length=100)
    n_bl = models.IntegerField(default=1, validators=[MinValueValidator(0)])
    observation = models.TextField(null=True)

    def __str__(self):
        return str(self.n_bl) + " (" + str(self.date_created) +")"