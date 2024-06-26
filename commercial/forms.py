from django.forms import ModelForm, inlineformset_factory
from django import forms
from .models import *
from django.db.models import Q
from account.models import *
from django.utils import timezone
from report.models import Price
from report.forms import getAttrs
from datetime import timedelta


class LivraisonForm(ModelForm):
    class Meta:
        model = Livraison
        fields = ['designation']

    designation = forms.CharField(widget=forms.TextInput(attrs=getAttrs('control','Designation')))

class PlanningCommForm(ModelForm):

    class Meta:
        model = Planning
        fields = ['site', 'date_planning', 'distributeur_id', 'distributeur','client_id', 'client', 'destination', 
                  'livraison', 'observation_comm', 'fournisseur', 'chauffeur', 'immatriculation', 'date_honored', 'observation_logi']

    site = forms.ModelChoiceField(queryset=Site.objects.all(), widget=forms.Select(attrs= getAttrs('select2')), empty_label="Site")
    date_planning = forms.DateField(initial=timezone.now().date() + timedelta(days=1), widget=forms.widgets.DateInput(attrs= getAttrs('date'), format='%Y-%m-%d'))

    distributeur_id = forms.IntegerField(widget=forms.HiddenInput(attrs=getAttrs('controlID','ID_dist_id')))
    distributeur = forms.CharField(widget=forms.TextInput(attrs=getAttrs('controlSearch','Distributeur')))

    client_id = forms.IntegerField(widget=forms.HiddenInput(attrs=getAttrs('controlID','ID_clinet_id')))
    client = forms.CharField(widget=forms.TextInput(attrs=getAttrs('controlSearch','Client')))

    destination = forms.ModelChoiceField(queryset=Emplacement.objects.all().order_by('id'), widget=forms.Select(attrs=getAttrs('select2')), empty_label="Déstination")
    livraison = forms.ModelChoiceField(queryset=Livraison.objects.all().order_by('id'), widget=forms.Select(attrs=getAttrs('select2')), empty_label="Livraison")
    observation_comm = forms.CharField(widget=forms.Textarea(attrs=getAttrs('textarea','Observation')), required=False)

    fournisseur = forms.ModelChoiceField(queryset=Fournisseur.objects.all(), widget=forms.Select(attrs=getAttrs('select2')), empty_label="Fournisseur", required=False)
    chauffeur = forms.CharField(widget=forms.TextInput(attrs= getAttrs('control','Chauffeur')), required=False)
    immatriculation = forms.CharField(widget=forms.TextInput(attrs= getAttrs('control','Immatriculation')), required=False)
    date_honored = forms.DateField(initial=timezone.now().date(), widget=forms.widgets.DateInput(attrs= getAttrs('date'), format='%Y-%m-%d'), required=False)
    tonnage = forms.ModelChoiceField(queryset=Tonnage.objects.all(), widget=forms.Select(attrs=getAttrs('select2')), empty_label="Tonnage", required=False)
    observation_logi = forms.CharField(widget=forms.Textarea(attrs=getAttrs('textarea','Observation')), required=False)

    def clean(self):
        cleaned_data = super().clean()
        site = cleaned_data.get('site')
        tonnage = cleaned_data.get('tonnage')
        destination = cleaned_data.get('destination')
        fournisseur = cleaned_data.get('fournisseur')
        date_planning = cleaned_data.get('date_planning')
        if fournisseur:
            if tonnage:
                if not Price.objects.filter(depart=site, destination=destination, tonnage=tonnage, 
                                            fournisseur=fournisseur, date_from__lte=date_planning).filter(Q(date_to__gte=date_planning) | Q(date_to__isnull=True)).exists():
                    self.add_error('fournisseur', 'Aucun prix trouvé pour cette configuration.')
                    self.add_error('site', 'Aucun prix trouvé pour cette configuration.')
                    self.add_error('tonnage', 'Aucun prix trouvé pour cette configuration.')
                    self.add_error('destination', 'Aucun prix trouvé pour cette configuration.')
            else:
                if not Price.objects.filter(depart=site, destination=destination, fournisseur=fournisseur, date_from__lte=date_planning).filter(Q(date_to__gte=date_planning) | Q(date_to__isnull=True)).exists():
                    self.add_error('fournisseur', 'Aucun prix trouvé pour cette configuration.')
                    self.add_error('site', 'Aucun prix trouvé pour cette configuration.')
                    self.add_error('destination', 'Aucun prix trouvé pour cette configuration.')
        else:
            if tonnage:
                if not Price.objects.filter(depart=site, destination=destination, tonnage=tonnage, date_from__lte=date_planning).filter(Q(date_to__gte=date_planning) | Q(date_to__isnull=True)).exists():
                    self.add_error('site', 'Aucun prix trouvé pour cette configuration.')
                    self.add_error('tonnage', 'Aucun prix trouvé pour cette configuration.')
                    self.add_error('destination', 'Aucun prix trouvé pour cette configuration.')
            else:
                if not Price.objects.filter(depart=site, destination=destination, date_from__lte=date_planning).filter(Q(date_to__gte=date_planning) | Q(date_to__isnull=True)).exists():
                    self.add_error('destination', 'Aucun prix trouvé pour cette configuration.')
                    self.add_error('site', 'Aucun prix trouvé pour cette configuration.')
        
        return cleaned_data


    def __init__(self, *args, **kwargs):
        sites = kwargs.pop('sites', None)
        super(PlanningCommForm, self).__init__(*args, **kwargs)
        self.fields['site'].initial = sites.first()
        if len(sites) < 2:
            self.fields['site'].widget.attrs['disabled'] = True
        else:
            self.fields['site'].queryset = sites

class PPlannedForm(ModelForm):
    class Meta:
        model = PPlanned
        fields = '__all__'

    product = forms.ModelChoiceField(queryset=Product.objects.all(), widget=forms.Select(attrs=getAttrs('select2')), empty_label="Produit")
    palette = forms.FloatField(widget=forms.NumberInput(attrs= getAttrs('control','Palette')))

PPlannedsFormSet = inlineformset_factory(Planning, PPlanned, form=PPlannedForm, fields=['product', 'palette'], extra=0)

class PlanningLogiForm(ModelForm):

    class Meta:
        model = Planning
        fields = ['fournisseur', 'date_honored', 'tonnage', 'observation_logi']

    fournisseur = forms.ModelChoiceField(queryset=Fournisseur.objects.all(), widget=forms.Select(attrs=getAttrs('select2')), empty_label="Fournisseur")
    date_honored = forms.DateField(initial=timezone.now().date(), widget=forms.widgets.DateInput(attrs= getAttrs('date'), format='%Y-%m-%d'))
    tonnage = forms.ModelChoiceField(queryset=Tonnage.objects.all(), widget=forms.Select(attrs=getAttrs('select2')), empty_label="Tonnage")
    def clean(self):
        cleaned_data = super().clean()
        fournisseur = cleaned_data.get('fournisseur')
        tonnage = cleaned_data.get('tonnage')
        date_planning = self.instance.date_planning
        if fournisseur and tonnage:
            if not Price.objects.filter(depart=self.instance.site, destination=self.instance.destination, tonnage=tonnage, 
                                        fournisseur=fournisseur, date_from__lte=date_planning).filter(Q(date_to__gte=date_planning) | Q(date_to__isnull=True)).exists():
                self.add_error('fournisseur', 'Aucun prix trouvé pour cette configuration.')
                self.add_error('tonnage', 'Aucun prix trouvé pour cette configuration.')
        return cleaned_data
    
class PlanningConfirmForm(ModelForm):

    class Meta:
        model = Planning
        fields = ['chauffeur', 'immatriculation', 'observation_logi']

    chauffeur = forms.CharField(widget=forms.TextInput(attrs= getAttrs('control','Chauffeur')))
    immatriculation = forms.CharField(widget=forms.TextInput(attrs= getAttrs('control','Immatriculation')), required=False)
    observation_logi = forms.CharField(widget=forms.Textarea(attrs=getAttrs('textarea','Observation')), required=False)