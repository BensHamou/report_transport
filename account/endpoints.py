from django.urls import path
from .api import *

urlpatterns = [
    path('api/planning/lookup/', lookup_planning_by_code, name='lookup_planning'),
    path('api/planning/submit/', submit_planning_data, name='submit_planning_data'),
]
