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
from commercial.views import checkAdminOrLogisticien

from django.views.generic.edit import CreateView, UpdateView
from django_filters.views import FilterView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.detail import DetailView


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

# ReparationType Views
@login_required(login_url='login')
@admin_required
def listReparationTypeView(request):
    types = ReparationType.objects.all().order_by('id')
    filteredData = ReparationTypeFilter(request.GET, queryset=types)
    page_size_param = request.GET.get('page_size')
    page_size = int(page_size_param) if page_size_param else 12
    paginator = Paginator(filteredData.qs, page_size)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {'page': page, 'filtredData': filteredData}
    return render(request, 'list_reparation_types.html', context)

@login_required(login_url='login')
@admin_required
def deleteReparationTypeView(request, id):
    item = ReparationType.objects.get(id=id)
    item.delete()
    cache_param = str(uuid.uuid4())
    url_path = reverse('reparation_types')
    redirect_url = f'{url_path}?cache={cache_param}'
    return redirect(redirect_url)

@login_required(login_url='login')
@admin_required
def createReparationTypeView(request):
    form = ReparationTypeForm()
    if request.method == 'POST':
        form = ReparationTypeForm(request.POST)
        if form.is_valid():
            form.save()
            cache_param = str(uuid.uuid4())
            url_path = reverse('reparation_types')
            redirect_url = f'{url_path}?cache={cache_param}'
            return redirect(redirect_url)
    context = {'form': form}
    return render(request, 'reparation_type_form.html', context)

@login_required(login_url='login')
@admin_required
def editReparationTypeView(request, id):
    item = ReparationType.objects.get(id=id)
    form = ReparationTypeForm(instance=item)
    if request.method == 'POST':
        form = ReparationTypeForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            cache_param = str(uuid.uuid4())
            url_path = reverse('reparation_types')
            page = request.GET.get('page', '1')
            page_size = request.GET.get('page_size', '12')
            search = request.GET.get('search', '')
            redirect_url = f'{url_path}?cache={cache_param}&page={page}&page_size={page_size}&search={search}'
            return redirect(redirect_url)
    context = {'form': form, 'reparation_type': item}
    return render(request, 'reparation_type_form.html', context)

# Reparation Views
@login_required(login_url='login')
@checkAdminOrLogisticien
def listReparationView(request):
    items = Reparation.objects.all().order_by('id')
    filteredData = ReparationFilter(request.GET, queryset=items)
    page_size_param = request.GET.get('page_size')
    page_size = int(page_size_param) if page_size_param else 12
    paginator = Paginator(filteredData.qs, page_size)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {'page': page, 'filtredData': filteredData}
    return render(request, 'list_reparations.html', context)

@login_required(login_url='login')
@checkAdminOrLogisticien
def deleteReparationView(request, id):
    item = Reparation.objects.get(id=id)
    item.delete()
    cache_param = str(uuid.uuid4())
    url_path = reverse('reparations')
    redirect_url = f'{url_path}?cache={cache_param}'
    return redirect(redirect_url)

@login_required(login_url='login')
@checkAdminOrLogisticien
def createReparationView(request):
    form = ReparationForm()
    if request.method == 'POST':
        form = ReparationForm(request.POST)
        if form.is_valid():
            form.save()
            cache_param = str(uuid.uuid4())
            url_path = reverse('reparations')
            redirect_url = f'{url_path}?cache={cache_param}'
            return redirect(redirect_url)
    context = {'form': form}
    return render(request, 'reparation_form.html', context)

@login_required(login_url='login')
@checkAdminOrLogisticien
def editReparationView(request, id):
    item = Reparation.objects.get(id=id)
    form = ReparationForm(instance=item)
    if request.method == 'POST':
        form = ReparationForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            cache_param = str(uuid.uuid4())
            url_path = reverse('reparations')
            page = request.GET.get('page', '1')
            page_size = request.GET.get('page_size', '12')
            search = request.GET.get('search', '')
            redirect_url = f'{url_path}?cache={cache_param}&page={page}&page_size={page_size}&search={search}'
            return redirect(redirect_url)
    context = {'form': form, 'reparation': item}
    return render(request, 'reparation_form.html', context)

# FuelRefill Views
@login_required(login_url='login')
@checkAdminOrLogisticien
def listFuelRefillView(request):
    items = FuelRefill.objects.all().order_by('id')
    filteredData = FuelRefillFilter(request.GET, queryset=items)
    page_size_param = request.GET.get('page_size')
    page_size = int(page_size_param) if page_size_param else 12
    paginator = Paginator(filteredData.qs, page_size)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {'page': page, 'filtredData': filteredData}
    return render(request, 'list_fuel_refills.html', context)

@login_required(login_url='login')
@checkAdminOrLogisticien
def deleteFuelRefillView(request, id):
    item = FuelRefill.objects.get(id=id)
    item.delete()
    cache_param = str(uuid.uuid4())
    url_path = reverse('fuel_refills')
    redirect_url = f'{url_path}?cache={cache_param}'
    return redirect(redirect_url)

@login_required(login_url='login')
@checkAdminOrLogisticien
def createFuelRefillView(request):
    form = FuelRefillForm()
    if request.method == 'POST':
        form = FuelRefillForm(request.POST)
        if form.is_valid():
            form.save()
            cache_param = str(uuid.uuid4())
            url_path = reverse('fuel_refills')
            redirect_url = f'{url_path}?cache={cache_param}'
            return redirect(redirect_url)
    context = {'form': form}
    return render(request, 'fuel_refill_form.html', context)

@login_required(login_url='login')
@checkAdminOrLogisticien
def editFuelRefillView(request, id):
    item = FuelRefill.objects.get(id=id)
    form = FuelRefillForm(instance=item)
    if request.method == 'POST':
        form = FuelRefillForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            cache_param = str(uuid.uuid4())
            url_path = reverse('fuel_refills')
            page = request.GET.get('page', '1')
            page_size = request.GET.get('page_size', '12')
            search = request.GET.get('search', '')
            redirect_url = f'{url_path}?cache={cache_param}&page={page}&page_size={page_size}&search={search}'
            return redirect(redirect_url)
    context = {'form': form, 'fuel_refill': item}
    return render(request, 'fuel_refill_form.html', context)

# Assurance Views
@login_required(login_url='login')
@checkAdminOrLogisticien
def listAssuranceView(request):
    items = Assurance.objects.all().order_by('id')
    filteredData = AssuranceFilter(request.GET, queryset=items)
    page_size_param = request.GET.get('page_size')
    page_size = int(page_size_param) if page_size_param else 12
    paginator = Paginator(filteredData.qs, page_size)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {'page': page, 'filtredData': filteredData}
    return render(request, 'list_assurances.html', context)

@login_required(login_url='login')
@checkAdminOrLogisticien
def deleteAssuranceView(request, id):
    item = Assurance.objects.get(id=id)
    item.delete()
    cache_param = str(uuid.uuid4())
    url_path = reverse('assurances')
    redirect_url = f'{url_path}?cache={cache_param}'
    return redirect(redirect_url)

@login_required(login_url='login')
@checkAdminOrLogisticien
def createAssuranceView(request):
    form = AssuranceForm()
    if request.method == 'POST':
        form = AssuranceForm(request.POST)
        if form.is_valid():
            form.save()
            cache_param = str(uuid.uuid4())
            url_path = reverse('assurances')
            redirect_url = f'{url_path}?cache={cache_param}'
            return redirect(redirect_url)
    context = {'form': form}
    return render(request, 'assurance_form.html', context)

@login_required(login_url='login')
@checkAdminOrLogisticien
def editAssuranceView(request, id):
    item = Assurance.objects.get(id=id)
    form = AssuranceForm(instance=item)
    if request.method == 'POST':
        form = AssuranceForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            cache_param = str(uuid.uuid4())
            url_path = reverse('assurances')
            page = request.GET.get('page', '1')
            page_size = request.GET.get('page_size', '12')
            search = request.GET.get('search', '')
            redirect_url = f'{url_path}?cache={cache_param}&page={page}&page_size={page_size}&search={search}'
            return redirect(redirect_url)
    context = {'form': form, 'assurance': item}
    return render(request, 'assurance_form.html', context)

# MissionCostType Views
@login_required(login_url='login')
@admin_required
def listMissionCostTypeView(request):
    types = MissionCostType.objects.all().order_by('id')
    filteredData = MissionCostTypeFilter(request.GET, queryset=types)
    page_size_param = request.GET.get('page_size')
    page_size = int(page_size_param) if page_size_param else 12
    paginator = Paginator(filteredData.qs, page_size)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {'page': page, 'filtredData': filteredData}
    return render(request, 'list_mission_cost_types.html', context)

@login_required(login_url='login')
@admin_required
def deleteMissionCostTypeView(request, id):
    item = MissionCostType.objects.get(id=id)
    item.delete()
    cache_param = str(uuid.uuid4())
    url_path = reverse('mission_cost_types')
    redirect_url = f'{url_path}?cache={cache_param}'
    return redirect(redirect_url)

@login_required(login_url='login')
@admin_required
def createMissionCostTypeView(request):
    form = MissionCostTypeForm()
    if request.method == 'POST':
        form = MissionCostTypeForm(request.POST)
        if form.is_valid():
            form.save()
            cache_param = str(uuid.uuid4())
            url_path = reverse('mission_cost_types')
            redirect_url = f'{url_path}?cache={cache_param}'
            return redirect(redirect_url)
    context = {'form': form}
    return render(request, 'mission_cost_type_form.html', context)

@login_required(login_url='login')
@admin_required
def editMissionCostTypeView(request, id):
    item = MissionCostType.objects.get(id=id)
    form = MissionCostTypeForm(instance=item)
    if request.method == 'POST':
        form = MissionCostTypeForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            cache_param = str(uuid.uuid4())
            url_path = reverse('mission_cost_types')
            page = request.GET.get('page', '1')
            page_size = request.GET.get('page_size', '12')
            search = request.GET.get('search', '')
            redirect_url = f'{url_path}?cache={cache_param}&page={page}&page_size={page_size}&search={search}'
            return redirect(redirect_url)
    context = {'form': form, 'mission_cost_type': item}
    return render(request, 'mission_cost_type_form.html', context)

# MissionCost Views
@login_required(login_url='login')
@checkAdminOrLogisticien
def listMissionCostView(request):
    items = MissionCost.objects.all().order_by('id')
    filteredData = MissionCostFilter(request.GET, queryset=items)
    page_size_param = request.GET.get('page_size')
    page_size = int(page_size_param) if page_size_param else 12
    paginator = Paginator(filteredData.qs, page_size)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {'page': page, 'filtredData': filteredData}
    return render(request, 'list_mission_costs.html', context)

@login_required(login_url='login')
@checkAdminOrLogisticien
def deleteMissionCostView(request, id):
    item = MissionCost.objects.get(id=id)
    item.delete()
    cache_param = str(uuid.uuid4())
    url_path = reverse('mission_costs')
    redirect_url = f'{url_path}?cache={cache_param}'
    return redirect(redirect_url)

@login_required(login_url='login')
@checkAdminOrLogisticien
def createMissionCostView(request):
    form = MissionCostForm()
    if request.method == 'POST':
        form = MissionCostForm(request.POST)
        if form.is_valid():
            form.save()
            cache_param = str(uuid.uuid4())
            url_path = reverse('mission_costs')
            redirect_url = f'{url_path}?cache={cache_param}'
            return redirect(redirect_url)
    context = {'form': form}
    return render(request, 'mission_cost_form.html', context)

@login_required(login_url='login')
@checkAdminOrLogisticien
def editMissionCostView(request, id):
    item = MissionCost.objects.get(id=id)
    form = MissionCostForm(instance=item)
    if request.method == 'POST':
        form = MissionCostForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            cache_param = str(uuid.uuid4())
            url_path = reverse('mission_costs')
            page = request.GET.get('page', '1')
            page_size = request.GET.get('page_size', '12')
            search = request.GET.get('search', '')
            redirect_url = f'{url_path}?cache={cache_param}&page={page}&page_size={page_size}&search={search}'
            return redirect(redirect_url)
    context = {'form': form, 'mission_cost': item}
    return render(request, 'mission_cost_form.html', context)


# MasseSalariale Views
@login_required(login_url='login')
@checkAdminOrLogisticien
def listMasseSalarialeView(request):
    items = MasseSalariale.objects.all().order_by('id')
    filteredData = MasseSalarialeFilter(request.GET, queryset=items)
    page_size_param = request.GET.get('page_size')
    page_size = int(page_size_param) if page_size_param else 12
    paginator = Paginator(filteredData.qs, page_size)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {'page': page, 'filtredData': filteredData}
    return render(request, 'list_masse_salariales.html', context)

@login_required(login_url='login')
@checkAdminOrLogisticien
def deleteMasseSalarialeView(request, id):
    item = MasseSalariale.objects.get(id=id)
    item.delete()
    cache_param = str(uuid.uuid4())
    url_path = reverse('masse_salariales')
    redirect_url = f'{url_path}?cache={cache_param}'
    return redirect(redirect_url)

@login_required(login_url='login')
@checkAdminOrLogisticien
def createMasseSalarialeView(request):
    form = MasseSalarialeForm()
    if request.method == 'POST':
        form = MasseSalarialeForm(request.POST)
        if form.is_valid():
            form.save()
            cache_param = str(uuid.uuid4())
            url_path = reverse('masse_salariales')
            redirect_url = f'{url_path}?cache={cache_param}'
            return redirect(redirect_url)
    context = {'form': form}
    return render(request, 'masse_salariale_form.html', context)

@login_required(login_url='login')
@checkAdminOrLogisticien
def editMasseSalarialeView(request, id):
    item = MasseSalariale.objects.get(id=id)
    form = MasseSalarialeForm(instance=item)
    if request.method == 'POST':
        form = MasseSalarialeForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            cache_param = str(uuid.uuid4())
            url_path = reverse('masse_salariales')
            page = request.GET.get('page', '1')
            page_size = request.GET.get('page_size', '12')
            search = request.GET.get('search', '')
            redirect_url = f'{url_path}?cache={cache_param}&page={page}&page_size={page_size}&search={search}'
            return redirect(redirect_url)
    context = {'form': form, 'masse_salariale': item}
    return render(request, 'masse_salariale_form.html', context)

# MissionCost Views

class CheckEditorMixin:
    def check_editor(self, mission_cost):
        if self.request.user.role == 'Admin':
            return True
        sites = self.request.user.sites.all()
        if mission_cost.from_emplacement in sites and self.request.user.role in ['Logisticien']:
            return True
        return False

    def dispatch(self, request, *args, **kwargs):
        mission_cost = self.get_object()  
        if not self.check_editor(mission_cost):
            return render(request, '403.html', status=403)
        return super().dispatch(request, *args, **kwargs)
    
class CheckMissionCostViewerMixin:
    def check_viewer(self, mission_cost):
        if self.request.user.role == 'Admin':
            return True
        sites = self.request.user.sites.all()
        if mission_cost.from_emplacement in sites and self.request.user.role in ['Logisticien']:
            return True
        return False

    def dispatch(self, request, *args, **kwargs):
        mission_cost = self.get_object()  
        if not self.check_viewer(mission_cost):
            return render(request, '403.html', status=403)
        return super().dispatch(request, *args, **kwargs)
    
class CheckMissionCostListViewerMixin:
    def check_viewer(self):
        if self.request.user.role in ['Admin', 'Logisticien', 'Observateur']:
            return True
        return False

    def dispatch(self, request, *args, **kwargs):
        if not self.check_viewer():
            return render(request, '403.html', status=403)
        return super().dispatch(request, *args, **kwargs)
    
class MissionCostInline():
    form_class = MissionCostForm
    model = MissionCost
    template_name = "mission_cost_form.html"    
    login_url = 'login'

    def form_valid(self, form):
        named_formsets = self.get_named_formsets()
        if not all((x.is_valid() for x in named_formsets.values())):
            return self.render_to_response(self.get_context_data(form=form))
        mission_cost = form.save(commit=False)
        
        mission_cost.save()
        new = True
        if self.object:
            new = False
        else:
            self.object = mission_cost

        for name, formset in named_formsets.items():
            formset_save_func = getattr(self, 'formset_{0}_valid'.format(name), None)
            if formset_save_func is not None:
                formset_save_func(formset)
            else:
                formset.save()

        if not new:
            cache_param = str(uuid.uuid4())
            url_path = reverse('view_mission_cost', args=[self.object.pk])
            redirect_url = f'{url_path}?cache={cache_param}'
            return redirect(redirect_url)
        return redirect('mission_costs')

    def formset_mission_cost_fees_valid(self, formset):
        mission_cost_fees = formset.save(commit=False)
        for obj in formset.deleted_objects:
            obj.delete()
        for mission_cost_fee in mission_cost_fees:
            mission_cost_fee.mission_cost = self.object
            mission_cost_fee.save()

class MissionCostCreate(LoginRequiredMixin, MissionCostInline, CreateView):

    def get_context_data(self, **kwargs):
        ctx = super(MissionCostCreate, self).get_context_data(**kwargs)
        ctx['named_formsets'] = self.get_named_formsets()
        return ctx

    def get_named_formsets(self):
        if self.request.method == "GET":
            return {'mission_cost_fees': MissionCostFeesFormSet(prefix='mission_cost_fees')}
        else:
            return {'mission_cost_fees': MissionCostFeesFormSet(self.request.POST or None, prefix='mission_cost_fees')}

class MissionCostUpdate(LoginRequiredMixin, CheckEditorMixin, MissionCostInline, UpdateView):

    def get_context_data(self, **kwargs):
        ctx = super(MissionCostUpdate, self).get_context_data(**kwargs)
        ctx['named_formsets'] = self.get_named_formsets()
        return ctx

    def get_named_formsets(self):
        return {'mission_cost_fees': MissionCostFeesFormSet(self.request.POST or None, instance=self.object, prefix='mission_cost_fees')}
    
class MissionCostDetail(LoginRequiredMixin, CheckMissionCostViewerMixin, DetailView):
    model = MissionCost
    template_name = 'mission_cost_details.html'
    context_object_name = 'mission_cost'
    login_url = 'login'

    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fields = [field for field in self.model._meta.get_fields() if field.concrete]
        context['fields'] = fields
        return context

class MissionCostList(LoginRequiredMixin, CheckMissionCostListViewerMixin, FilterView):
    model = MissionCost
    template_name = "list_mission_costs.html"
    context_object_name = "mission_costs"
    filterset_class = MissionCostFilter
    ordering = ['-mission_date', '-date_created']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        sites = self.request.user.sites.all()
        queryset = queryset.filter(from_emplacement__in=sites)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page_size_param = self.request.GET.get('page_size')
        page_size = int(page_size_param) if page_size_param else 12        
        paginator = Paginator(context['mission_costs'], page_size)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['page'] = page_obj
        return context

@login_required(login_url='login')
@checkAdminOrLogisticien
def deleteMissionCostView(request, id):
    mission_cost = MissionCost.objects.get(id=id)
    mission_cost.delete()
    cache_param = str(uuid.uuid4())
    url_path = reverse('mission_costs')
    redirect_url = f'{url_path}?cache={cache_param}'
    return redirect(redirect_url)


@login_required(login_url='login')
@checkAdminOrLogisticien
def deleteMissionCostFeeView(request, pk):
    try:
        mission_cost_fee = MissionCostFee.objects.get(id=pk)
    except MissionCostFee.DoesNotExist:
        messages.success(request, 'Mission Cost Fee Does not exit')
        url_path = reverse('edit_mission_cost', args=[mission_cost_fee.mission_cost.id])
        cache_param = str(uuid.uuid4())
        redirect_url = f'{url_path}?cache={cache_param}'
        return redirect(redirect_url)

    mission_cost_fee.delete()
    messages.success(request, 'Mission Cost Fee deleted successfully')
    url_path = reverse('edit_mission_cost', args=[mission_cost_fee.mission_cost.id])
    cache_param = str(uuid.uuid4())
    redirect_url = f'{url_path}?cache={cache_param}'
    return redirect(redirect_url)

