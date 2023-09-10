from django.urls import path
from . import views
from .views import *

urlpatterns = [
    path('emplacements/', views.listEmplacementView, name='emplacements'),
    path("emplacements/delete-emplacement/<int:id>", views.deleteEmplacementView, name="delete_emplacement"),
    path("emplacements/edit-emplacement/<int:id>", views.editEmplacementView, name="edit_emplacement"),
    path("emplacements/create-emplacement/", views.createEmplacementView, name="create_emplacement"),
    
    path('fournisseurs/', views.listFournisseurView, name='fournisseurs'),
    path("fournisseurs/delete-fournisseur/<int:id>", views.deleteFournisseurView, name="delete_fournisseur"),
    path("fournisseurs/edit-fournisseur/<int:id>", views.editFournisseurView, name="edit_fournisseur"),
    path("fournisseurs/create-fournisseur/", views.createFournisseurView, name="create_fournisseur"),

    path('tonnages/', views.listTonnageView, name='tonnages'),
    path("tonnages/delete-tonnage/<int:id>", views.deleteTonnageView, name="delete_tonnage"),
    path("tonnages/edit-tonnage/<int:id>", views.editTonnageView, name="edit_tonnage"),
    path("tonnages/create-tonnage/", views.createTonnageView, name="create_tonnage"),
    
    path('products/', views.listProductList, name='products'),
    path("products/delete-product/<int:id>", views.deleteProductView, name="delete_product"),
    path("products/edit-product/<int:id>", views.editProductView, name="edit_product"),
    path("products/create-product/", views.createProductView, name="create_product"),

    path('prix/', views.listPriceView, name='prices'),
    path("prix/delete-prix/<int:id>", views.deletePriceView, name="delete_price"),
    path("prix/edit-prix/<int:id>", views.editPriceView, name="edit_price"),
    path("prix/create-prix/", views.createPriceView, name="create_price"),

    path('reports/', ReportList.as_view(), name='reports'),
    path('', ReportList.as_view(), name='reports'),
    path("report/<int:pk>", ReportDetail.as_view(), name="view_report"),
    path("report/<int:id>/delete", views.deleteReportView, name="delete_report"),
    path("report/<int:pk>/edit", ReportUpdate.as_view(), name="edit_report"),
    path("report/create/", ReportCreate.as_view(), name="create_report"),
    path('delete-product/<int:pk>/', delete_product, name='delete_product'),

    path('report/<int:pk>/confirm/', views.confirmReport, name='confirm_report'),
    path('report/<int:pk>/cancel/', views.cancelReport, name='cancel_report'),
    path('report/get-price/', views.getPrice, name='get_price'),

]