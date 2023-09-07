from django import forms
from django.db.models import Q
from django_filters import FilterSet, CharFilter
from .models import *
from report.forms import getAttrs

class ProductFilter(FilterSet):

    search = CharFilter(method='filter_search', widget=forms.TextInput(attrs=getAttrs('search', 'Rechercher..')))

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(designation__icontains=value) | (
            Q(line__designation__icontains=value) &
            Q(line__in=self.user.lines.all()) )
        ).distinct()

    class Meta:
        model = Product
        fields = ['search']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        self.user = user
        super(ProductFilter, self).__init__(*args, **kwargs)

class EmplacementFilter(FilterSet):

    search = CharFilter(method='filter_search', widget=forms.TextInput(attrs=getAttrs('search', 'Rechercher Emplacement..')))

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(designation__icontains=value)|
            Q(categ__icontains=value)
        ).distinct()

    class Meta:
        model = Emplacement
        fields = ['search']

class FournisseurFilter(FilterSet):

    search = CharFilter(method='filter_search', widget=forms.TextInput(attrs=getAttrs('search', 'Rechercher Fournisseur..') ))

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(designation__icontains=value)
        ).distinct()

    class Meta:
        model = Fournisseur
        fields = ['search']

class TonnageFilter(FilterSet):

    search = CharFilter(method='filter_search', widget=forms.TextInput(attrs=getAttrs('search', 'Rechercher Tonnage..')))

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(designation__icontains=value)
        ).distinct()

    class Meta:
        model = Tonnage
        fields = ['search']

class PriceFilter(FilterSet):

    search = CharFilter(method='filter_search', widget=forms.TextInput(attrs=getAttrs('search', 'Search...')))

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
        
class ReportFilter(FilterSet):

    search = CharFilter(method='filter_search', widget=forms.TextInput(attrs=getAttrs('search', 'Search...')))

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(prix__destination__designation__icontains=value) |
            Q(prix__depart__designation__icontains=value) |
            Q(prix__tonnage__designation__icontains=value) |
            Q(prix__fournisseur__designation__icontains=value) |
            Q(creator__fullname__icontains=value) |
            Q(chauffeur__icontains=value)|
            Q(n_bl__icontains=value)
        ).distinct()

    class Meta:
        model = Report
        fields = ['search']
