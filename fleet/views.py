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


# Drivers
@login_required(login_url='login')
@admin_required
def listDriverView(request):
    drivers = Driver.objects.all().order_by('id')
    filteredData = DriverFilter(request.GET, queryset=drivers)
    drivers = filteredData.qs
    page_size_param = request.GET.get('page_size')
    page_size = int(page_size_param) if page_size_param else 12   
    paginator = Paginator(drivers, page_size)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {'page': page, 'filtredData': filteredData}
    return render(request, 'list_drivers.html', context)

@login_required(login_url='login')
@admin_required
def deleteDriverView(request, id):
    driver = Driver.objects.get(id=id)
    driver.delete()
    cache_param = str(uuid.uuid4())
    url_path = reverse('drivers')
    redirect_url = f'{url_path}?cache={cache_param}'
    return redirect(redirect_url)

@login_required(login_url='login')
@admin_required
def createDriverView(request):
    form = DriverForm()
    if request.method == 'POST':
        form = DriverForm(request.POST)
        if form.is_valid():
            form.save()
            cache_param = str(uuid.uuid4())
            url_path = reverse('drivers')
            redirect_url = f'{url_path}?cache={cache_param}'
            return redirect(redirect_url)
    context = {'form': form}
    return render(request, 'driver_form.html', context)

@login_required(login_url='login')
@admin_required
def editDriverView(request, id):
    driver = Driver.objects.get(id=id)
    form = DriverForm(instance=driver)
    if request.method == 'POST':
        form = DriverForm(request.POST, instance=driver)
        if form.is_valid():
            form.save()
            cache_param = str(uuid.uuid4())
            url_path = reverse('drivers')
            page = request.GET.get('page', '1')
            page_size = request.GET.get('page_size', '12')
            search = request.GET.get('search', '')
            redirect_url = f'{url_path}?cache={cache_param}&page={page}&page_size={page_size}&search={search}'
            return redirect(redirect_url)
    context = {'form': form, 'driver': driver}

    return render(request, 'driver_form.html', context)

# Vehicle
@login_required(login_url='login')
@admin_required
def listVehicleView(request):
    vehicles = Vehicle.objects.all().order_by('id')
    filteredData = VehicleFilter(request.GET, queryset=vehicles)
    drivers = filteredData.qs
    page_size_param = request.GET.get('page_size')
    page_size = int(page_size_param) if page_size_param else 12   
    paginator = Paginator(drivers, page_size)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {'page': page, 'filtredData': filteredData}
    return render(request, 'list_vehicles.html', context)

@login_required(login_url='login')
@admin_required
def deleteVehicleView(request, id):
    vehicle = Vehicle.objects.get(id=id)
    vehicle.delete()
    cache_param = str(uuid.uuid4())
    url_path = reverse('vehicles')
    redirect_url = f'{url_path}?cache={cache_param}'
    return redirect(redirect_url)

@login_required(login_url='login')
@admin_required
def createVehicleView(request):
    form = VehicleForm()
    if request.method == 'POST':
        form = VehicleForm(request.POST)
        if form.is_valid():
            form.save()
            cache_param = str(uuid.uuid4())
            url_path = reverse('vehicles')
            redirect_url = f'{url_path}?cache={cache_param}'
            return redirect(redirect_url)
    context = {'form': form}
    return render(request, 'vehicle_form.html', context)

@login_required(login_url='login')
@admin_required
def editVehicleView(request, id):
    vehicle = Vehicle.objects.get(id=id)
    form = VehicleForm(instance=vehicle)
    if request.method == 'POST':
        form = VehicleForm(request.POST, instance=vehicle)
        if form.is_valid():
            form.save()
            cache_param = str(uuid.uuid4())
            url_path = reverse('vehicles')
            page = request.GET.get('page', '1')
            page_size = request.GET.get('page_size', '12')
            search = request.GET.get('search', '')
            redirect_url = f'{url_path}?cache={cache_param}&page={page}&page_size={page_size}&search={search}'
            return redirect(redirect_url)
    context = {'form': form, 'vehicle': vehicle}

    return render(request, 'vehicle_form.html', context)

