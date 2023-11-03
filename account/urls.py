from django.urls import path
from . import views
from .views import *

urlpatterns = [
    path('login_success/', views.login_success, name='login_success'),

    path("dashboard/", views.homeView, name="home"),
    path("refresh-users/", views.refreshUsersList, name="refresh_users"),
    path("users/edit-user/<int:id>", views.editUserView, name="edit_user"),
    path("users/delete-user/<int:id>", views.deleteUserView, name="delete_user"),
    path("users/", views.listUsersView, name="users"),
    path('users/details/<int:id>', views.userDetailsView, name='details'),

    path('sites/', views.listSiteView, name='sites'),
    path("site/delete-site/<int:id>", views.deleteSiteView, name="delete_site"),
    path("site/edit-site/<int:id>", views.editSiteView, name="edit_site"),
    path("site/create-site/", views.createSiteView, name="create_site"),
    
    path('login/', CustomLoginView.as_view(), name='login'),
    path('accounts/login/', CustomLoginView.as_view(), name='login'),
    path('logout/', views.logoutView, name='logout'),
]