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

# Prices
@login_required(login_url='login')
@admin_required
def listPriceView(request):
    prices = Price.objects.all().order_by('id')
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
    form = PriceForm()
    if request.method == 'POST':
        form = PriceForm(request.POST)
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

# Reports
@login_required(login_url='login')
@admin_required
def listReportView(request):
    reports = Report.objects.all().order_by('id')
    filteredData = ReportFilter(request.GET, queryset=reports)
    reports = filteredData.qs
    paginator = Paginator(reports, 7)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'page': page, 'filtredData': filteredData, 
    }
    return render(request, 'list_reports.html', context)

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
def createReportView(request):
    form = ReportForm()
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False) 
            report.creator = request.user
            report.state = 'Brouillon'
            report.save()
            cache_param = str(uuid.uuid4())
            url_path = reverse('reports')
            redirect_url = f'{url_path}?cache={cache_param}'
            return redirect(redirect_url)
    context = {'form': form}
    return render(request, 'report_form.html', context)

@login_required(login_url='login')
@check_creator
def editReportView(request, id):
    report = Report.objects.get(id=id)
    form = ReportForm(instance=report)
    if request.method == 'POST':
        form = ReportForm(request.POST, instance=report)
        if form.is_valid():
            form.save()
            cache_param = str(uuid.uuid4())
            url_path = reverse('view_report', args=[report.id])
            page = request.GET.get('page', '1')
            redirect_url = f'{url_path}?cache={cache_param}&page={page}'
            return redirect(redirect_url)
    context = {'form': form, 'report': report}

    return render(request, 'report_form.html', context)

@login_required(login_url='login')
@check_creator
def detailReportView(request, id):
    report = Report.objects.get(id=id)
    context = { 'report': report }
    return render(request, 'report_details.html', context)

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