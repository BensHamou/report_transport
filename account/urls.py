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

    path('lines/', views.listLineView, name='lines'),
    path("line/delete-line/<int:id>", views.deleteLineView, name="delete_line"),
    path("line/edit-line/<int:id>", views.editLineView, name="edit_line"),
    path("line/create-line/", views.createLineView, name="create_line"),
    
    path('login/', CustomLoginView.as_view(), name='login'),
    path('accounts/login/', CustomLoginView.as_view(), name='login'),
    path('logout/', views.logoutView, name='logout'),
]