from django.views.generic.edit import CreateView, UpdateView
from django_filters.views import FilterView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.detail import DetailView
import uuid
from .forms import *
from .filters import *
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse
from django.core.paginator import Paginator
from django.http import JsonResponse
from functools import wraps
from .utils import *

def check_creator(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if 'id' in kwargs:
            plan_id = kwargs['id']
        elif 'pk' in kwargs:
            plan_id = kwargs['pk']
        planning = Planning.objects.get(id=plan_id)
        if planning.creator != request.user and request.user.role != 'Admin':
            return render(request, '403.html', status=403)
        return view_func(request, *args, **kwargs)
    return wrapper

def check_validator(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.role not in ['Admin', 'Logisticien']:
            return render(request, '403.html', status=403)
        return view_func(request, *args, **kwargs)
    return wrapper
    

def check_creatorPPlanned(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        pplanned_id = kwargs.get('pk')
        pplanned = PPlanned.objects.get(id=pplanned_id)
        if not ((pplanned.planning.state == 'Brouillon' and request.user == pplanned.planning.creator) or request.user.role == 'Admin'):
            return render(request, '403.html', status=403)
        return view_func(request, *args, **kwargs)
    return wrapper

# PLANNINGS

class CheckEditorMixin:
    def check_editor(self, planning):
        if self.request.user.role == 'Admin':
            return True
        if planning.creator == self.request.user and planning.state == 'Brouillon' and self.request.user.role == 'Commercial':
            return True
        if planning.state == 'Planning' and self.request.user.role == 'Logisticien':
            return True
        return False

    def dispatch(self, request, *args, **kwargs):
        planning = self.get_object()  
        if not self.check_editor(planning):
            return render(request, '403.html', status=403)
        return super().dispatch(request, *args, **kwargs)
    
class CheckPlanningViewerMixin:
    def check_viewer(self, planning):
        if self.request.user.role == 'Admin':
            return True
        sites = self.request.user.sites.all()
        if planning.site in sites and self.request.user.role in ['Observateur', 'Logisticien', 'Commercial']:
            return True
        return False

    def dispatch(self, request, *args, **kwargs):
        planning = self.get_object()  
        if not self.check_viewer(planning):
            return render(request, '403.html', status=403)
        return super().dispatch(request, *args, **kwargs)
    
class CheckPlanningListViewerMixin:
    def check_viewer(self):
        if self.request.user.role in ['Admin', 'Logisticien', 'Observateur', 'Commercial']:
            return True
        return False

    def dispatch(self, request, *args, **kwargs):
        if not self.check_viewer():
            return render(request, '403.html', status=403)
        return super().dispatch(request, *args, **kwargs)

class PlanningInline():
    form_class = PlanningCommForm
    model = Planning
    template_name = "planning_form.html"    
    login_url = 'login'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['sites'] = self.request.user.sites.all()
        return kwargs

    def form_valid(self, form):
        named_formsets = self.get_named_formsets()
        if not all((x.is_valid() for x in named_formsets.values())):
            return self.render_to_response(self.get_context_data(form=form))
        planning = form.save(commit=False)
        if not planning.state or planning.state == 'Brouillon':
            planning.state = 'Brouillon'
        
        if not planning.id:
            planning.creator = self.request.user
        
        planning.save()
        new = True
        if self.object:
            new = False
        else:
            self.object = planning

        for name, formset in named_formsets.items():
            formset_save_func = getattr(self, 'formset_{0}_valid'.format(name), None)
            if formset_save_func is not None:
                formset_save_func(formset)
            else:
                formset.save()

        if not new:
            cache_param = str(uuid.uuid4())
            url_path = reverse('view_planning', args=[self.object.pk])
            redirect_url = f'{url_path}?cache={cache_param}'
            return redirect(redirect_url)
        return redirect('plannings')

    def formset_pplanneds_valid(self, formset):
        pplanneds = formset.save(commit=False)
        for obj in formset.deleted_objects:
            obj.delete()
        for pplanned in pplanneds:
            pplanned.planning = self.object
            pplanned.save()

class PlanningCreate(LoginRequiredMixin, PlanningInline, CreateView):

    def get_context_data(self, **kwargs):
        ctx = super(PlanningCreate, self).get_context_data(**kwargs)
        ctx['named_formsets'] = self.get_named_formsets()
        return ctx

    def get_named_formsets(self):
        if self.request.method == "GET":
            return {
                'pplanneds': PPlannedsFormSet(prefix='pplanneds'),
            }
        else:
            return {
                'pplanneds': PPlannedsFormSet(self.request.POST or None, prefix='pplanneds'),
            }

class PlanningUpdate(LoginRequiredMixin, CheckEditorMixin, PlanningInline, UpdateView):

    def get_context_data(self, **kwargs):
        ctx = super(PlanningUpdate, self).get_context_data(**kwargs)
        ctx['named_formsets'] = self.get_named_formsets()
        return ctx

    def get_named_formsets(self):
        return {
            'pplanneds': PPlannedsFormSet(self.request.POST or None, instance=self.object, prefix='pplanneds'),
        }
    
class PlanningDetail(LoginRequiredMixin, CheckPlanningViewerMixin, DetailView):
    model = Planning
    template_name = 'planning_details.html'
    context_object_name = 'planning'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fields = [field for field in self.model._meta.get_fields() if field.concrete]
        context['fields'] = fields
        return context

class PlanningList(LoginRequiredMixin, CheckPlanningListViewerMixin, FilterView):
    model = Planning
    template_name = "list_plannings.html"
    context_object_name = "plannings"
    filterset_class = PlanningFilter
    ordering = ['-date_created', '-date_planning']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        sites = self.request.user.sites.all()
        queryset = queryset.filter(site__in=sites)
        return queryset   

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page_size_param = self.request.GET.get('page_size')
        page_size = int(page_size_param) if page_size_param else 12        
        paginator = Paginator(context['plannings'], page_size)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['page'] = page_obj
        return context

@login_required(login_url='login')
def completePlanning(request, id):
    planning = Planning.objects.get(id=id)
    form = PlanningLogiForm(instance=planning)
    if request.method == 'POST':
        form = PlanningLogiForm(request.POST, instance=planning)
        if form.is_valid():
            form.save()
            url_path = reverse('view_planning', args=[planning.id])
            page = request.GET.get('page', '1')
            page_size = request.GET.get('page_size', '12')
            search = request.GET.get('search', '')
            cache_param = str(uuid.uuid4())
            redirect_url = f'{url_path}?cache={cache_param}&page={page}&page_size={page_size}&search={search}'
            return redirect(redirect_url)
    context = {'form': form, 'planning': planning}

    return render(request, 'planning_complete.html', context)

@login_required(login_url='login')
@check_creator
def deletePlanningView(request, id):
    planning = Planning.objects.get(id=id)
    planning.delete()
    cache_param = str(uuid.uuid4())
    url_path = reverse('plannings')
    redirect_url = f'{url_path}?cache={cache_param}'
    return redirect(redirect_url)


@login_required(login_url='login')
@check_creatorPPlanned
def delete_product(request, pk):
    try:
        pplanned = PPlanned.objects.get(id=pk)
    except PPlanned.DoesNotExist:
        messages.success(request, 'Produit Planified Does not exit')
        url_path = reverse('edit_planning', args=[pplanned.planning.id])
        cache_param = str(uuid.uuid4())
        redirect_url = f'{url_path}?cache={cache_param}'
        return redirect(redirect_url)

    pplanned.delete()
    messages.success(request, 'Produit Planifier deleted successfully')
    url_path = reverse('edit_planning', args=[pplanned.planning.id])
    cache_param = str(uuid.uuid4())
    redirect_url = f'{url_path}?cache={cache_param}'
    return redirect(redirect_url)


@login_required(login_url='login')
@check_creator
def confirmPlanning(request, pk):
    try:
        planning = Planning.objects.get(id=pk)
    except Planning.DoesNotExist:
        messages.success(request, 'Planning Does not exit')

    if planning.state == 'Planning':
        url_path = reverse('view_planning', args=[planning.id])
        cache_param = str(uuid.uuid4())
        redirect_url = f'{url_path}?cache={cache_param}'
        return redirect(redirect_url)
    
    old_state = planning.state
    miss_reason = '/'

    planning.state = 'Planning'
    new_state = planning.state
    actor = request.user
    validation = Validation(old_state=old_state, new_state=new_state, actor=actor, miss_reason=miss_reason, planning=planning)
    planning.save()
    validation.save()
    
    messages.success(request, 'Planning plannifier avec succès')
    url_path = reverse('view_planning', args=[planning.id])
    cache_param = str(uuid.uuid4())
    redirect_url = f'{url_path}?cache={cache_param}'
    return redirect(redirect_url)

@login_required(login_url='login')
@check_creator
def cancelPlanning(request, pk):
    try:
        planning = Planning.objects.get(id=pk)
    except Planning.DoesNotExist:
        messages.success(request, 'Planning Does not exit')

    if planning.state == 'Annulé':
        url_path = reverse('view_planning', args=[planning.id])
        cache_param = str(uuid.uuid4())
        redirect_url = f'{url_path}?cache={cache_param}'
        return redirect(redirect_url)
    
    old_state = planning.state
    
    planning.state = 'Annulé'

    new_state = planning.state
    actor = request.user

    validation = Validation(old_state=old_state, new_state=new_state, actor=actor, miss_reason='/', planning=planning)
    planning.save()
    validation.save()

    messages.success(request, 'Planning annulé avec succès')
    url_path = reverse('view_planning', args=[planning.id])
    cache_param = str(uuid.uuid4())
    redirect_url = f'{url_path}?cache={cache_param}'
    return redirect(redirect_url)


@login_required(login_url='login')
@check_validator
def validatePlanning(request, pk):
    try:
        planning = Planning.objects.get(id=pk)
    except Planning.DoesNotExist:
        messages.success(request, 'Planning Does not exit')

    if planning.state == 'Planning Confirmé':
        url_path = reverse('view_planning', args=[planning.id])
        cache_param = str(uuid.uuid4())
        redirect_url = f'{url_path}?cache={cache_param}'
        return redirect(redirect_url)
    
    old_state = planning.state
    
    planning.state = 'Planning Confirmé'

    new_state = planning.state
    actor = request.user

    validation = Validation(old_state=old_state, new_state=new_state, actor=actor, miss_reason='/', planning=planning)
    planning.save()
    validation.save()

    messages.success(request, 'Planning confirmé avec succès')
    url_path = reverse('view_planning', args=[planning.id])
    cache_param = str(uuid.uuid4())
    redirect_url = f'{url_path}?cache={cache_param}'
    return redirect(redirect_url)


@login_required(login_url='login')
@check_validator
def missPlanning(request, pk):
    try:
        planning = Planning.objects.get(id=pk)
    except Planning.DoesNotExist:
        messages.success(request, 'Planning Does not exit')

    if planning.state == 'Raté':
        url_path = reverse('view_planning', args=[planning.id])
        cache_param = str(uuid.uuid4())
        redirect_url = f'{url_path}?cache={cache_param}'
        return redirect(redirect_url)
    
    old_state = planning.state
    
    planning.state = 'Raté'

    new_state = planning.state
    miss_reason = request.POST.get('miss_reason')
    actor = request.user

    validation = Validation(old_state=old_state, new_state=new_state, actor=actor, miss_reason=miss_reason, planning=planning)
    planning.save()
    validation.save()

    messages.success(request, 'Planning raté avec succès')
    url_path = reverse('view_planning', args=[planning.id])
    cache_param = str(uuid.uuid4())
    redirect_url = f'{url_path}?cache={cache_param}'
    return redirect(redirect_url)

@login_required(login_url='login')
def live_search(request):
    search_for = request.GET.get('search_for', '')
    term = request.GET.get('search_term', '')

    if search_for == 'distributeur':
        records = getDistributeurId(term)
    elif search_for == 'client':
        records = getClientId(term)

    if len(records) > 0:
        return JsonResponse([{'id': obj[0], 'name': obj[1].replace("'","\\'")} for obj in records], safe=False)
        
    return JsonResponse([], safe=False)