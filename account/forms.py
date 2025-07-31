from django.forms import ModelForm
from django import forms
from .models import *
from django.contrib.auth.forms import AuthenticationForm
from report.forms import getAttrs

class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'is_admin', 'first_name', 'last_name', 'sites', 'role']

    attr = {'class': 'form-control', 'style': 'background-color: #cacfd7;', 'readonly':'readonly'}
    attr_select = {'class': 'form-select', 'style': 'background-color: #cacfd7;', 'readonly':'readonly'}

    username = forms.CharField(widget=forms.TextInput(attrs=attr))
    last_name = forms.CharField(widget=forms.TextInput(attrs=attr))
    first_name = forms.CharField(widget=forms.TextInput(attrs=attr))
    email = forms.EmailField(widget=forms.EmailInput(attrs=attr))
    sites = forms.SelectMultiple(attrs={'class': 'form-select'})
    role = forms.ChoiceField(choices=User.ROLE_CHOICES, widget=forms.Select(attrs=attr_select))
    is_admin = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'type': 'checkbox', 'data-onstyle':'primary', 
                                                                                    'data-toggle':'switchbutton',  'data-onlabel': "Adminnn", 'data-offlabel': "User"}))

class SiteForm(ModelForm):
    class Meta:
        model = Site
        fields = ['designation', 'address', 'prefix_site', 'btr_prefix_site', 'planning_prefix', 'include_cron', 'prefix_invocie_site']

    designation = forms.CharField(widget=forms.TextInput(attrs=getAttrs('control', 'Désignation')))
    address = forms.CharField(widget=forms.TextInput(attrs=getAttrs('control', 'Address')))
    prefix_site = forms.CharField(widget=forms.TextInput(attrs=getAttrs('control', 'Préfixe (BL)')))
    btr_prefix_site = forms.CharField(widget=forms.TextInput(attrs=getAttrs('control', 'Préfixe (BTR)')))
    planning_prefix = forms.CharField(widget=forms.TextInput(attrs=getAttrs('control', 'Préfixe (Planning)')))
    prefix_invocie_site = forms.CharField(widget=forms.TextInput(attrs=getAttrs('control', 'Préfixe (Facture)')))
    include_cron = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'type': 'checkbox', 'data-onstyle':'secondary', 'data-toggle':'switchbutton'}))

class CustomLoginForm(AuthenticationForm):
    
    username = forms.CharField( label="Email / AD 2000", widget=forms.TextInput(attrs={'autofocus': True, 'class': 'form-control', 'placeholder':'Email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder':'Mot de passe', 'style':'height: 45px; color: black;'}))
