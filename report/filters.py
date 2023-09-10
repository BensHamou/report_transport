from django import forms
from django.db.models import Q
from django_filters import FilterSet, CharFilter, ChoiceFilter, ModelChoiceFilter, DateFilter
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

    other = {'style': 'background-color: rgba(202, 207, 215, 0.5); border-color: transparent; box-shadow: 0 0 6px rgba(0, 0, 0, 0.2); color: #f2f2f2; height: 40px; border-radius: 5px;'}
    other_line = {'style': 'background-color: rgba(202, 207, 215, 0.5); border-color: transparent; box-shadow: 0 0 6px rgba(0, 0, 0, 0.2); color: #30343b; height: 40px; border-radius: 5px;'}

    search = CharFilter(method='filter_search', widget=forms.TextInput(attrs=getAttrs('search', 'Rechercher...')))    
    start_date = DateFilter(field_name='date_dep', lookup_expr='gte', widget=forms.widgets.DateInput(attrs= getAttrs('date', other=other), format='%d-%m-%Y'))
    end_date = DateFilter(field_name='date_dep', lookup_expr='lte', widget=forms.widgets.DateInput(attrs= getAttrs('date', other=other), format='%d-%m-%Y'))
    line = ModelChoiceFilter(queryset=Line.objects.all(), widget=forms.Select(attrs= getAttrs('select', other=other)), empty_label="All")

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
        fields = ['search', 'start_date', 'end_date', 'line']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(ReportFilter, self).__init__(*args, **kwargs)
        if user:
            self.filters['line'].queryset = user.lines.all()
