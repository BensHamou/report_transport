from django.db import models
from django.core.validators import MinValueValidator
from account.models import User, Site
from report.models import Fournisseur, Product, Tonnage, Emplacement, Report
from fleet.models import Driver, Vehicle
from django.template.defaultfilters import slugify
from PIL import Image as PILImage
import os
import string
import random
from datetime import date, timedelta

class Setting(models.Model):
    name = models.CharField(max_length=50)
    value = models.CharField(max_length=250)

    def __str__(self):
        return self.name + ' : ' + self.value

class Livraison(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    designation = models.CharField(max_length=50)

    def __str__(self):
        return self.designation

class Blocked(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)

    distributeur_id = models.IntegerField()
    distributeur = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.distributeur} - {self.id}' 
    

class Planning(models.Model):
 
    STATE_PLANNING = [
        ('Brouillon', 'Brouillon'),
        ('Planning', 'Planning'),
        ('Planning en Attente', 'Planning en Attente'),
        ('Planning Confirmé', 'Planning Confirmé'),
        ('Livraison Confirmé', 'Livraison Confirmé'),
        ('Raté', 'Raté'),
        ('Planning Bloqué', 'Planning Bloqué'),
        ('Annulé', 'Annulé')
    ]

    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    state = models.CharField(choices=STATE_PLANNING, max_length=40)

    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    date_planning = models.DateField()
    date_replanning = models.DateField(null=True, blank=True)

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
    
    driver = models.ForeignKey(Driver, null=True, on_delete=models.SET_NULL, blank=True)
    vehicle = models.ForeignKey(Vehicle, null=True, on_delete=models.SET_NULL, blank=True)
    
    date_honored = models.DateField(null=True, blank=True)
    n_bl = models.IntegerField(validators=[MinValueValidator(0)], null=True, blank=True)
    n_invoice = models.IntegerField(validators=[MinValueValidator(0)], null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True, unique=True)
    google_maps_coords = models.CharField(max_length=255, blank=True, null=True)
    is_marked = models.BooleanField(default=False)
    supplier_informed = models.BooleanField(default=False)
    observation_logi = models.TextField(null=True, blank=True)


    report = models.ForeignKey(Report, on_delete=models.SET_NULL, null=True, blank=True)

    def pplanneds(self):
        return self.pplanned_set.all()
    
    @classmethod
    def generate_unique_code(cls):
        # chars = string.ascii_uppercase + string.digits
        chars = string.digits
        while True:
            code = ''.join(random.choices(chars, k=6))
            if not cls.objects.filter(code=code).exists():
                return code

    @property
    def date_planning_final(self):
        if self.date_replanning:
            return max(self.date_planning, self.date_replanning)
        return self.date_planning
    
    @property
    def is_delivered(self):
        return self.state == 'Livraison Confirmé' and self.files.exists()
    
    @property
    def date_delivered(self):
        if self.state == 'Livraison Confirmé':
            return self.validation_set.filter(new_state='Livraison Confirmé').order_by('date').last().date
        else:
            return None
    
    @property
    def is_missing_delivery_overdue(self):
        if self.date_honored:
            cutoff_date = date(2025, 10, 1)
            if self.date_honored < cutoff_date:
                return False
            return self.state == 'Livraison Confirmé' and not self.files.exists() and self.date_honored <= date.today() - timedelta(days=2)
        return False

    @property
    def str_chauffeur(self):
        if self.driver:
            return self.driver.__str__()
        return self.chauffeur

    @property
    def sequence(self):
        return self.__str__()

    @property
    def str_immatriculation(self):
        if self.vehicle:
            return self.vehicle.__str__()
        return self.immatriculation
    
    def validations(self):
        return self.validation_set.all()
    
    @property
    def delivery_date(self):
        if self.state == 'Livraison Confirmé':
            return self.validation_set.filter(new_state='Livraison Confirmé').order_by('date').last().date
        return None
    
    @property
    def files_state(self):
        if len(self.files.all()) == 0:
            return 'Aucun fichier'
        elif all(f.state == 'Approuvé' for f in self.files.all()):
            return 'Approuvé'
        elif any(f.state == 'Refusé' for f in self.files.all()):
            return 'Refusé'
        else:
            return 'En attente'
    
    @property
    def planning_files_state(self):
        if len(self.files.all()) == 0:
            return 'En attente'
        elif any(f.state == 'Refusé' for f in self.files.all()):
            return 'Refusé'
        else:
            return 'Approuvé'

    def __str__(self):
        return f"{self.site.planning_prefix}{self.id:05d}/{self.date_planning_final.strftime('%y')}"
    
class PPlanned(models.Model):
    planning = models.ForeignKey(Planning, on_delete=models.CASCADE)
    
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
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
    
def get_image_filename(instance, filename):
    pass

def get_upload_filename(instance, filename):
    title = instance.planning.id
    slug = slugify(title)
    return "planning_files/%s-%s" % (slug, filename)

class File(models.Model):
    STATE_FILE = [
        ('En attente', 'En attente'),
        ('Approuvé', 'Approuvé'),
        ('Refusé', 'Refusé')
    ]

    planning = models.ForeignKey(Planning, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to=get_upload_filename, verbose_name='Fichier')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    state = models.CharField(choices=STATE_FILE, max_length=20, default='En attente')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.file and os.path.exists(self.file.path):
            ext = os.path.splitext(self.file.name)[1].lower()
            if ext in ['.jpg', '.jpeg', '.png', '.webp']:
                try:
                    img = PILImage.open(self.file.path)
                    max_size = (1920, 1080)
                    img.thumbnail(max_size, PILImage.LANCZOS)
                    img.save(self.file.path, quality=80, optimize=True)
                except Exception:
                    pass
    
    def __str__(self):
        return f'File - Planning {self.planning.id} - {self.file.name} - {self.state}'

    
class FileValidation(models.Model):

    STATE_FILE = [
        ('En attente', 'En attente'),
        ('Approuvé', 'Approuvé'),
        ('Refusé', 'Refusé')
    ]

    old_state = models.CharField(choices=STATE_FILE, max_length=40)
    new_state = models.CharField(choices=STATE_FILE, max_length=40)
    date = models.DateTimeField(auto_now_add=True) 
    actor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    refusal_reason = models.TextField(null=True, blank=True)
    file = models.ForeignKey(File, on_delete=models.CASCADE, related_name='validations')

    def __str__(self):
        return "Validation - " + str(self.file.id) + " - " + str(self.date)
    
class Device(models.Model):
    DEVICE_TYPES = (('android','android'),('ios','ios'),('web','web'))
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='devices')
    token = models.CharField(max_length=512, unique=True)
    device_type = models.CharField(max_length=16, choices=DEVICE_TYPES, default='android')
    created_at = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user} - {self.device_type}'
    