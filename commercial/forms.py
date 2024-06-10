from django.forms import ModelForm, inlineformset_factory
from django import forms
from .models import *
from account.models import *
from django.utils import timezone
from django.db.models import Q
from report.forms import getAttrs

class PlanningCommForm(ModelForm):

    class Meta:
        model = Planning
        fields = ['site', 'date_planning', 'distributeur_id', 'distributeur','client_id', 'client', 'tonnage', 'destination', 'livraison', 'observation_comm', 'fournisseur', 'chauffeur', 'immatriculation', 'observation_logi']

    site = forms.ModelChoiceField(queryset=Site.objects.all(), widget=forms.Select(attrs= getAttrs('select2')), empty_label="Site")
    date_planning = forms.DateField(initial=timezone.now().date(), widget=forms.widgets.DateInput(attrs= getAttrs('date'), format='%Y-%m-%d'))

    distributeur_id = forms.IntegerField(widget=forms.HiddenInput(attrs=getAttrs('controlID','ID_dist_id')))
    distributeur = forms.CharField(widget=forms.TextInput(attrs=getAttrs('controlSearch','Distributeur')))

    client_id = forms.IntegerField(widget=forms.HiddenInput(attrs=getAttrs('controlID','ID_clinet_id')))
    client = forms.CharField(widget=forms.TextInput(attrs=getAttrs('controlSearch','Client')))

    tonnage = forms.ModelChoiceField(queryset=Tonnage.objects.all(), widget=forms.Select(attrs=getAttrs('select2')), empty_label="Tonnage")
    destination = forms.ModelChoiceField(queryset=Emplacement.objects.all().order_by('id'), widget=forms.Select(attrs=getAttrs('select2')), empty_label="Déstination")
    livraison = forms.CharField(widget=forms.TextInput(attrs=getAttrs('control','Livraison')), required=False)
    observation_comm = forms.CharField(widget=forms.Textarea(attrs=getAttrs('textarea','Observation')), required=False)

    fournisseur = forms.ModelChoiceField(queryset=Fournisseur.objects.all(), widget=forms.Select(attrs=getAttrs('select2')), empty_label="Fournisseur", required=False)
    chauffeur = forms.CharField(widget=forms.TextInput(attrs= getAttrs('control','Chauffeur')), required=False)
    immatriculation = forms.CharField(widget=forms.TextInput(attrs= getAttrs('control','Immatriculation')), required=False)
    observation_logi = forms.CharField(widget=forms.Textarea(attrs=getAttrs('textarea','Observation')), required=False)


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
        fields = ['fournisseur', 'chauffeur', 'immatriculation', 'observation_logi']

    fournisseur = forms.ModelChoiceField(queryset=Fournisseur.objects.all(), widget=forms.Select(attrs=getAttrs('select2')), empty_label="Fournisseur", required=False)
    chauffeur = forms.CharField(widget=forms.TextInput(attrs= getAttrs('control','Chauffeur')), required=False)
    immatriculation = forms.CharField(widget=forms.TextInput(attrs= getAttrs('control','Immatriculation')), required=False)
    observation_logi = forms.CharField(widget=forms.Textarea(attrs=getAttrs('textarea','Observation')), required=False)
