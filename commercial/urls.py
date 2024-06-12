from django.urls import path
from .views import *

urlpatterns = [

    path('plannings/', PlanningList.as_view(), name='plannings'),
    path("planning/<int:pk>", PlanningDetail.as_view(), name="view_planning"),
    path("planning/<int:id>/delete", deletePlanningView, name="delete_planning"),
    path("planning/<int:id>/complete", completePlanning, name="complete_planning"),
    path("planning/<int:pk>/edit", PlanningUpdate.as_view(), name="edit_planning"),
    path("planning/create/", PlanningCreate.as_view(), name="create_planning"),
    path('delete-product/<int:pk>/', delete_product, name='planning_delete_product'),

    path('planning/<int:pk>/confirm/', confirmPlanning, name='confirm_planning'),
    path('planning/<int:pk>/cancel/', cancelPlanning, name='cancel_planning'),
    path('planning/<int:pk>/validate/', validatePlanning, name='validate_planning'),
    path('planning/<int:pk>/miss/', missPlanning, name='miss_planning'),
    path('planning/<int:pk>/draft/', makeDraftPlanning, name='make_draft_planning'),
    path('planning/<int:pk>/deliver/', deliverPlanning, name='validate_delivery'),
    
    path('live_search/', live_search, name='live_search'),
]