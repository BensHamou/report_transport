from django import forms
from django.db.models import Q
from django_filters import FilterSet, CharFilter, ChoiceFilter, ModelChoiceFilter, DateFilter
from .models import *
from account.models import Site
from report.forms import getAttrs
from datetime import timedelta, date
from django.db.models import F, Q
from django.db.models.functions import Greatest

class LivraisonFilter(FilterSet):

    search = CharFilter(method='filter_search', widget=forms.TextInput(attrs=getAttrs('search', 'Rechercher Livraison..') ))

    def filter_search(self, queryset, name, value):
        return queryset.filter(Q(designation__icontains=value)).distinct()

    class Meta:
        model = Livraison
        fields = ['search']
        
class BlockedFilter(FilterSet):

    distru = CharFilter(method='distru_search', widget=forms.TextInput(attrs=getAttrs('search', 'Rechercher Distributeur..')))

    def distru_search(self, queryset, name, value):
        return queryset.filter(Q(distributeur__icontains=value)).distinct()

    class Meta:
        model = Blocked
        fields = ['distru']

class PlanningFilter(FilterSet):

    other = {'style': 'background-color: #ebecee; border-color: transparent; color: #133356; height: 40px; border-radius: 5px;'}


    search = CharFilter(method='filter_search', widget=forms.TextInput(attrs=getAttrs('search', 'Rechercher Rapport..')))
    bl_number = CharFilter(field_name='n_bl', lookup_expr='exact', widget=forms.NumberInput(attrs=getAttrs('search', 'Rechercher BL...')))
    start_date = DateFilter(field_name='date_planning', lookup_expr='gte', widget=forms.widgets.DateInput(attrs= getAttrs('date', other=other), format='%d-%m-%Y'))
    end_date = DateFilter(field_name='date_planning', lookup_expr='lte', widget=forms.widgets.DateInput(attrs= getAttrs('date', other=other), format='%d-%m-%Y'))
    site = ModelChoiceFilter(queryset=Site.objects.all(), widget=forms.Select(attrs= getAttrs('select', other=other)), empty_label="Site")
    state = ChoiceFilter(choices=Planning.STATE_PLANNING, widget=forms.Select(attrs=getAttrs('select', other=other)), empty_label="Etat")
    distru = CharFilter(method='distru_search', widget=forms.TextInput(attrs=getAttrs('search', 'Rechercher Distributeur..')))
    SCAN_CHOICES = [
        ('', 'Tous'),
        ('scanned', 'Scanné'),
        ('overdue', 'En retard'),
    ]
    scan_state = ChoiceFilter(choices=SCAN_CHOICES, method='filter_scan_state', widget=forms.Select(attrs=getAttrs('select', other=other)), empty_label=None)

    def filter_scan_state(self, queryset, name, value):
        cutoff_date = date(2025, 10, 1)
        two_days_ago = date.today() - timedelta(days=2)

        queryset = queryset.annotate(final_date=Greatest(F('date_planning'), F('date_replanning')))

        if value == 'scanned':
            return queryset.filter(state='Livraison Confirmé', files__isnull=False).distinct()
        elif value == 'overdue':
            return queryset.filter(state='Livraison Confirmé', files__isnull=True, final_date__lte=two_days_ago, final_date__gte=cutoff_date).distinct()

        return queryset



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
        fields = ['search', 'start_date', 'end_date', 'site', 'distru', 'bl_number', 'state', 'scan_state']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(PlanningFilter, self).__init__(*args, **kwargs)
        if user:
            self.filters['site'].queryset = user.sites.all()

class ArchivedPlanningFilter(FilterSet):
    other = {'style': 'background-color: #ebecee; border-color: transparent; color: #133356; height: 40px; border-radius: 5px;'}

    bl_number = CharFilter(field_name='n_bl', lookup_expr='exact', widget=forms.NumberInput(attrs=getAttrs('search', 'Rechercher BL...')))
    start_date = DateFilter(field_name='date_honored', lookup_expr='gte', widget=forms.widgets.DateInput(attrs=getAttrs('date', other=other)))
    end_date = DateFilter(field_name='date_honored', lookup_expr='lte', widget=forms.widgets.DateInput(attrs=getAttrs('date', other=other)))
    site = ModelChoiceFilter(queryset=Site.objects.all(), widget=forms.Select(attrs=getAttrs('select2', other=other)), empty_label="Site")
    distributeur = CharFilter(field_name='distributeur', lookup_expr='icontains', widget=forms.TextInput(attrs=getAttrs('search', 'Rechercher Distributeur...')))
    driver = CharFilter(method='filter_driver', widget=forms.TextInput(attrs=getAttrs('search', 'Rechercher Chauffeur...')))
    fournisseur = ModelChoiceFilter(queryset=Fournisseur.objects.all(), widget=forms.Select(attrs=getAttrs('select2', other=other)), empty_label="Fournisseur")

    def filter_driver(self, queryset, name, value):
        return queryset.filter(Q(chauffeur__icontains=value) | Q(driver__last_name__icontains=value) | Q(driver__first_name__icontains=value)).distinct()

    class Meta:
        model = Planning
        fields = ['bl_number', 'start_date', 'end_date', 'site', 'distributeur', 'driver', 'fournisseur']


