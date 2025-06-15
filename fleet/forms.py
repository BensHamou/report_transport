from django.forms import ModelForm, inlineformset_factory
from report.forms import getAttrs
from django import forms
from .models import *
from report.models import Fournisseur, Emplacement
from django.core.validators import MinValueValidator
from django.utils import timezone
from account.models import Site

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

    designation = forms.CharField(widget=forms.TextInput(attrs=getAttrs('control','Code camion')), required=False)
    model = forms.CharField(widget=forms.TextInput(attrs=getAttrs('control','Modèle')), required=False)
    mark = forms.CharField(widget=forms.TextInput(attrs=getAttrs('control','Marque')), required=False)
    immatriculation = forms.CharField(widget=forms.TextInput(attrs=getAttrs('control','Immatriculation')))
    year = forms.IntegerField(widget=forms.NumberInput(attrs=getAttrs('control','Année')), validators=[MinValueValidator(1900)], required=False)
    fournisseur = forms.ModelChoiceField(queryset=Fournisseur.objects.filter(is_tracked=True), widget=forms.Select(attrs=getAttrs('select')), required=False)
    objectif = forms.FloatField(widget=forms.NumberInput(attrs=getAttrs('control','Objectif')), validators=[MinValueValidator(0)])
    consommation_with = forms.FloatField(widget=forms.NumberInput(attrs=getAttrs('control','Consommation avec marchandise')), validators=[MinValueValidator(0)])
    consommation_without = forms.FloatField(widget=forms.NumberInput(attrs=getAttrs('control','Consommation sans marchandise')), validators=[MinValueValidator(0)])
    dotation = forms.FloatField(widget=forms.NumberInput(attrs=getAttrs('control','Dotation')), validators=[MinValueValidator(0)])


class ReparationTypeForm(ModelForm):
    class Meta:
        model = ReparationType
        fields = '__all__'

    designation = forms.CharField(widget=forms.TextInput(attrs=getAttrs('control', 'Désignation')))

class ReparationForm(ModelForm):
    class Meta:
        model = Reparation
        fields = '__all__'

    vehicle = forms.ModelChoiceField(queryset=Vehicle.objects.all(), widget=forms.Select(attrs=getAttrs('select2')))
    reparation_type = forms.ModelChoiceField(queryset=ReparationType.objects.all(), widget=forms.Select(attrs=getAttrs('select2')))
    reparation_date = forms.DateField(initial=timezone.now().date(), widget=forms.widgets.DateInput(attrs= getAttrs('date'), format='%Y-%m-%d'))
    amount = forms.FloatField(widget=forms.NumberInput(attrs=getAttrs('control','Montant')), validators=[MinValueValidator(0)])
    observation = forms.CharField(widget=forms.Textarea(attrs=getAttrs('textarea','Observation')), required=False)


class FuelRefillForm(ModelForm):
    class Meta:
        model = FuelRefill
        fields = '__all__'

    vehicle = forms.ModelChoiceField(queryset=Vehicle.objects.all(), widget=forms.Select(attrs=getAttrs('select2')))
    driver = forms.ModelChoiceField(queryset=Driver.objects.all(), widget=forms.Select(attrs=getAttrs('select2')), required=False)
    refill_date = forms.DateField(initial=timezone.now().date(), widget=forms.widgets.DateInput(attrs= getAttrs('date'), format='%Y-%m-%d'))
    km = forms.FloatField(widget=forms.NumberInput(attrs=getAttrs('control','Kilométrage')), validators=[MinValueValidator(0)])
    amount = forms.FloatField(widget=forms.NumberInput(attrs=getAttrs('control','Montant de la recharge')), validators=[MinValueValidator(0)])
    observation = forms.CharField(widget=forms.Textarea(attrs=getAttrs('textarea','Observation')), required=False)


class AssuranceForm(ModelForm):
    class Meta:
        model = Assurance
        fields = '__all__'
    
    type = forms.ChoiceField(choices=Assurance.INSUTANCE_CHOICES, widget=forms.Select(attrs=getAttrs('select')))
    vehicle = forms.ModelChoiceField(queryset=Vehicle.objects.all(), widget=forms.Select(attrs=getAttrs('select2')), empty_label="Camion")
    assurance_date = forms.DateField(initial=timezone.now().date(), widget=forms.widgets.DateInput(attrs= getAttrs('date'), format='%Y-%m-%d'))
    assurance_expiry_date = forms.DateField(widget=forms.widgets.DateInput(attrs= getAttrs('date'), format='%Y-%m-%d'))
    observation = forms.CharField(widget=forms.Textarea(attrs=getAttrs('textarea','Observation')), required=False)


class MissionCostTypeForm(ModelForm):
    class Meta:
        model = MissionCostType
        fields = '__all__'

    designation = forms.CharField(widget=forms.TextInput(attrs=getAttrs('control', 'Désignation')))


class MissionCostForm(ModelForm):
    class Meta:
        model = MissionCost
        fields = '__all__'

    mission_date = forms.DateField(initial=timezone.now().date(), widget=forms.widgets.DateInput(attrs= getAttrs('date'), format='%Y-%m-%d'))
    vehicle = forms.ModelChoiceField(queryset=Vehicle.objects.all(), widget=forms.Select(attrs=getAttrs('select2')))
    driver = forms.ModelChoiceField(queryset=Driver.objects.all(), widget=forms.Select(attrs=getAttrs('select2')), required=False)
    from_emplacement = forms.ModelChoiceField(queryset=Site.objects.all(), widget=forms.Select(attrs=getAttrs('select2')))
    to_emplacement = forms.ModelChoiceField(queryset=Emplacement.objects.all(), widget=forms.Select(attrs=getAttrs('select2')))
    observation = forms.CharField(widget=forms.Textarea(attrs=getAttrs('textarea','Observation')), required=False)

class MissionCostFeeForm(ModelForm):
    class Meta:
        model = MissionCostFee
        fields = '__all__'

    fee_type = forms.ModelChoiceField(queryset=MissionCostType.objects.all(), widget=forms.Select(attrs=getAttrs('select2')), empty_label="Type de frais")
    cost = forms.FloatField(widget=forms.NumberInput(attrs= getAttrs('control','Cout')), validators=[MinValueValidator(0)])
    observation = forms.CharField(widget=forms.Textarea(attrs=getAttrs('textarea','Observation')), required=False)

MissionCostFeesFormSet = inlineformset_factory(MissionCost, MissionCostFee, form=MissionCostFeeForm, fields=['fee_type', 'cost', 'observation'], extra=0)

class MasseSalarialeForm(ModelForm):
    class Meta:
        model = MasseSalariale
        fields = '__all__'

    vehicle = forms.ModelChoiceField(queryset=Vehicle.objects.all(), widget=forms.Select(attrs=getAttrs('select2')))
    month = forms.DateField(initial=timezone.now().date(), widget=forms.widgets.DateInput(attrs=getAttrs('month'), format='%Y-%m'), input_formats=['%Y-%m'])
    amount = forms.FloatField(widget=forms.NumberInput(attrs=getAttrs('control','Montant de la mission')), validators=[MinValueValidator(0)])





