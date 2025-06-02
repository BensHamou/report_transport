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

    path('reparation-types/', listReparationTypeView, name='reparation_types'),
    path("reparation-types/delete/<int:id>", deleteReparationTypeView, name="delete_reparation_type"),
    path("reparation-types/edit/<int:id>", editReparationTypeView, name="edit_reparation_type"),
    path("reparation-types/create/", createReparationTypeView, name="create_reparation_type"),

    path('reparations/', listReparationView, name='reparations'),
    path("reparation/delete/<int:id>", deleteReparationView, name="delete_reparation"),
    path("reparation/edit/<int:id>", editReparationView, name="edit_reparation"),
    path("reparation/create/", createReparationView, name="create_reparation"),

    path('fuel-refills/', listFuelRefillView, name='fuel_refills'),
    path("fuel-refill/delete/<int:id>", deleteFuelRefillView, name="delete_fuel_refill"),
    path("fuel-refill/edit/<int:id>", editFuelRefillView, name="edit_fuel_refill"),
    path("fuel-refill/create/", createFuelRefillView, name="create_fuel_refill"),

    path('assurances/', listAssuranceView, name='assurances'),
    path("assurance/delete/<int:id>", deleteAssuranceView, name="delete_assurance"),
    path("assurance/edit/<int:id>", editAssuranceView, name="edit_assurance"),
    path("assurance/create/", createAssuranceView, name="create_assurance"),
    
]