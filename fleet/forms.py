from django.forms import ModelForm
from report.forms import getAttrs
from django import forms
from .models import *
from report.models import Fournisseur
from django.core.validators import MinValueValidator

class DriverForm(ModelForm):
    class Meta:
        model = Driver
        fields = '__all__'

    last_name = forms.CharField(widget=forms.TextInput(attrs=getAttrs('control','Nom')))
    first_name = forms.CharField(widget=forms.TextInput(attrs=getAttrs('control','Prénom')))
    fournisseur = forms.ModelChoiceField(queryset=Fournisseur.objects.filter(is_tracked=True), widget=forms.Select(attrs=getAttrs('select')))
    phone = forms.CharField(widget=forms.TextInput(attrs=getAttrs('control','Téléphone')), required=False)
    address = forms.CharField(widget=forms.TextInput(attrs=getAttrs('control','Adresse')), required=False)
    driving_license = forms.CharField(widget=forms.TextInput(attrs=getAttrs('control','Permis de conduire')), required=False)


class VehicleForm(ModelForm):
    class Meta:
        model = Vehicle
        fields = '__all__'

    model = forms.CharField(widget=forms.TextInput(attrs=getAttrs('control','Modèle')), required=False)
    mark = forms.CharField(widget=forms.TextInput(attrs=getAttrs('control','Marque')), required=False)
    immatriculation = forms.CharField(widget=forms.TextInput(attrs=getAttrs('control','Immatriculation')))
    year = forms.IntegerField(widget=forms.NumberInput(attrs=getAttrs('control','Année')), validators=[MinValueValidator(1900)], required=False)
    fournisseur = forms.ModelChoiceField(queryset=Fournisseur.objects.filter(is_tracked=True), widget=forms.Select(attrs=getAttrs('select')), required=False)
    objectif = forms.FloatField(widget=forms.NumberInput(attrs=getAttrs('control','Objectif')), validators=[MinValueValidator(0)])
    consommation_with = forms.FloatField(widget=forms.NumberInput(attrs=getAttrs('control','Consommation avec marchandise')), validators=[MinValueValidator(0)])
    consommation_without = forms.FloatField(widget=forms.NumberInput(attrs=getAttrs('control','Consommation sans marchandise')), validators=[MinValueValidator(0)])
