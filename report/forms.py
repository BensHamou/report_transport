from django.forms import ModelForm, inlineformset_factory
from django import forms
from .models import *
from account.models import *
from django.utils import timezone
from django.db.models import Q


def getAttrs(type, placeholder='', other={}):
    ATTRIBUTES = {
        'control': {'class': 'form-control', 'style': 'background-color: #ebecee;', 'placeholder': ''},
        'search': {'class': 'form-control form-input', 'style': 'background-color: #ebecee; border-color: transparent; color: #133356; height: 40px; text-indent: 33px; border-radius: 5px;', 'type': 'search', 'placeholder': '', 'id': 'search'},
        'select': {'class': 'form-select', 'style': 'background-color: #ebecee;'},
        'select2': {'class': 'form-select', 'style': 'background-color: #ebecee; width: 100%;'},
        'date': {'type': 'date', 'class': 'form-control dateinput','style': 'background-color: #ebecee;'},
        'textarea': {"rows": "3", 'style': 'width: 100%', 'class': 'form-control', 'placeholder': '', 'style': 'background-color: #ebecee;'}
    }

    
    if type in ATTRIBUTES:
        attributes = ATTRIBUTES[type]
        if 'placeholder' in attributes:
            attributes['placeholder'] = placeholder
        if other:
            attributes.update(other)
        return attributes
    else:
        return {}


class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = ['designation']

    designation = forms.CharField(widget=forms.TextInput(attrs=getAttrs('control','Designation')))

class EmplacementForm(ModelForm):
    class Meta:
        model = Emplacement
        fields = ['designation']
    
    designation = forms.CharField(widget=forms.TextInput(attrs=getAttrs('control','Designation')))

class TonnageForm(ModelForm):
    class Meta:
        model = Tonnage
        fields = ['designation']

    designation = forms.CharField(widget=forms.TextInput(attrs=getAttrs('control', 'Désignation')))

class FournisseurForm(ModelForm):
    class Meta:
        model = Fournisseur
        fields = ['designation']

    designation = forms.CharField(widget=forms.TextInput(attrs=getAttrs('control', 'Désignation')))

class PriceForm(ModelForm):
    
    destination = forms.ModelChoiceField(queryset=Emplacement.objects.all(), widget=forms.Select(attrs=getAttrs('select2')), empty_label="Déstination")
    depart = forms.ModelChoiceField(queryset=Site.objects.all(), widget=forms.Select(attrs=getAttrs('select2')), empty_label="Départ")
    tonnage = forms.ModelChoiceField(queryset=Tonnage.objects.all(), widget=forms.Select(attrs=getAttrs('select2')), empty_label="Tonnage")
    fournisseur = forms.ModelChoiceField(queryset=Fournisseur.objects.all(), widget=forms.Select(attrs=getAttrs('select2')), empty_label="Fournisseur")
    price = forms.FloatField(widget=forms.NumberInput(attrs= getAttrs('control','Prix')))
    class Meta:
        model = Price
        fields = ['destination', 'depart', 'fournisseur', 'tonnage', 'price']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(PriceForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['depart'].queryset = user.sites.all()
    
    
    def clean(self):
        cleaned_data = super().clean()
        destination = cleaned_data.get('destination')
        depart = cleaned_data.get('depart')
        fournisseur = cleaned_data.get('fournisseur')
        tonnage = cleaned_data.get('tonnage')

        if destination and depart and fournisseur and tonnage:
            if self.instance.pk:
                existing_price = Price.objects.filter(destination=destination, depart=depart, fournisseur=fournisseur, 
                tonnage=tonnage).exclude(Q(id=self.instance.pk)).exists()
            else:
                existing_price = Price.objects.filter(destination=destination, depart=depart, fournisseur=fournisseur, 
                tonnage=tonnage).exists()
            if existing_price:
                self.add_error('destination', 'Une liste de prix avec cette configuration existe déjà.')


class ReportForm(ModelForm):

    prix = forms.ModelChoiceField(queryset=Price.objects.all(), widget=forms.HiddenInput(), empty_label="Prix")
    date_dep = forms.DateField(initial=timezone.now().date(), widget=forms.widgets.DateInput(attrs= getAttrs('date'), format='%Y-%m-%d'))
    chauffeur = forms.CharField(widget=forms.TextInput(attrs= getAttrs('control','Chauffeur')))
    immatriculation = forms.CharField(widget=forms.TextInput(attrs= getAttrs('control','Immatriculation')))
    n_bl = forms.IntegerField(widget=forms.NumberInput(attrs= getAttrs('control','N° BL')))
    n_bl_2 = forms.IntegerField(widget=forms.NumberInput(attrs= getAttrs('control','N° BL 2 (Facultatif)')), required=False)
    observation = forms.CharField(widget=forms.Textarea(attrs=getAttrs('textarea','Observation')), required=False)
    site = forms.ModelChoiceField(queryset=Site.objects.all(), widget=forms.Select(attrs= getAttrs('select2')), empty_label="Site")
    destination = forms.ModelChoiceField(queryset=Emplacement.objects.all(), widget=forms.Select(attrs=getAttrs('select2')), empty_label="Déstination")
    tonnage = forms.ModelChoiceField(queryset=Tonnage.objects.all(), widget=forms.Select(attrs=getAttrs('select2')), empty_label="Tonnage")
    fournisseur = forms.ModelChoiceField(queryset=Fournisseur.objects.all(), widget=forms.Select(attrs=getAttrs('select2')), empty_label="Fournisseur")
    price = forms.FloatField(widget=forms.NumberInput(attrs= getAttrs('control','Prix')))

    class Meta:
        model = Report
        fields = ['prix', 'date_dep', 'chauffeur', 'immatriculation','n_bl', 'n_bl_2', 'site', 'observation', 'destination', 'tonnage', 'fournisseur', 'price']

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        sites = kwargs.pop('sites', None)
        super(ReportForm, self).__init__(*args, **kwargs)
        self.fields["prix"].widget.attrs['disabled'] = True
        self.fields["price"].widget.attrs['disabled'] = True
        self.fields['site'].initial = sites.first()
        if instance:
            self.fields['destination'].initial = instance.prix.destination
            self.fields['site'].initial = instance.prix.depart
            self.fields['tonnage'].initial = instance.prix.tonnage
            self.fields['fournisseur'].initial = instance.prix.fournisseur
            self.fields['price'].initial = instance.prix.price
        if len(sites) < 2:
            self.fields['site'].widget.attrs['disabled'] = True
        else:
            self.fields['site'].queryset = sites

    def clean(self):
        cleaned_data = super().clean()
        n_bl = cleaned_data.get('n_bl')
        n_bl_2 = cleaned_data.get('n_bl_2')
        site = cleaned_data.get('site')
        date_dep = cleaned_data.get('date_dep')

        if n_bl and n_bl != 0 and site:
            if self.instance.pk:
                existing_report = Report.objects.filter(Q(n_bl=n_bl, site=site) |  Q(n_bl_2=n_bl, site=site), date_dep__year=date_dep.year).exclude( Q(id=self.instance.pk) | Q(state='Annulé')).exists()
            else:
                existing_report = Report.objects.filter(Q(n_bl=n_bl, site=site) |  Q(n_bl_2=n_bl, site=site), date_dep__year=date_dep.year).exclude(state='Annulé').exists()
            if existing_report:
                self.add_error('n_bl', 'Un rapport avec ce numéro de BL existe déjà pour ce site.')

        if n_bl_2 and n_bl_2 != 0 and site:
            if self.instance.pk:
                existing_report_2 = Report.objects.filter(Q(n_bl=n_bl_2, site=site) |  Q(n_bl_2=n_bl_2, site=site), date_dep__year=date_dep.year).exclude( Q(id=self.instance.pk) | Q(state='Annulé')).exists()
            else:
                existing_report_2 = Report.objects.filter(Q(n_bl=n_bl_2, site=site) |  Q(n_bl_2=n_bl_2, site=site), date_dep__year=date_dep.year).exclude(state='Annulé').exists()
            if existing_report_2:
                self.add_error('n_bl_2', 'Un rapport avec ce numéro de BL existe déjà pour ce site.')
        return cleaned_data

class PTransportedForm(ModelForm):
    class Meta:
        model = PTransported
        fields = '__all__'

    product = forms.ModelChoiceField(queryset=Product.objects.all(), widget=forms.Select(attrs=getAttrs('select2')), empty_label="Produit")
    qte_transported = forms.FloatField(widget=forms.NumberInput(attrs= getAttrs('control','Qte Consomée')))
    observation = forms.CharField(widget=forms.Textarea(attrs=getAttrs('textarea','Observation')), required=False)

PTransportedsFormSet = inlineformset_factory(Report, PTransported, form=PTransportedForm, fields=['product', 'qte_transported', 'observation'], extra=0)
