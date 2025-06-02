from django.contrib import admin
from .models import *

admin.site.register(Vehicle)
admin.site.register(Driver)
admin.site.register(Distance)
admin.site.register(Cost)
admin.site.register(ReparationType)
admin.site.register(Reparation)
admin.site.register(FuelRefill)
admin.site.register(Assurance)