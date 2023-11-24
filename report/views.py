from django.shortcuts import render
from account.models import *
from .models import *
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from account.views import admin_required
import uuid
from .forms import *
from .filters import *
from django.core.paginator import Paginator
from django.urls import reverse
from django.http import JsonResponse
from django.views.generic.edit import CreateView, UpdateView
from django_filters.views import FilterView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.views.generic.detail import DetailView
from django.db.models import Count
from django.template.defaulttags import register
from functools import wraps
from django.core.mail import send_mail
from django.utils.html import format_html
from datetime import datetime


def check_creator(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if 'id' in kwargs:
            rep_id = kwargs['id']
        elif 'pk' in kwargs:
            rep_id = kwargs['pk']
        report = Report.objects.get(id=rep_id)
        if report.creator != request.user and request.user.is_admin:
            return render(request, '403.html', status=403)
        return view_func(request, *args, **kwargs)
    return wrapper

def check_creatoPTransported(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        ptransported_id = kwargs.get('pk')
        ptransported = PTransported.objects.get(id=ptransported_id)
        if not ((ptransported.report.state == 'Brouillon' and request.user == ptransported.report.creator) or request.user.id_admin):
            return render(request, '403.html', status=403)
        return view_func(request, *args, **kwargs)
    return wrapper


# Emplacements
@login_required(login_url='login')
@admin_required
def listEmplacementView(request):
    emplacements = Emplacement.objects.all().order_by('id')
    filteredData = EmplacementFilter(request.GET, queryset=emplacements)
    emplacements = filteredData.qs
    paginator = Paginator(emplacements, 7)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'page': page, 'filtredData': filteredData, 
    }
    return render(request, 'list_emplacements.html', context)

@login_required(login_url='login')
@admin_required
def deleteEmplacementView(request, id):
    emplacement = Emplacement.objects.get(id=id)
    emplacement.delete()
    cache_param = str(uuid.uuid4())
    url_path = reverse('emplacements')
    redirect_url = f'{url_path}?cache={cache_param}'
    return redirect(redirect_url)

@login_required(login_url='login')
@admin_required
def createEmplacementView(request):
    form = EmplacementForm()
    if request.method == 'POST':
        form = EmplacementForm(request.POST)
        if form.is_valid():
            form.save()
            cache_param = str(uuid.uuid4())
            url_path = reverse('emplacements')
            redirect_url = f'{url_path}?cache={cache_param}'
            return redirect(redirect_url)
    context = {'form': form}
    return render(request, 'emplacement_form.html', context)

@login_required(login_url='login')
@admin_required
def editEmplacementView(request, id):
    emplacement = Emplacement.objects.get(id=id)
    form = EmplacementForm(instance=emplacement)
    if request.method == 'POST':
        form = EmplacementForm(request.POST, instance=emplacement)
        if form.is_valid():
            form.save()
            cache_param = str(uuid.uuid4())
            url_path = reverse('emplacements')
            page = request.GET.get('page', '1')
            redirect_url = f'{url_path}?cache={cache_param}&page={page}'
            return redirect(redirect_url)
    context = {'form': form, 'emplacement': emplacement}

    return render(request, 'emplacement_form.html', context)

# Fournisseur
@login_required(login_url='login')
@admin_required
def listFournisseurView(request):
    fournisseurs = Fournisseur.objects.all().order_by('id')
    filteredData = FournisseurFilter(request.GET, queryset=fournisseurs)
    fournisseurs = filteredData.qs
    paginator = Paginator(fournisseurs, 7)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'page': page, 'filtredData': filteredData, 
    }
    return render(request, 'list_fournisseurs.html', context)

@login_required(login_url='login')
@admin_required
def deleteFournisseurView(request, id):
    fournisseur = Fournisseur.objects.get(id=id)
    fournisseur.delete()
    cache_param = str(uuid.uuid4())
    url_path = reverse('fournisseurs')
    redirect_url = f'{url_path}?cache={cache_param}'
    return redirect(redirect_url)

@login_required(login_url='login')
@admin_required
def createFournisseurView(request):
    form = FournisseurForm()
    if request.method == 'POST':
        form = FournisseurForm(request.POST)
        if form.is_valid():
            form.save()
            cache_param = str(uuid.uuid4())
            url_path = reverse('fournisseurs')
            redirect_url = f'{url_path}?cache={cache_param}'
            return redirect(redirect_url)
    context = {'form': form}
    return render(request, 'fournisseur_form.html', context)

@login_required(login_url='login')
@admin_required
def editFournisseurView(request, id):
    fournisseur = Fournisseur.objects.get(id=id)
    form = FournisseurForm(instance=fournisseur)
    if request.method == 'POST':
        form = FournisseurForm(request.POST, instance=fournisseur)
        if form.is_valid():
            form.save()
            cache_param = str(uuid.uuid4())
            url_path = reverse('fournisseurs')
            page = request.GET.get('page', '1')
            redirect_url = f'{url_path}?cache={cache_param}&page={page}'
            return redirect(redirect_url)
    context = {'form': form, 'fournisseur': fournisseur}

    return render(request, 'fournisseur_form.html', context)

# Tonnages
@login_required(login_url='login')
@admin_required
def listTonnageView(request):
    tonnages = Tonnage.objects.all().order_by('id')
    filteredData = TonnageFilter(request.GET, queryset=tonnages)
    tonnages = filteredData.qs
    paginator = Paginator(tonnages, 7)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'page': page, 'filtredData': filteredData, 
    }
    return render(request, 'list_tonnages.html', context)

@login_required(login_url='login')
@admin_required
def deleteTonnageView(request, id):
    tonnage = Tonnage.objects.get(id=id)
    tonnage.delete()
    cache_param = str(uuid.uuid4())
    url_path = reverse('tonnages')
    redirect_url = f'{url_path}?cache={cache_param}'
    return redirect(redirect_url)

@login_required(login_url='login')
@admin_required
def createTonnageView(request):
    form = TonnageForm()
    if request.method == 'POST':
        form = TonnageForm(request.POST)
        if form.is_valid():
            form.save()
            cache_param = str(uuid.uuid4())
            url_path = reverse('tonnages')
            redirect_url = f'{url_path}?cache={cache_param}'
            return redirect(redirect_url)
    context = {'form': form}
    return render(request, 'tonnage_form.html', context)

@login_required(login_url='login')
@admin_required
def editTonnageView(request, id):
    tonnage = Tonnage.objects.get(id=id)
    form = TonnageForm(instance=tonnage)
    if request.method == 'POST':
        form = TonnageForm(request.POST, instance=tonnage)
        if form.is_valid():
            form.save()
            cache_param = str(uuid.uuid4())
            url_path = reverse('tonnages')
            page = request.GET.get('page', '1')
            redirect_url = f'{url_path}?cache={cache_param}&page={page}'
            return redirect(redirect_url)
    context = {'form': form, 'tonnage': tonnage}

    return render(request, 'tonnage_form.html', context)

# PRODUCTS
@login_required(login_url='login')
@admin_required 
def listProductList(request):
    products = Product.objects.all().order_by('id')
    filteredData = ProductFilter(request.GET, queryset=products)
    products = filteredData.qs
    paginator = Paginator(products, 7)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'page': page, 'filtredData': filteredData, 
    }
    return render(request, 'list_products.html', context)

@login_required(login_url='login')
@admin_required
def deleteProductView(request, id):
    product = Product.objects.get(id=id)
    product.delete()
    cache_param = str(uuid.uuid4())
    url_path = reverse('products')

    redirect_url = f'{url_path}?cache={cache_param}'

    return redirect(redirect_url)

@login_required(login_url='login')
@admin_required
def createProductView(request):
    form = ProductForm()
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            cache_param = str(uuid.uuid4())
            url_path = reverse('products')
            redirect_url = f'{url_path}?cache={cache_param}'
            return redirect(redirect_url)
    context = {'form': form }
    return render(request, 'product_form.html', context)

@login_required(login_url='login')
@admin_required
def editProductView(request, id):
    product = Product.objects.get(id=id)

    form = ProductForm(instance=product)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            cache_param = str(uuid.uuid4())
            url_path = reverse('products')
            page = request.GET.get('page', '1')
            redirect_url = f'{url_path}?cache={cache_param}&page={page}'
            return redirect(redirect_url)
    context = {'form': form, 'product': product }

    return render(request, 'product_form.html', context)

# Prices
@login_required(login_url='login')
@admin_required
def listPriceView(request):
    prices = Price.objects.filter(depart__in=request.user.sites.all()).order_by('id')
    filteredData = PriceFilter(request.GET, queryset=prices)
    prices = filteredData.qs
    paginator = Paginator(prices, 7)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'page': page, 'filtredData': filteredData, 
    }
    return render(request, 'list_prices.html', context)

@login_required(login_url='login')
@admin_required
def deletePriceView(request, id):
    price = Price.objects.get(id=id)
    price.delete()
    cache_param = str(uuid.uuid4())
    url_path = reverse('prices')
    redirect_url = f'{url_path}?cache={cache_param}'
    return redirect(redirect_url)

@login_required(login_url='login')
@admin_required
def createPriceView(request):
    form = PriceForm(user = request.user)
    if request.method == 'POST':
        form = PriceForm(request.POST, user = request.user)
        if form.is_valid():
            form.save()
            cache_param = str(uuid.uuid4())
            url_path = reverse('prices')
            redirect_url = f'{url_path}?cache={cache_param}'
            return redirect(redirect_url)
    context = {'form': form}
    return render(request, 'price_form.html', context)

@login_required(login_url='login')
@admin_required
def editPriceView(request, id):
    price = Price.objects.get(id=id)
    form = PriceForm(instance=price)
    if request.method == 'POST':
        form = PriceForm(request.POST, instance=price)
        if form.is_valid():
            form.save()
            cache_param = str(uuid.uuid4())
            url_path = reverse('prices')
            page = request.GET.get('page', '1')
            redirect_url = f'{url_path}?cache={cache_param}&page={page}'
            return redirect(redirect_url)
    context = {'form': form, 'price': price}

    return render(request, 'price_form.html', context)

#REPORTS

class CheckEditorMixin:
    def check_editor(self, report):
        if (report.creator != self.request.user or report.state != 'Brouillon') and not self.request.user.is_admin:
            return False
        return True

    def dispatch(self, request, *args, **kwargs):
        report = self.get_object()  
        if not self.check_editor(report):
            return render(request, '403.html', status=403)
        return super().dispatch(request, *args, **kwargs)
    
class CheckReportViewerMixin:
    def check_viewer(self, report):
        sites = self.request.user.sites.all()
        if report.site not in sites and self.request.user.is_admin:
            return False
        return True

    def dispatch(self, request, *args, **kwargs):
        report = self.get_object()  
        if not self.check_viewer(report):
            return render(request, '403.html', status=403)
        return super().dispatch(request, *args, **kwargs)

class ReportInline():
    form_class = ReportForm
    model = Report
    template_name = "report_form.html"    
    login_url = 'login'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['sites'] = self.request.user.sites.all()
        return kwargs

    def form_valid(self, form):
        named_formsets = self.get_named_formsets()
        if not all((x.is_valid() for x in named_formsets.values())):
            return self.render_to_response(self.get_context_data(form=form))
        report = form.save(commit=False)
        if not report.state or report.state == 'Brouillon':
            report.state = 'Brouillon'
        
        if not report.id:
            report.creator = self.request.user
        
        report.save()
        new = True
        if self.object:
            new = False
        else:
            self.object = report

        for name, formset in named_formsets.items():
            formset_save_func = getattr(self, 'formset_{0}_valid'.format(name), None)
            if formset_save_func is not None:
                formset_save_func(formset)
            else:
                formset.save()

        if not new:
            cache_param = str(uuid.uuid4())
            url_path = reverse('view_report', args=[self.object.pk])
            redirect_url = f'{url_path}?cache={cache_param}'
            return redirect(redirect_url)
        return redirect('reports')

    def formset_ptransporteds_valid(self, formset):
        ptransporteds = formset.save(commit=False)
        for obj in formset.deleted_objects:
            obj.delete()
        for ptransported in ptransporteds:
            ptransported.report = self.object
            ptransported.save()

class ReportCreate(LoginRequiredMixin, ReportInline, CreateView):

    def get_context_data(self, **kwargs):
        ctx = super(ReportCreate, self).get_context_data(**kwargs)
        ctx['named_formsets'] = self.get_named_formsets()
        return ctx

    def get_named_formsets(self):
        if self.request.method == "GET":
            return {
                'ptransporteds': PTransportedsFormSet(prefix='ptransporteds'),
            }
        else:
            return {
                'ptransporteds': PTransportedsFormSet(self.request.POST or None, prefix='ptransporteds'),
            }

class ReportUpdate(LoginRequiredMixin, CheckEditorMixin, ReportInline, UpdateView):

    def get_context_data(self, **kwargs):
        ctx = super(ReportUpdate, self).get_context_data(**kwargs)
        ctx['named_formsets'] = self.get_named_formsets()
        return ctx

    def get_named_formsets(self):
        return {
            'ptransporteds': PTransportedsFormSet(self.request.POST or None, instance=self.object, prefix='ptransporteds'),
        }
    
class ReportDetail(LoginRequiredMixin, CheckReportViewerMixin, DetailView):
    model = Report
    template_name = 'report_details.html'
    context_object_name = 'report'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fields = [field for field in self.model._meta.get_fields() if field.concrete]
        context['fields'] = fields
        return context

class ReportList(LoginRequiredMixin, FilterView):
    model = Report
    template_name = "list_reports.html"
    context_object_name = "reports"
    filterset_class = ReportFilter
    ordering = ['-date_dep']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        sites = self.request.user.sites.all()
        queryset = queryset.filter(site__in=sites)
        return queryset   

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page_size_param = self.request.GET.get('page_size')
        page_size = int(page_size_param) if page_size_param else 12        
        paginator = Paginator(context['reports'], page_size)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['page'] = page_obj
        return context

@login_required(login_url='login')
@check_creator
def deleteReportView(request, id):
    price = Report.objects.get(id=id)
    price.delete()
    cache_param = str(uuid.uuid4())
    url_path = reverse('reports')
    redirect_url = f'{url_path}?cache={cache_param}'
    return redirect(redirect_url)


@login_required(login_url='login')
@check_creatoPTransported
def delete_product(request, pk):
    try:
        ptransported = PTransported.objects.get(id=pk)
    except PTransported.DoesNotExist:
        messages.success(
            request, 'Produit Transported Does not exit'
            )
        url_path = reverse('edit_report', args=[ptransported.report.id])
        cache_param = str(uuid.uuid4())
        redirect_url = f'{url_path}?cache={cache_param}'
        return redirect(redirect_url)

    ptransported.delete()
    messages.success(
            request, 'Produit Transported deleted successfully'
            )
    url_path = reverse('edit_report', args=[ptransported.report.id])
    cache_param = str(uuid.uuid4())
    redirect_url = f'{url_path}?cache={cache_param}'
    return redirect(redirect_url)


@login_required(login_url='login')
@check_creator
def confirmReport(request, pk):
    try:
        report = Report.objects.get(id=pk)
    except Report.DoesNotExist:
        messages.success(request, 'Report Does not exit')
    
    if report.state != 'Confirmé':
        report.state = 'Confirmé'
        report.save()
    
    url_path = reverse('view_report', args=[report.id])
    cache_param = str(uuid.uuid4())
    redirect_url = f'{url_path}?cache={cache_param}'
    return redirect(redirect_url)

@login_required(login_url='login')
@check_creator
def cancelReport(request, pk):
    try:
        report = Report.objects.get(id=pk)
    except Report.DoesNotExist:
        messages.success(request, 'Report Does not exit')
    
    if report.state != 'Annulé':
        report.state = 'Annulé'
        report.save()
    
    url_path = reverse('view_report', args=[report.id])
    cache_param = str(uuid.uuid4())
    redirect_url = f'{url_path}?cache={cache_param}'
    return redirect(redirect_url)

@login_required(login_url='login')
def getPrice(request):
    try:
       price = Price.objects.get(destination = request.GET.get('destination'), depart = request.GET.get('site'), 
                                 tonnage = request.GET.get('tonnage'), fournisseur = request.GET.get('fournisseur'))
       
       return JsonResponse({'exist': True, 'price_id': price.id, 'price_prix': price.price })
    except Price.DoesNotExist:
        return JsonResponse({'exist': False, 'price_id': 0, 'price_prix': 0 })

    