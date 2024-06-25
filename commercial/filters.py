from django import forms
from django.db.models import Q
from django_filters import FilterSet, CharFilter, ChoiceFilter, ModelChoiceFilter, DateFilter
from .models import *
from account.models import Site
from report.forms import getAttrs

class LivraisonFilter(FilterSet):

    search = CharFilter(method='filter_search', widget=forms.TextInput(attrs=getAttrs('search', 'Rechercher Livraison..') ))

    def filter_search(self, queryset, name, value):
        return queryset.filter(Q(designation__icontains=value)).distinct()

    class Meta:
        model = Livraison
        fields = ['search']
        
class PlanningFilter(FilterSet):

    other = {'style': 'background-color: #ebecee; border-color: transparent; color: #133356; height: 40px; border-radius: 5px;'}


    search = CharFilter(method='filter_search', widget=forms.TextInput(attrs=getAttrs('search', 'Rechercher Rapport..')))
    start_date = DateFilter(field_name='date_planning', lookup_expr='gte', widget=forms.widgets.DateInput(attrs= getAttrs('date', other=other), format='%d-%m-%Y'))
    end_date = DateFilter(field_name='date_planning', lookup_expr='lte', widget=forms.widgets.DateInput(attrs= getAttrs('date', other=other), format='%d-%m-%Y'))
    site = ModelChoiceFilter(queryset=Site.objects.all(), widget=forms.Select(attrs= getAttrs('select', other=other)), empty_label="Site")
    state = ChoiceFilter(choices=Planning.STATE_PLANNING, widget=forms.Select(attrs=getAttrs('select', other=other)), empty_label="Etat")
    distru = CharFilter(method='distru_search', widget=forms.TextInput(attrs=getAttrs('search', 'Rechercher Distributeur..')))


    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(destination__designation__icontains=value) | Q(tonnage__designation__icontains=value) |
            Q(fournisseur__designation__icontains=value) | Q(creator__fullname__icontains=value) |
            Q(chauffeur__icontains=value) | Q(pk__icontains=value)).distinct()


    def distru_search(self, queryset, name, value):
        return queryset.filter(
            Q(distributeur__icontains=value)).distinct()

    class Meta:
        model = Planning
        fields = ['search', 'start_date', 'end_date', 'site', 'distru']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(PlanningFilter, self).__init__(*args, **kwargs)
        if user:
            self.filters['site'].queryset = user.sites.all()
