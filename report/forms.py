from django.forms import ModelForm, inlineformset_factory
from django import forms
from .models import *
from django.utils import timezone

def getAttrs(type, placeholder='', other={}):
    ATTRIBUTES = {
        'control': {'class': 'form-control', 'style': 'background-color: #cacfd7;', 'placeholder': ''},
        'search': {'class': 'form-control form-input', 'style': 'background-color: rgba(202, 207, 215, 0.5); border-color: transparent; box-shadow: 0 0 6px rgba(0, 0, 0, 0.2); color: #f2f2f2; height: 40px; text-indent: 33px; border-radius: 5px;', 'type': 'search', 'placeholder': '', 'id': 'search'},
        'select': {'class': 'form-select', 'style': 'background-color: #cacfd7;'},
        'date': {'type': 'date', 'class': 'form-control dateinput','style': 'background-color: #cacfd7;'},
        'textarea': {"rows": "3", 'style': 'width: 100%', 'class': 'form-control', 'placeholder': '', 'style': 'background-color: #cacfd7;'}
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
        fields = ['designation', 'line']

    designation = forms.CharField(widget=forms.TextInput(attrs=getAttrs('control','Designation')))
    line = forms.ModelChoiceField(queryset=Line.objects.all(), widget=forms.Select(attrs=getAttrs('select')), empty_label="Ligne")

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(ProductForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['line'].queryset = user.lines.all()

class EmplacementForm(ModelForm):
    class Meta:
        model = Emplacement
        fields = ['designation', 'categ']
    
    designation = forms.CharField(widget=forms.TextInput(attrs=getAttrs('control','Designation')))
    categ = forms.ChoiceField(choices=Emplacement.DESTINATION_CHOICES, widget=forms.Select(attrs=getAttrs('select')))

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
    
    destination = forms.ModelChoiceField(queryset=Emplacement.objects.filter(categ='Déstination'), widget=forms.Select(attrs=getAttrs('select')), empty_label="Déstination")
    depart = forms.ModelChoiceField(queryset=Emplacement.objects.filter(categ='Départ'), widget=forms.Select(attrs=getAttrs('select')), empty_label="Départ")
    tonnage = forms.ModelChoiceField(queryset=Tonnage.objects.all(), widget=forms.Select(attrs=getAttrs('select')), empty_label="Tonnage")
    fournisseur = forms.ModelChoiceField(queryset=Fournisseur.objects.all(), widget=forms.Select(attrs=getAttrs('select')), empty_label="Fournisseur")
    price = forms.FloatField(widget=forms.NumberInput(attrs= getAttrs('control','Prix')))
    class Meta:
        model = Price
        fields = ['destination', 'depart', 'fournisseur', 'tonnage', 'price']


class ReportForm(ModelForm):

    prix = forms.ModelChoiceField(queryset=Price.objects.all(), widget=forms.HiddenInput(), empty_label="Prix")
    date_dep = forms.DateField(initial=timezone.now().date(), widget=forms.widgets.DateInput(attrs= getAttrs('date'), format='%Y-%m-%d'))
    chauffeur = forms.CharField(widget=forms.TextInput(attrs= getAttrs('control','Chauffeur')))
    n_bl = forms.IntegerField(widget=forms.NumberInput(attrs= getAttrs('control','N° BL')))
    observation = forms.CharField(widget=forms.Textarea(attrs=getAttrs('textarea','Observation')), required=False)
    line = forms.ModelChoiceField(queryset=Line.objects.all(), widget=forms.Select(attrs= getAttrs('select')), empty_label="Ligne")

    destination = forms.ModelChoiceField(queryset=Emplacement.objects.filter(categ='Déstination'), widget=forms.Select(attrs=getAttrs('select')), empty_label="Déstination")
    depart = forms.ModelChoiceField(queryset=Emplacement.objects.filter(categ='Départ'), widget=forms.Select(attrs=getAttrs('select')), empty_label="Départ")
    tonnage = forms.ModelChoiceField(queryset=Tonnage.objects.all(), widget=forms.Select(attrs=getAttrs('select')), empty_label="Tonnage")
    fournisseur = forms.ModelChoiceField(queryset=Fournisseur.objects.all(), widget=forms.Select(attrs=getAttrs('select')), empty_label="Fournisseur")
    price = forms.FloatField(widget=forms.NumberInput(attrs= getAttrs('control','Prix')))

    class Meta:
        model = Report
        fields = ['prix', 'date_dep', 'chauffeur', 'n_bl', 'line', 'observation', 'destination', 'depart', 'tonnage', 'fournisseur', 'price']

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        admin = kwargs.pop('admin', None)
        lines = kwargs.pop('lines', None)
        super(ReportForm, self).__init__(*args, **kwargs)
        self.fields["prix"].widget.attrs['disabled'] = True
        self.fields["price"].widget.attrs['disabled'] = True
        self.fields['line'].initial = lines.first()
        if instance:
            self.fields['destination'].initial = instance.prix.destination
            self.fields['depart'].initial = instance.prix.depart
            self.fields['tonnage'].initial = instance.prix.tonnage
            self.fields['fournisseur'].initial = instance.prix.fournisseur
            self.fields['price'].initial = instance.prix.price
        if not admin and len(lines) < 2:
            self.fields['line'].widget.attrs['disabled'] = True
        else:
            self.fields['line'].queryset = lines

class PTransportedForm(ModelForm):
    class Meta:
        model = PTransported
        fields = '__all__'

    product = forms.ModelChoiceField(queryset=Product.objects.all(), widget=forms.Select(attrs=getAttrs('select')), empty_label="Product")
    qte_transported = forms.FloatField(widget=forms.NumberInput(attrs= getAttrs('control','Qte Consomée')))
    observation = forms.CharField(widget=forms.Textarea(attrs=getAttrs('textarea','Observation')), required=False)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        # instance = kwargs.get('instance')
        super(PTransportedForm, self).__init__(*args, **kwargs)
        if user: 
            self.fields['product'].queryset = Product.objects.filter(line__in=user.lines.all())

PTransportedsFormSet = inlineformset_factory(Report, PTransported, form=PTransportedForm, fields=['product', 'qte_transported', 'observation'], extra=0)
