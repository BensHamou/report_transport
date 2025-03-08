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
from django.views.generic.detail import DetailView
from functools import wraps
from django.template.defaulttags import register
import datetime
from fleet.models import *
from commercial.models import *
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from datetime import datetime, timedelta

@register.filter
def startwith(value, word):
    return str(value).startswith(word)

@register.filter
def is_login(messages):
    for message in messages:
        if str(message).startswith('LOGIN : '):
            return True
    return False

@register.filter
def loginerror(value, word):
    return str(value)[len(word):]

def check_creator(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if 'id' in kwargs:
            rep_id = kwargs['id']
        elif 'pk' in kwargs:
            rep_id = kwargs['pk']
        report = Report.objects.get(id=rep_id)
        if report.creator != request.user and request.user.role != 'Admin':
            return render(request, '403.html', status=403)
        return view_func(request, *args, **kwargs)
    return wrapper

def check_creatorPTransported(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        ptransported_id = kwargs.get('pk')
        ptransported = PTransported.objects.get(id=ptransported_id)
        if not ((ptransported.report.state == 'Brouillon' and request.user == ptransported.report.creator) or request.user.is_admin):
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
    page_size_param = request.GET.get('page_size')
    page_size = int(page_size_param) if page_size_param else 12   
    paginator = Paginator(emplacements, page_size)
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
            page_size = request.GET.get('page_size', '12')
            search = request.GET.get('search', '')
            redirect_url = f'{url_path}?cache={cache_param}&page={page}&page_size={page_size}&search={search}'
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
    page_size_param = request.GET.get('page_size')
    page_size = int(page_size_param) if page_size_param else 12   
    paginator = Paginator(fournisseurs, page_size)
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
            page_size = request.GET.get('page_size', '12')
            search = request.GET.get('search', '')
            redirect_url = f'{url_path}?cache={cache_param}&page={page}&page_size={page_size}&search={search}'
            return redirect(redirect_url)
    context = {'form': form, 'fournisseur': fournisseur}    

    return render(request, 'fournisseur_form.html', context)

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
import json
from datetime import datetime

@login_required(login_url='login')
@admin_required
@csrf_protect
@require_http_methods(["POST"])
def sendSupplierEmail(request, id):
    try:
        body = json.loads(request.body)
        from_date = body.get('from_date')
        to_date = body.get('to_date')
        from_date = datetime.strptime(from_date, '%Y-%m-%d') if from_date else None
        to_date = datetime.strptime(to_date, '%Y-%m-%d') if to_date else None

        fournisseur = Fournisseur.objects.get(id=id)
        sendEmail(fournisseur, from_date, to_date)
        return JsonResponse({'success': True, 'message': 'E-mail envoyé avec succès'})

    except Fournisseur.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Fournisseur non trouvé'}, status=200)
    
    except ValueError as ve:
        return JsonResponse({'success': False, 'message': f'Format de date invalide: {str(ve)}'}, status=200)
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=200)

def sendEmail(supplier, from_date, to_date):

    vehicles = Vehicle.objects.filter(fournisseur=supplier)

    results = []

    for vehicle in vehicles:
        plannings = Planning.objects.filter(fournisseur=supplier,vehicle=vehicle, date_honored__range=[from_date, to_date], state='Livraison Confirmé')
        sorted_plannings = sorted(plannings, key=lambda p: p.delivery_date if p.delivery_date else datetime.min)

        total_distance_with = 0
        total_distance_without = 0
        total_price = 0

        previous_destination = None

        for planning in sorted_plannings:
            if previous_destination:
                distance_without = Distance.objects.filter(site=planning.site, emplacement=previous_destination).first()
                if distance_without:
                    total_distance_without += distance_without.distance

            distance_with = Distance.objects.filter(site=planning.site, emplacement=planning.destination).first()
            if distance_with:
                total_distance_with += distance_with.distance

            previous_destination = planning.destination

            date_planning_final = planning.date_planning_final
            
            planning_price = Price.objects.filter(depart=planning.site, destination=planning.destination,
                                         fournisseur=planning.fournisseur, tonnage=planning.tonnage,
                                         date_from__lte=date_planning_final).filter(Q(date_to__gte=date_planning_final) | Q(date_to__isnull=True)).last().price

            total_price += planning_price

        total_consumption_with = total_distance_with * vehicle.consommation_with
        total_consumption_without = total_distance_without * vehicle.consommation_without
        total_consumption = total_consumption_with + total_consumption_without
        cost = Cost.objects.filter(fournisseur=supplier, min_km__lte=total_distance_with, max_km__gte=total_distance_with).order_by('id').last()
        if cost:
            frais_mission = f'{cost.tarif} DZD'
        else:
            frais_mission = '/'

        days_in_period = (to_date - from_date).days
        relative_objectif = round(vehicle.objectif * days_in_period / 30, 2)


        if total_distance_with > 0:
            results.append({
                'immatriculation': vehicle.immatriculation, 
                'km_with_marchandise': total_distance_with, 
                'km_without_marchandise': total_distance_without,
                'price': total_price, 
                'objectif': relative_objectif, 
                'consommation_with': total_consumption_with, 
                'consommation_without': total_consumption_without,
                'total_consumption': total_consumption,
                'frais_mission': frais_mission,
                })
        
    subject = f'Calcule Rotations {supplier.designation}'
    addresses = ['mohammed.senoussaoui@grupopuma-dz.com', 'mohammed.benslimane@groupe-hasnaoui.com']

    html_message = render_to_string('email_template.html', {'results': results, 'supplier': supplier.designation})
    email = EmailMultiAlternatives(subject, None, 'Puma Trans', addresses)
    email.attach_alternative(html_message, "text/html") 
    email.send()    


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
    page_size_param = request.GET.get('page_size')
    page_size = int(page_size_param) if page_size_param else 12   
    paginator = Paginator(products, page_size)
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
            page = request.GET.get('page', '1')
            page_size = request.GET.get('page_size', '12')
            search = request.GET.get('search', '')
            redirect_url = f'{url_path}?cache={cache_param}&page={page}&page_size={page_size}&search={search}'
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
            page_size = request.GET.get('page_size', '12')
            search = request.GET.get('search', '')
            redirect_url = f'{url_path}?cache={cache_param}&page={page}&page_size={page_size}&search={search}'
            return redirect(redirect_url)
    context = {'form': form, 'product': product }

    return render(request, 'product_form.html', context)

# Prices
@login_required(login_url='login')
@admin_required
def listPriceView(request):
    prices = Price.objects.filter(depart__in=request.user.sites.all()).order_by('-date_modified')
    filteredData = PriceFilter(request.GET, queryset=prices)
    prices = filteredData.qs
    page_size_param = request.GET.get('page_size')
    page_size = int(page_size_param) if page_size_param else 12   
    paginator = Paginator(prices, page_size)
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
        if self.request.user.role == 'Admin':
            return True
        if report.creator == self.request.user and report.state == 'Brouillon' and self.request.user.role == 'Logisticien':
            return True
        return False

    def dispatch(self, request, *args, **kwargs):
        report = self.get_object()  
        if not self.check_editor(report):
            return render(request, '403.html', status=403)
        return super().dispatch(request, *args, **kwargs)
    
class CheckReportViewerMixin:
    def check_viewer(self, report):
        if self.request.user.role == 'Admin':
            return True
        sites = self.request.user.sites.all()
        if report.site in sites and self.request.user.role in ['Observateur', 'Logisticien']:
            return True
        return False

    def dispatch(self, request, *args, **kwargs):
        report = self.get_object()  
        if not self.check_viewer(report):
            return render(request, '403.html', status=403)
        return super().dispatch(request, *args, **kwargs)
    
class CheckReportListViewerMixin:
    def check_viewer(self):
        if self.request.user.role in ['Admin', 'Logisticien', 'Observateur']:
            return True
        return False

    def dispatch(self, request, *args, **kwargs):
        if not self.check_viewer():
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
        kwargs['role'] = self.request.user.role
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

class ReportList(LoginRequiredMixin, CheckReportListViewerMixin, FilterView):
    model = Report
    template_name = "list_reports.html"
    context_object_name = "reports"
    filterset_class = ReportFilter
    ordering = ['-date_created', '-date_dep']
    
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
@check_creatorPTransported
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
    date_transport = request.GET.get('date')
    try:
        price = Price.objects.filter(destination=request.GET.get('destination'),
                                    depart=request.GET.get('site'),
                                    tonnage=request.GET.get('tonnage'),
                                    fournisseur=request.GET.get('fournisseur'),
                                    date_from__lte=date_transport
                                ).filter(Q(date_to__gte=date_transport) | Q(date_to__isnull=True)).order_by('id').last()
        if price:
            return JsonResponse({'exist': True, 'price_id': price.id, 'price_prix': price.price })
        else:
            return JsonResponse({'exist': False, 'price_id': 0, 'price_prix': 0 })
    except Price.DoesNotExist:
        return JsonResponse({'exist': False, 'price_id': 0, 'price_prix': 0 })

    