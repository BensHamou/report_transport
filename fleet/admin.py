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
admin.site.register(MissionCostType)
admin.site.register(MissionCost)
admin.site.register(MasseSalariale)