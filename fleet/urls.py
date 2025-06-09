from django.urls import path
from .views import *

urlpatterns = [

    path('drivers/', listDriverView, name='drivers'),
    path("driver/delete-driver/<int:id>", deleteDriverView, name="delete_driver"),
    path("driver/edit-driver/<int:id>", editDriverView, name="edit_driver"),
    path("driver/create-driver/", createDriverView, name="create_driver"),
    
    path('vehicles/', listVehicleView, name='vehicles'),
    path("vehicle/delete-vehicle/<int:id>", deleteVehicleView, name="delete_vehicle"),
    path("vehicle/edit-vehicle/<int:id>", editVehicleView, name="edit_vehicle"),
    path("vehicle/create-vehicle/", createVehicleView, name="create_vehicle"),

    path('reparation-types/', listReparationTypeView, name='reparation_types'),
    path("reparation-type/delete/<int:id>", deleteReparationTypeView, name="delete_reparation_type"),
    path("reparation-type/edit/<int:id>", editReparationTypeView, name="edit_reparation_type"),
    path("reparation-type/create/", createReparationTypeView, name="create_reparation_type"),

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

    path('mission-cost-types/', listMissionCostTypeView, name='mission_cost_types'),
    path("mission-cost-type/delete/<int:id>", deleteMissionCostTypeView, name="delete_mission_cost_type"),
    path("mission-cost-type/edit/<int:id>", editMissionCostTypeView, name="edit_mission_cost_type"),
    path("mission-cost-type/create/", createMissionCostTypeView, name="create_mission_cost_type"),

    path('mission-costs/', listMissionCostView, name='mission_costs'),
    path("mission-cost/delete/<int:id>", deleteMissionCostView, name="delete_mission_cost"),
    path("mission-cost/edit/<int:id>", editMissionCostView, name="edit_mission_cost"),
    path("mission-cost/create/", createMissionCostView, name="create_mission_cost"),

    path('masse-salariales/', listMasseSalarialeView, name='masse_salariales'),
    path("masse-salariale/delete/<int:id>", deleteMasseSalarialeView, name="delete_masse_salariale"),
    path("masse-salariale/edit/<int:id>", editMasseSalarialeView, name="edit_masse_salariale"),
    path("masse-salariale/create/", createMasseSalarialeView, name="create_masse_salariale"),
    
]