from django import forms
from django.db.models import Q
from django_filters import FilterSet, CharFilter, ChoiceFilter, ModelChoiceFilter, DateFilter
from .models import *
from report.models import Fournisseur
from report.forms import getAttrs

class DriverFilter(FilterSet):
    other = {'style': 'background-color: #ebecee; border-color: transparent; color: #133356; height: 40px; border-radius: 5px;'}

    search = CharFilter(method='filter_search', widget=forms.TextInput(attrs=getAttrs('search', 'Rechercher Chauffeur..')))
    fournisseur = ModelChoiceFilter(queryset=Fournisseur.objects.all(), widget=forms.Select(attrs= getAttrs('select', other=other)), empty_label="Fournisseur")

    def filter_search(self, queryset, name, value):
        return queryset.filter(Q(first_name__icontains=value) |Q(last_name__icontains=value)).distinct()

    class Meta:
        model = Driver
        fields = ['search']


class VehicleFilter(FilterSet):
    other = {'style': 'background-color: #ebecee; border-color: transparent; color: #133356; height: 40px; border-radius: 5px;'}

    search = CharFilter(method='filter_search', widget=forms.TextInput(attrs=getAttrs('search', 'Rechercher vehicle..')))
    fournisseur = ModelChoiceFilter(queryset=Fournisseur.objects.all(), widget=forms.Select(attrs= getAttrs('select', other=other)), empty_label="Fournisseur")

    def filter_search(self, queryset, name, value):
        return queryset.filter(Q(immatriculation__icontains=value) |Q(model__icontains=value) |Q(mark__icontains=value)).distinct()

    class Meta:
        model = Vehicle
        fields = ['search']


