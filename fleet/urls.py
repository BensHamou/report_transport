from django.urls import path
from .views import *

urlpatterns = [

    path('drivers/', listDriverView, name='drivers'),
    path("drivers/delete-driver/<int:id>", deleteDriverView, name="delete_driver"),
    path("drivers/edit-driver/<int:id>", editDriverView, name="edit_driver"),
    path("drivers/create-driver/", createDriverView, name="create_driver"),
    
    path('vehicles/', listVehicleView, name='vehicles'),
    path("vehicles/delete-vehicle/<int:id>", deleteVehicleView, name="delete_vehicle"),
    path("vehicles/edit-vehicle/<int:id>", editVehicleView, name="edit_vehicle"),
    path("vehicles/create-vehicle/", createVehicleView, name="create_vehicle"),
    
]