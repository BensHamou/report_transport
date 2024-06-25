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
import json
from django.core.mail import send_mail
from report.views import admin_required
from django.utils.html import format_html
from collections import defaultdict
from django.core.mail import EmailMessage


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

def check_marker(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.role != 'Admin' and (request.user.role != 'Logisticien' or not request.user.is_admin):
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

def checkAdminOrCommercial(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.role not in ['Admin', 'Commercial']:
            return render(request, '403.html', status=403)
        return view_func(request, *args, **kwargs)
    return wrapper

def checkAdminOrLogisticien(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.role not in ['Admin', 'Logisticien']:
            return render(request, '403.html', status=403)
        return view_func(request, *args, **kwargs)
    return wrapper

def check_return_to_draft(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.role not in ['Admin']:
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

# LIVRAISONS
@login_required(login_url='login')
@admin_required 
def listLivraisonList(request):
    livraisons = Livraison.objects.all().order_by('id')
    filteredData = LivraisonFilter(request.GET, queryset=livraisons)
    livraisons = filteredData.qs
    page_size_param = request.GET.get('page_size')
    page_size = int(page_size_param) if page_size_param else 12   
    paginator = Paginator(livraisons, page_size)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {'page': page, 'filtredData': filteredData, }
    return render(request, 'list_livraisons.html', context)

@login_required(login_url='login')
@admin_required
def deleteLivraisonView(request, id):
    livraison = Livraison.objects.get(id=id)
    livraison.delete()
    cache_param = str(uuid.uuid4())
    url_path = reverse('livraisons')

    redirect_url = f'{url_path}?cache={cache_param}'

    return redirect(redirect_url)

@login_required(login_url='login')
@admin_required
def createLivraisonView(request):
    form = LivraisonForm()
    if request.method == 'POST':
        form = LivraisonForm(request.POST)
        if form.is_valid():
            form.save()
            cache_param = str(uuid.uuid4())
            url_path = reverse('livraisons')
            page = request.GET.get('page', '1')
            page_size = request.GET.get('page_size', '12')
            search = request.GET.get('search', '')
            redirect_url = f'{url_path}?cache={cache_param}&page={page}&page_size={page_size}&search={search}'
            return redirect(redirect_url)
    context = {'form': form }
    return render(request, 'livraison_form.html', context)

@login_required(login_url='login')
@admin_required
def editLivraisonView(request, id):
    livraison = Livraison.objects.get(id=id)

    form = LivraisonForm(instance=livraison)
    if request.method == 'POST':
        form = LivraisonForm(request.POST, instance=livraison)
        if form.is_valid():
            form.save()
            cache_param = str(uuid.uuid4())
            url_path = reverse('livraisons')
            page = request.GET.get('page', '1')
            page_size = request.GET.get('page_size', '12')
            search = request.GET.get('search', '')
            redirect_url = f'{url_path}?cache={cache_param}&page={page}&page_size={page_size}&search={search}'
            return redirect(redirect_url)
    context = {'form': form, 'livraison': livraison }

    return render(request, 'livraison_form.html', context)

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
            old_state = planning.state
            planning.state = 'Planning en Attente'
            new_state = planning.state
            actor = request.user
            validation = Validation(old_state=old_state, new_state=new_state, actor=actor, miss_reason='/', planning=planning)
            planning.save()
            validation.save()
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
def finishPlanning(request, id):
    planning = Planning.objects.get(id=id)
    form = PlanningConfirmForm(instance=planning)
    if request.method == 'POST':
        form = PlanningConfirmForm(request.POST, instance=planning)
        if form.is_valid():
            form.save()
            old_state = planning.state
            planning.state = 'Planning Confirmé'
            new_state = planning.state
            actor = request.user
            validation = Validation(old_state=old_state, new_state=new_state, actor=actor, miss_reason='/', planning=planning)
            planning.save()
            sendValidationMail(planning, request.user.fullname)
            validation.save()
            url_path = reverse('view_planning', args=[planning.id])
            page = request.GET.get('page', '1')
            page_size = request.GET.get('page_size', '12')
            search = request.GET.get('search', '')
            cache_param = str(uuid.uuid4())
            redirect_url = f'{url_path}?cache={cache_param}&page={page}&page_size={page_size}&search={search}'
            return redirect(redirect_url)
    context = {'form': form, 'planning': planning}

    return render(request, 'planning_finish.html', context)

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
def deliverPlanning(request, pk):
    try:
        planning = Planning.objects.get(id=pk)
    except Planning.DoesNotExist:
        messages.success(request, 'Planning Does not exit')

    if planning.state == 'Livraison Confirmé':
        url_path = reverse('view_planning', args=[planning.id])
        cache_param = str(uuid.uuid4())
        redirect_url = f'{url_path}?cache={cache_param}'
        return redirect(redirect_url)
    
    n_bl = request.POST.get('n_bl')
    old_state = planning.state
    planning.n_bl = n_bl
    planning.state = 'Livraison Confirmé'
    new_state = planning.state
    actor = request.user
    validation = Validation(old_state=old_state, new_state=new_state, actor=actor, miss_reason='/', planning=planning)
    planning.save()
    validation.save()
    # sendValidationMail(planning, request.user.fullname)
    messages.success(request, 'Livraison confirmé avec succès')
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
@check_marker
def markPlanning(request, pk):
    try:
        planning = Planning.objects.get(id=pk)
    except Planning.DoesNotExist:
        messages.success(request, 'Planning Does not exit')

    if planning.is_marked:
        url_path = reverse('view_planning', args=[planning.id])
        cache_param = str(uuid.uuid4())
        redirect_url = f'{url_path}?cache={cache_param}'
        return redirect(redirect_url)
    
    planning.is_marked = True
    planning.save()

    messages.success(request, 'Planning visé avec succès')
    url_path = reverse('view_planning', args=[planning.id])
    cache_param = str(uuid.uuid4())
    redirect_url = f'{url_path}?cache={cache_param}'
    return redirect(redirect_url)

@login_required(login_url='login')
@check_marker
def unmarkPlanning(request, pk):
    try:
        planning = Planning.objects.get(id=pk)
    except Planning.DoesNotExist:
        messages.success(request, 'Planning Does not exit')

    if not planning.is_marked:
        url_path = reverse('view_planning', args=[planning.id])
        cache_param = str(uuid.uuid4())
        redirect_url = f'{url_path}?cache={cache_param}'
        return redirect(redirect_url)
    
    planning.is_marked = False
    planning.save()

    messages.success(request, 'Planning non visée avec succès')
    url_path = reverse('view_planning', args=[planning.id])
    cache_param = str(uuid.uuid4())
    redirect_url = f'{url_path}?cache={cache_param}'
    return redirect(redirect_url)


@login_required(login_url='login')
@check_return_to_draft
def makeDraftPlanning(request, pk):
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
    planning.state = 'Planning'
    planning.date_honored = None
    planning.chauffeur = None
    planning.immatriculation = None
    planning.fournisseur = None
    planning.tonnage = None
    new_state = planning.state
    actor = request.user
    validation = Validation(old_state=old_state, new_state=new_state, actor=actor, miss_reason='/', planning=planning)
    planning.save()
    validation.save()

    messages.success(request, 'Planning définir comme Planning avec succès')
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
        return JsonResponse([{'id': obj[0], 'name': f'''{obj[1]} - [ref: 0{obj[0]}] : ({obj[0]})'''.replace("'","\\'")} for obj in records], safe=False)
        
    return JsonResponse([], safe=False)

@login_required(login_url='login')
@checkAdminOrCommercial
def sendSelectedPlannings(request):

    data = json.loads(request.body)
    ids = data.get('ids', [])
    have_draft = Planning.objects.filter(creator=request.user, state='Brouillon').exists()
    if have_draft and ids:
        return JsonResponse({'message': 'Vous devez vous assurer de ne pas avoir de planning en brouillon avant d\'envoyer l\'émail.', 'OK': False}, safe=False)
    if ids:
        for site in request.user.sites.all():
            selected_plannings = Planning.objects.filter(id__in=ids, site=site)
            missed_plannings = Planning.objects.filter(state='Raté', site=site)
            subject = f"Planning {site.designation} du {timezone.localdate().strftime('%d/%m/%Y')}."
            message = f'''<p>Bonjour l'équipe,</p>'''
            title_missing = f'''
            <h3 style="color: red;">RAPPEL ROTATION RATÉ</h3>
            <p>Le planning a été créé par <b style="color: #002060">{request.user.fullname}</b>. Veuillez trouver ci-dessous les livraisons <b>ratées</b> du <b>{timezone.localdate().strftime('%d/%m/%Y')}</b></p>
            <ul><li><p><b>Rotation Ratés {site.designation} : {len(missed_plannings)}</b></p></li></ul>
            '''
            title_planned = f'''
            <h3 style="color: red;">PLANNING DU JOUR</h3>
            <p>Le planning a été créé par <b style="color: #002060">{request.user.fullname}</b>. Veuillez trouver ci-dessous le planning des livraisons du <b>{timezone.localdate().strftime('%d/%m/%Y')}</b></p>
            
            <ul><li><p><b>Nombres de Commandes : {len(selected_plannings)}</b></p></li></ul>
            '''
            if missed_plannings:
                message = getTable(message, missed_plannings, title_missing, True, False)
            if selected_plannings:
                message = getTable(message, selected_plannings, title_planned, False, False)

            if site.address:
                recipient_list = site.address.split('&')
            else:
                recipient_list = ['benshamou@gmail.com']
            formatHtml = format_html(message)
            if selected_plannings or missed_plannings:
                send_mail(subject, "", 'Puma Trans', recipient_list, html_message=formatHtml)
        return JsonResponse({'message': 'Les plannings ont été envoyés avec succès.', 'OK': True}, safe=False)
    else:
        missed_plannings = Planning.objects.filter(state='Raté')
        plannings_by_site = defaultdict(list)
        all_sites = Site.objects.all()
        for planning in missed_plannings:
            plannings_by_site[planning.site].append(planning)
        subject = f"Planning du {timezone.localdate().strftime('%d/%m/%Y')}."
        message = f'''<p>Bonjour l'équipe,</p>'''
        message += f'''
            <h3 style="color: red;">RAPPEL ROTATION RATÉ</h3>
            <p>Le planning a été créé par <b style="color: #002060">{request.user.fullname}</b>. Veuillez trouver ci-dessous les livraisons <b>ratées</b> du <b>{timezone.localdate().strftime('%d/%m/%Y')}</b></p>
            <ul><li><p><b>Rotation Ratés : {len(missed_plannings)}</b></p></li>'''
        recipient_list = []
        for site in all_sites:
            message += f'''<li><p><b>Rotation Ratés {site.designation} : {len(site.planning_set.all())}</b></p></li>'''
            recipient_list.append(site.address)
        message += '''</ul>'''
        for site, plannings in plannings_by_site.items():
            if planning:
                title_missing = f'''<h3 style="color: red;">ROTATION RATÉES {site.designation}</h3>'''
                message = getTable(message, plannings, title_missing, True, False)
        formatHtml = format_html(message)
        if missed_plannings:
            send_mail(subject, "", 'Puma Trans', recipient_list, html_message=formatHtml)
        return JsonResponse({'message': 'Les plannings ratés ont été envoyés avec succès.', 'OK': True}, safe=False)

@login_required(login_url='login')
@checkAdminOrLogisticien
def sendPlanningSupplier(request):
    data = json.loads(request.body)
    ids = data.get('ids', [])
    selected_plannings = Planning.objects.filter(id__in=ids, state='Planning en Attente')
    
    plannings_by_fournisseur = defaultdict(lambda: defaultdict(list))

    for planning in selected_plannings:
        plannings_by_fournisseur[planning.fournisseur][planning.site].append(planning)

    for fournisseur, sites in plannings_by_fournisseur.items():
        missed_plannings = Planning.objects.filter(state='Raté', fournisseur=fournisseur)
        subject = f"Planning PUMA du {timezone.localdate().strftime('%d/%m/%Y')}."
        message = f'''<p>Bonjour {fournisseur.designation},</p>'''
        style_th_header = ' colspan="7" style="font-size: 24px; color: white; background-color: #2a4767; border-bottom: 1px solid black; white-space: nowrap; text-align: center; padding: 0 10px;"'
        style_th = ' style="color: white; background-color: #2a4767; border-bottom: 1px solid black; white-space: nowrap; text-align: center; padding: 0 10px;"'
        style_td = ' style="border-left: 1px solid gray; border-bottom: 1px solid gray; white-space: nowrap; text-align: center; padding: 0 10px;"'
        style_td_last = ' style="border-right: 1px solid gray; border-left: 1px solid gray; border-bottom: 1px solid gray; white-space: nowrap; text-align: center; padding: 0 10px;"'
        if missed_plannings:
            message += f'''
            <h3 style="color: red;">ROTATION RATÉES</h3>'''
            table_header = f'''
            <table><thead>
                <tr><th{style_th}>N°</th><th{style_th}>SITE</th><th{style_th}>Tonnage</th><th{style_th}>Destination</th><th{style_th}>Date Planning</th>
                <th{style_th}>Livraison</th><th{style_th}>Observation</th></tr></thead><tbody>'''
            message += table_header
            for planning in missed_plannings:
                obs = planning.observation_comm if planning.observation_comm else '/'
                message += f'''<tr>
                <td{style_td}>{ planning.__str__() }</td>
                <td{style_td}>{ planning.site.designation }</td>
                <td{style_td}>{ planning.tonnage.designation }</td>
                <td{style_td}>{ planning.destination.designation }</td>
                <td{style_td}>{ planning.date_planning }</td>
                <td{style_td}>{ planning.livraison.designation }</td>
                <td{style_td_last}>{ obs }</td></tr>
                '''
            message += '</tbody></table><br><br>'

        message += f'''
        <h3 style="color: red;">PLANNING DU JOUR</h3>
        <p>Veuillez trouver ci-dessous notre besoin pour <b>{timezone.localdate().strftime('%d/%m/%Y')}</b></p>'''
        for site, plannings in sites.items():
            message += f'''<b>DEPART {str(site.designation).upper()}</b>'''
            table_header = f'''
            <table><thead><th{style_th_header}>grupopuma</th></thead>
            <thead>
                <tr><th{style_th}>N°</th><th{style_th}>SITE</th><th{style_th}>Tonnage</th><th{style_th}>Destination</th><th{style_th}>Date Planning</th>
                <th{style_th}>Livraison</th><th{style_th}>Observation</th></tr></thead><tbody>'''
            message += table_header
            for planning in plannings:
                obs = planning.observation_comm if planning.observation_comm else '/'
                message += f'''<tr>
                <td{style_td}>{ planning.__str__() }</td>
                <td{style_td}>{ planning.site.designation }</td>
                <td{style_td}>{ planning.tonnage.designation }</td>
                <td{style_td}>{ planning.destination.designation }</td>
                <td{style_td}>{ planning.date_planning }</td>
                <td{style_td}>{ planning.livraison.designation }</td>
                <td{style_td_last}>{ obs }</td></tr>
                '''
            message += '</tbody></table><br><br>'
        if fournisseur.address:
            recipient_list = fournisseur.address.split('&')
        else:
            recipient_list = ['benshamou@gmail.com']
        cc_settings = Setting.objects.filter(name='in_cc').values_list('value', flat=True)
        cc_list = list(cc_settings)
        email = EmailMessage( subject, message, 'Puma Trans', recipient_list, cc=cc_list)
        email.content_subtype = "html" 
        email.send(fail_silently=False)
    return JsonResponse({'message': 'Les plannings ratés ont été envoyés avec succès.', 'OK': True}, safe=False)


def getTable(msg, plannings, title, addDate, addSupp):
    old_message = msg
    style_th = ' style="color: white; background-color: #002060; border-bottom: 1px solid black; white-space: nowrap; text-align: center; padding: 0 10px;"'
    style_td = ' style="border-left: 1px solid gray; border-bottom: 1px solid gray; white-space: nowrap; text-align: center; padding: 0 10px;"'
    style_td_last = ' style="border-right: 1px solid gray; border-left: 1px solid gray; border-bottom: 1px solid gray; white-space: nowrap; text-align: center; padding: 0 10px;"'
    date_column = f'<th{style_th}>Date Planning</th>' if addDate else ''
    supp_column = f'<th{style_th}>Date Honorée</th>' if addSupp else ''
    
    table_header = f'''
    <table><thead>
        <tr><th{style_th}>N°</th><th{style_th}>SITE</th><th{style_th}>Distributeur</th><th{style_th}>Client</th><th{style_th}>Produit</th>
        <th{style_th}>Palette</th><th{style_th}>Tonnage</th><th{style_th}>Destination</th>{date_column}{supp_column}<th{style_th}>Livraison</th><th{style_th}>Observation</th></tr></thead><tbody>'''
    old_message += title
    for planning in plannings:
        obs = planning.observation_comm if planning.observation_comm else '/'
        old_message += table_header
        rowspan = len(planning.pplanneds())
        date_row = f'<td{style_td} rowspan="{rowspan}">{ planning.date_planning }</td>' if addDate else ''
        supp_row = f'<td{style_td} rowspan="{rowspan}">{ planning.date_honored }</td>' if addSupp else ''
        has_printed = False
        for product in planning.pplanneds():
            if not has_printed:
                old_message += f'''<tr>
                <td{style_td} rowspan="{rowspan}">{ planning.__str__() }</td>
                <td{style_td} rowspan="{rowspan}">{ planning.site.designation }</td>
                <td{style_td} rowspan="{rowspan}">{ planning.distributeur }</td>
                <td{style_td} rowspan="{rowspan}">{ planning.client }</td>
                <td{style_td}>{ product.product.designation }</td>
                <td{style_td}>{ int(product.palette) } palettes</td>
                <td{style_td} rowspan="{rowspan}">{ planning.tonnage.designation }</td>
                <td{style_td} rowspan="{rowspan}">{ planning.destination.designation }</td>
                {date_row}
                {supp_row}
                <td{style_td} rowspan="{rowspan}">{ planning.livraison.designation }</td>
                <td{style_td_last} rowspan="{rowspan}">{ obs }</td></tr>
                '''
                has_printed = True
            else:
                old_message += f'''<tr>
                <td{style_td}>{ product.product.designation }</td>
                <td{style_td}>{ int(product.palette) } palettes</td></tr>'''
        old_message += '</tbody></table><br><br>'
    return old_message

def sendValidationMail(planning, user):
    subject = f"Livraison de planning N° {planning} ({timezone.localdate().strftime('%d/%m/%Y')})."
    message = f'''<p>Bonjour l'équipe,</p>'''
    message += f'''
        <p>Le planning a été confirmé par <b style="color: #002060">{user}</b>. Veuillez trouver ci-dessous les livraisons <b>Confirmer</b> du <b>{timezone.localdate().strftime('%d/%m/%Y')}</b></p>'''
    
    price = Price.objects.get(depart=planning.site, destination=planning.destination, fournisseur=planning.fournisseur, tonnage=planning.tonnage)
    prices = Price.objects.filter(depart=planning.site, destination=planning.destination, tonnage=planning.tonnage).exclude(pk=price.pk).order_by('price')

    style_th = ' style="color: white; background-color: #002060; border-bottom: 1px solid black; white-space: nowrap; text-align: center; padding: 0 10px;"'
    style_td = ' style="border-left: 1px solid gray; border-bottom: 1px solid gray; white-space: nowrap; text-align: center; padding: 0 10px;"'
    style_td_price = ' style="border-left: 1px solid gray; border-bottom: 1px solid gray; white-space: nowrap; color: green; font-weight: bold; text-align: center; padding: 0 10px;"'

    min_prices = min(len(prices), 4)
    prices = prices[:min_prices]
    prices_header = ''
    for p in prices:
        prices_header += f'<th{style_th}>{p.fournisseur.designation}</th>'
    table_header = f'''
    <table><thead><th></th><th></th><th></th><th></th><th></th><th></th><th></th><th></th><th></th><th></th><th></th><th></th><th></th><th></th>
    <th colspan="{min_prices}" style='border: 1px solid gray; white-space: nowrap; color: green; font-weight: bold;'>{price.price:,.2f} DA</th></thead><thead><tr><th{style_th}>N°</th><th{style_th}>SITE</th><th{style_th}>Distributeur</th><th{style_th}>Client</th>
    <th{style_th}>Produit</th><th{style_th}>Palette</th><th{style_th}>Tonnage</th><th{style_th}>Destination</th><th{style_th}>Livraison</th>
    <th{style_th}>Observation</th><th{style_th}>Fournisseur</th><th{style_th}>Chauffeur</th><th{style_th}>Immatrucilation</th><th{style_th}>N° BL</th>{prices_header}
    </tr></thead><tbody>'''
    message += table_header
    obs = planning.observation_comm if planning.observation_comm else '/'
    rowspan = len(planning.pplanneds())
    has_printed = False
    for product in planning.pplanneds():
        if not has_printed:
            message += f'''<tr style='border-left: 1px solid gray; white-space: nowrap;'>
            <td{style_td} rowspan="{rowspan}">{ planning.__str__() }</td>
            <td{style_td} rowspan="{rowspan}">{ planning.site.designation }</td>
            <td{style_td} rowspan="{rowspan}">{ planning.distributeur }</td>
            <td{style_td} rowspan="{rowspan}">{ planning.client }</td>
            <td{style_td}>{ product.product.designation }</td>
            <td{style_td}>{ int(product.palette) } palettes</td>
            <td{style_td} rowspan="{rowspan}">{ planning.tonnage.designation }</td>
            <td{style_td} rowspan="{rowspan}">{ planning.destination.designation }</td>
            <td{style_td} rowspan="{rowspan}">{ planning.livraison.designation }</td>
            <td{style_td} rowspan="{rowspan}">{ obs }</td>
            <td{style_td} rowspan="{rowspan}">{ planning.fournisseur }</td>
            <td{style_td} rowspan="{rowspan}">{ planning.chauffeur }</td>
            <td{style_td} rowspan="{rowspan}">{ planning.immatriculation }</td>
            <td{style_td} rowspan="{rowspan}">{ planning.n_bl }</td>
            '''
            for p in prices:
                message += f'<th{style_td_price} rowspan="{rowspan}">{p.price:,.2f} DA</th>'
            has_printed = True
        else:
            message += f'''<tr>
            <td{style_td}>{ product.product.designation }</td>
            <td{style_td}>{ int(product.palette) } palettes</td>'''
        message += '</tr>'
    message += '</tbody></table><br><br>'
    if planning.site.address:
        recipient_list = planning.site.address.split('&')
    else:
        recipient_list = ['benshamou@gmail.com']
    formatHtml = format_html(message)
    send_mail(subject, "", 'Puma Trans', recipient_list, html_message=formatHtml)