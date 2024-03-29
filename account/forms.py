from django.forms import ModelForm
from django import forms
from .models import *
from django.contrib.auth.forms import AuthenticationForm
from report.forms import getAttrs

class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['username', 'fullname', 'email', 'is_admin', 'first_name', 'last_name', 'sites']

    attr = {'class': 'form-control', 'style': 'background-color: #cacfd7;', 'readonly':'readonly'}

    username = forms.CharField(widget=forms.TextInput(attrs=attr))
    last_name = forms.CharField(widget=forms.TextInput(attrs=attr))
    first_name = forms.CharField(widget=forms.TextInput(attrs=attr))
    fullname = forms.CharField(widget=forms.TextInput(attrs=attr))
    email = forms.EmailField(widget=forms.EmailInput(attrs=attr))
    sites = forms.SelectMultiple(attrs={'class': 'form-select'})
    is_admin = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'type': 'checkbox', 'data-onstyle':'secondary', 'data-toggle':'switchbutton'}))

class SiteForm(ModelForm):
    class Meta:
        model = Site
        fields = ['designation', 'address', 'prefix_site', 'btr_prefix_site', 'include_cron']

    designation = forms.CharField(widget=forms.TextInput(attrs=getAttrs('control', 'Désignation')))
    address = forms.CharField(widget=forms.TextInput(attrs=getAttrs('control', 'Address')))
    prefix_site = forms.CharField(widget=forms.TextInput(attrs=getAttrs('control', 'Préfixe (BL)')))
    btr_prefix_site = forms.CharField(widget=forms.TextInput(attrs=getAttrs('control', 'Préfixe (BTR)')))
    include_cron = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'type': 'checkbox', 'data-onstyle':'secondary', 'data-toggle':'switchbutton'}))

class CustomLoginForm(AuthenticationForm):
    
    username = forms.CharField( label="Email / AD 2000", widget=forms.TextInput(attrs={'autofocus': True, 'class': 'form-control', 'placeholder':'Email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder':'Mot de passe', 'style':'height: 45px; color: black;'}))
