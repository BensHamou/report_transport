import django_filters
from django import forms
from django.db.models import Q

from .models import *
from report.forms import getAttrs

class EmplacementFilter(django_filters.FilterSet):

    search = django_filters.CharFilter(method='filter_search', widget=forms.TextInput(attrs=getAttrs('search', 'Rechercher Emplacement..')))

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(designation__icontains=value)|
            Q(categ__icontains=value)
        ).distinct()

    class Meta:
        model = Emplacement
        fields = ['search']

class FournisseurFilter(django_filters.FilterSet):

    search = django_filters.CharFilter(method='filter_search', widget=forms.TextInput(attrs=getAttrs('search', 'Rechercher Fournisseur..') ))

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(designation__icontains=value)
        ).distinct()

    class Meta:
        model = Fournisseur
        fields = ['search']


class TonnageFilter(django_filters.FilterSet):

    search = django_filters.CharFilter(method='filter_search', widget=forms.TextInput(attrs=getAttrs('search', 'Rechercher Tonnage..')))

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(designation__icontains=value)
        ).distinct()

    class Meta:
        model = Tonnage
        fields = ['search']

class PriceFilter(django_filters.FilterSet):

    search = django_filters.CharFilter(method='filter_search', widget=forms.TextInput(attrs=getAttrs('search', 'Search...')))

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(destination__designation__icontains=value) |
            Q(depart__designation__icontains=value) |
            Q(tonnage__designation__icontains=value) |
            Q(fournisseur__designation__icontains=value) |
            Q(price__icontains=value)
        ).distinct()

    class Meta:
        model = Price
        fields = ['search']
