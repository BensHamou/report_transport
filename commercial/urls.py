from django.urls import path
from .views import *
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    
    path('livraisons/', listLivraisonList, name='livraisons'),
    path("livraisons/delete-livraison/<int:id>", deleteLivraisonView, name="delete_livraison"),
    path("livraisons/edit-livraison/<int:id>", editLivraisonView, name="edit_livraison"),
    path("livraisons/create-livraison/", createLivraisonView, name="create_livraison"),
    
    path('black-list/', blockedList, name='blockeds'),
    path("black-list/remove/<int:id>", removeBlockedView, name="remove_blocked"),
    path("black-list/add/", addBlockedView, name="add_blocked"),
    path("black-list/send/", sendBlockList, name="send_blocked"),

    path('plannings/', PlanningList.as_view(), name='plannings'),
    path("planning/<int:pk>", PlanningDetail.as_view(), name="view_planning"),
    path("planning/<int:id>/delete", deletePlanningView, name="delete_planning"),
    path("planning/<int:id>/complete", completePlanning, name="complete_planning"),
    path("planning/<int:id>/finish", finishPlanning, name="finish_planning"),
    path("planning/<int:pk>/edit", PlanningUpdate.as_view(), name="edit_planning"),
    path("planning/create/", PlanningCreate.as_view(), name="create_planning"),
    path('planning/delete-product/<int:pk>/', delete_product, name='planning_delete_product'),

    path('planning/<int:pk>/confirm/', confirmPlanning, name='confirm_planning'),
    path('planning/<int:pk>/cancel/', cancelPlanning, name='cancel_planning'),
    path('planning/<int:pk>/validate/', validatePlanning, name='validate_planning'),
    path('planning/<int:pk>/miss/', missPlanning, name='miss_planning'),
    path('planning/<int:pk>/mark/', markPlanning, name='mark_planning'),
    path('planning/<int:pk>/unmark/', unmarkPlanning, name='unmark_planning'),
    path('planning/<int:pk>/reschedule/', reschedulePlanning, name='reschedule_planning'),
    path('planning/<int:pk>/deliver/', deliverPlanning, name='validate_delivery'),
    path('planning/mail/', sendSelectedPlannings, name='send_selected_plannings'),
    path('planning/missing/', sendMissedPlannings, name='send_missed_plannings'),
    path('planning/supplier/', sendPlanningSupplier, name='send_selected_supplier'),
    path('planning/finished/', sendValidationMail, name='send_confirmed'),
    path('planning/change-dates/', changePlanningDates, name='change_planning_dates'),
    
    path('live_search/', live_search, name='live_search'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)