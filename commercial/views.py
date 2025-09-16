from django.views.generic.edit import CreateView, UpdateView
from django_filters.views import FilterView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.detail import DetailView
from django.views.generic import ListView
from django.db.models.functions import ExtractYear, ExtractMonth
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
from django.db.models import Q
from report.models import Report, PTransported, Price
from datetime import datetime
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.utils.translation import gettext_lazy as _
from django_filters.views import FilterView
from django.db.models import Exists, OuterRef

FRENCH_MONTHS = {
    1: _("janvier"),
    2: _("février"),
    3: _("mars"), 
    4: _("avril"),
    5: _("mai"),
    6: _("juin"),
    7: _("juillet"),
    8: _("août"),
    9: _("septembre"),
    10: _("octobre"),
    11: _("novembre"),
    12: _("décembre")
}


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
        if request.user.role not in ['Admin', 'Logisticien', 'Commercial']:
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

# BLOCKED
@login_required(login_url='login')
@admin_required 
def blockedList(request):
    blockeds = Blocked.objects.all().order_by('-date_modified')
    filteredData = BlockedFilter(request.GET, queryset=blockeds)
    blockeds = filteredData.qs
    page_size_param = request.GET.get('page_size')
    page_size = int(page_size_param) if page_size_param else 12   
    paginator = Paginator(blockeds, page_size)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {'page': page, 'filtredData': filteredData, }
    return render(request, 'list_blockeds.html', context)

@login_required(login_url='login')
@admin_required
def removeBlockedView(request, id):
    blocked = Blocked.objects.get(id=id)
    blocked.delete()
    plannings = Planning.objects.filter(Q(state='Planning Bloqué') & Q(distributeur_id=blocked.distributeur_id))
    for planning in plannings:
        old_state = planning.state
        planning.state = 'Planning'
        planning.date_modified = timezone.now()
        new_state = planning.state
        actor = request.user
        validation = Validation(old_state=old_state, new_state=new_state, actor=actor, miss_reason='Distributeur Débloqué', planning=planning)
        planning.save()
        validation.save()

    cache_param = str(uuid.uuid4())
    url_path = reverse('blockeds')

    redirect_url = f'{url_path}?cache={cache_param}'

    return redirect(redirect_url)

@login_required(login_url='login')
@admin_required
def addBlockedView(request):
    form = BlockedForm()
    if request.method == 'POST':
        form = BlockedForm(request.POST)
        if form.is_valid():
            blocked = form.save(commit=False)
            blocked.creator = request.user
            blocked.save()
            for planning in Planning.objects.filter((Q(state='Planning') | Q(state='Raté')) & Q(distributeur_id=blocked.distributeur_id)):
                old_state = planning.state
                planning.state = 'Planning Bloqué'
                planning.date_modified = timezone.now()
                new_state = planning.state
                actor = request.user
                validation = Validation(old_state=old_state, new_state=new_state, actor=actor, miss_reason='Distributeur Bloqué', planning=planning)
                planning.save()
                validation.save()
            cache_param = str(uuid.uuid4())
            url_path = reverse('blockeds')
            page = request.GET.get('page', '1')
            page_size = request.GET.get('page_size', '12')
            search = request.GET.get('search', '')
            redirect_url = f'{url_path}?cache={cache_param}&page={page}&page_size={page_size}&search={search}'
            return redirect(redirect_url)
    context = {'form': form }
    return render(request, 'blocked_form.html', context)

@login_required(login_url='login')
@admin_required
def sendBlockList(reqest):
    blockeds = Blocked.objects.all()
    if not blockeds:
        return JsonResponse({'message': 'Assurez-vous d\'avoir au moins une planification bloqué.', 'OK': False}, safe=False)
    
    style_th = ' style="color: white; background-color: #002060; border: 1px solid black; white-space: nowrap; text-align: center; padding: 0 20px;"'
    style_td = ' style="border-left: 1px solid black; border-right: 1px solid black; border-bottom: 1px solid black; white-space: nowrap; text-align: center; padding: 0 20px;"'
    
    subject = f"Liste bloquer du ({timezone.localdate().strftime('%d/%m/%Y')})."
    message = f'''<p>Bonjour l'équipe,</p>
    <h4 style="color: red;">LISTE BLOQUER</h4>
    La liste bloquer a été à jour par <b style="color: #002060;">{reqest.user.fullname}</b> le <b style="color: #002060;">{timezone.localdate().strftime('%d/%m/%Y')}</b> :
    <ul><li><b>Total des clients bloquer : {len(blockeds)}</b></li></ul>
     <table><thead><th{style_th}>Distributeur bloquer</th></thead><tbody>'''
    
    for blocked in blockeds:
        message += f'''<tr style='border-left: 1px solid gray; white-space: nowrap;'>
                        <td{style_td}>{ blocked.distributeur }</td></td>'''
    message += '</tbody></table><br><br>Coridalement;'
    recipient_list = []
    for site in Site.objects.all():
        recipient_list.append(site.address)
    if not recipient_list:
        recipient_list = ['mohammed.senoussaoui@grupopuma-dz.com']
    formatHtml = format_html(message)
    send_mail(subject, "", 'Puma Trans', recipient_list, html_message=formatHtml)
    return JsonResponse({'message': 'Les distibuteurs bloqués ont été envoyés avec succès.', 'OK': True}, safe=False)

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
        url_path = reverse('view_planning', args=[self.object.pk]) if not new else reverse('plannings')
        return redirect(getRedirectionURL(self.request, url_path))
        
    def formset_pplanneds_valid(self, formset):
        pplanneds = formset.save(commit=False)
        for obj in formset.deleted_objects:
            obj.delete()
        for pplanned in pplanneds:
            pplanned.planning = self.object
            pplanned.save()
            
    def formset_files_valid(self, formset):
        files = formset.save(commit=False)
        for obj in formset.deleted_objects:
            obj.delete()
        for file in files:
            file.planning = self.object
            file.save()

class PlanningCreate(LoginRequiredMixin, PlanningInline, CreateView):

    def get_context_data(self, **kwargs):
        ctx = super(PlanningCreate, self).get_context_data(**kwargs)
        ctx['named_formsets'] = self.get_named_formsets()
        return ctx

    def get_named_formsets(self):
        if self.request.method == "GET":
            return {'pplanneds': PPlannedsFormSet(prefix='pplanneds')}
        else:
            return {'pplanneds': PPlannedsFormSet(self.request.POST or None, prefix='pplanneds')}

class PlanningUpdate(LoginRequiredMixin, CheckEditorMixin, PlanningInline, UpdateView):

    def get_context_data(self, **kwargs):
        ctx = super(PlanningUpdate, self).get_context_data(**kwargs)
        ctx['named_formsets'] = self.get_named_formsets()
        return ctx

    def get_named_formsets(self):
        return {
            'pplanneds': PPlannedsFormSet(self.request.POST or None, instance=self.object, prefix='pplanneds'),
            'files': FileFormSet(self.request.POST or None, self.request.FILES or None, instance=self.object, prefix='files')
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
    ordering = ['-date_modified', '-date_planning']
    
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
            return redirect(getRedirectionURL(request, url_path))
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
            # sendValidationMail(planning, request.user.fullname)
            validation.save()
            url_path = reverse('view_planning', args=[planning.id])
            return redirect(getRedirectionURL(request, url_path))
    context = {'form': form, 'planning': planning}

    return render(request, 'planning_finish.html', context)

@login_required(login_url='login')
@check_creator
def deletePlanningView(request, id):
    planning = Planning.objects.get(id=id)
    planning.delete()
    url_path = reverse('plannings')
    return redirect(getRedirectionURL(request, url_path))


@login_required(login_url='login')
@check_creatorPPlanned
def delete_product(request, pk):
    try:
        pplanned = PPlanned.objects.get(id=pk)
    except PPlanned.DoesNotExist:
        messages.success(request, 'Produit Planified Does not exit')
        url_path = reverse('edit_planning', args=[pplanned.planning.id])
        return redirect(getRedirectionURL(request, url_path))
        
    pplanned.delete()
    messages.success(request, 'Produit Planifier deleted successfully')
    url_path = reverse('edit_planning', args=[pplanned.planning.id])
    return redirect(getRedirectionURL(request, url_path))


@login_required(login_url='login')
@check_creator
def confirmPlanning(request, pk):
    try:
        planning = Planning.objects.get(id=pk)
    except Planning.DoesNotExist:
        messages.success(request, 'Planning Does not exit')

    url_path = reverse('view_planning', args=[planning.id])
    if planning.state in ['Planning', 'Planning Bloqué']:
        return redirect(getRedirectionURL(request, url_path))
        
    old_state = planning.state
    miss_reason = '/'
    if Blocked.objects.filter(Q(distributeur_id=planning.distributeur_id)).exists():
        planning.state = 'Planning Bloqué'
    else:
        planning.state = 'Planning'
    new_state = planning.state
    actor = request.user
    validation = Validation(old_state=old_state, new_state=new_state, actor=actor, miss_reason=miss_reason, planning=planning)
    planning.save()
    validation.save()
    
    messages.success(request, 'Planning plannifier avec succès')
    url_path = reverse('view_planning', args=[planning.id])
    return redirect(getRedirectionURL(request, url_path))

@login_required(login_url='login')
@check_creator
def cancelPlanning(request, pk):
    try:
        planning = Planning.objects.get(id=pk)
    except Planning.DoesNotExist:
        messages.success(request, 'Planning Does not exit')

    url_path = reverse('view_planning', args=[planning.id])
    if planning.state == 'Annulé':
        return redirect(getRedirectionURL(request, url_path))
    
    old_state = planning.state
    
    planning.state = 'Annulé'

    new_state = planning.state
    actor = request.user

    validation = Validation(old_state=old_state, new_state=new_state, actor=actor, miss_reason='/', planning=planning)
    planning.save()
    validation.save()

    messages.success(request, 'Planning annulé avec succès')
    url_path = reverse('view_planning', args=[planning.id])
    return redirect(getRedirectionURL(request, url_path))


@login_required(login_url='login')
@check_validator
def validatePlanning(request, pk):
    try:
        planning = Planning.objects.get(id=pk)
    except Planning.DoesNotExist:
        messages.success(request, 'Planning Does not exit')

    url_path = reverse('view_planning', args=[planning.id])
    if planning.state == 'Planning Confirmé':
        return redirect(getRedirectionURL(request, url_path))
    
    old_state = planning.state
    
    planning.state = 'Planning Confirmé'

    new_state = planning.state
    actor = request.user

    validation = Validation(old_state=old_state, new_state=new_state, actor=actor, miss_reason='/', planning=planning)
    planning.save()
    validation.save()

    messages.success(request, 'Planning confirmé avec succès')
    url_path = reverse('view_planning', args=[planning.id])
    return redirect(getRedirectionURL(request, url_path))

@login_required(login_url='login')
@check_validator
def deliverPlanning(request, pk):
    try:
        planning = Planning.objects.get(id=pk)
    except Planning.DoesNotExist:
        messages.success(request, 'Planning Does not exit')

    url_path = reverse('view_planning', args=[planning.id])
    if planning.state == 'Livraison Confirmé':
        return JsonResponse({'status': True, 'message': 'Livraison confirmé avec succès', 'redirect': getRedirectionURL(request, url_path)})
    
    n_bl = request.POST.get('n_bl', None)

    # if n_bl and planning.fournisseur.send_email:
    #     try:
    #         n_bl_numeric = int(n_bl)
    #         current_year = planning.date_honored.year
            
    #         higher_bl_exists = Planning.objects.filter(fournisseur=planning.fournisseur, site=planning.site, state='Livraison Confirmé', date_honored__year=current_year, n_bl__gte=n_bl_numeric).exists()
            
    #         if higher_bl_exists:
    #             return JsonResponse({'status': False, 
    #                 'message': f'Il existe déjà des BL avec numéro égal ou supérieur à {n_bl} pour cette année. Veuillez utiliser un numéro séquentiel.'
    #             }, status=200)
    #     except ValueError:
    #         return JsonResponse({'status': False, 'message': 'Le numéro BL doit être un nombre entier.'}, status=200)
        
    if n_bl and planning.fournisseur.send_email:
        try:
            n_bl_numeric = int(n_bl)
            current_year = planning.date_honored.year
            
            previous_report = Report.objects.filter(prix__fournisseur=planning.fournisseur, prix__depart=planning.site, 
                                                    n_bl__lt=n_bl_numeric, date_dep__year=current_year, state='Confirmé').order_by('-n_bl').first()
            
            
            if previous_report:
                previous_planning_exists = Planning.objects.filter(fournisseur=planning.fournisseur, site=planning.site, 
                                                                   state='Livraison Confirmé', n_bl=previous_report.n_bl).exists()
                
                if not previous_planning_exists:
                    return JsonResponse({'status': False, 'message': 
                                         f'Le BL précédent {previous_report.n_bl} n\'a pas de planning associé. Veuillez vérifier.'}, status=200)
            
        except ValueError:
            return JsonResponse({'status': False, 'message': 'Le numéro BL doit être un nombre entier.'}, status=200)
    
        
    # create_rotation = request.POST.get('create_rotation')
    create_rotation = True
    if create_rotation:
        prix = Price.objects.filter(
            depart=planning.site,
            destination=planning.destination,
            fournisseur=planning.fournisseur,
            tonnage=planning.tonnage,
            date_from__lte=planning.date_planning_final,
        ).filter(Q(date_to__gte=planning.date_planning_final) | Q(date_to__isnull=True)).last()
        report = Report(creator=request.user, site=planning.site, state='Brouillon', prix=prix, date_dep=planning.date_honored, 
                        chauffeur=planning.str_chauffeur, immatriculation=planning.str_immatriculation, n_bl=n_bl, observation=planning.observation_logi,
                        n_btr=None, n_bl_2=None)
        report.save()
        for pplanned in planning.pplanned_set.all():
            ptransported = PTransported(report=report, product=pplanned.product, qte_transported=0, observation=None)
            ptransported.save()
        planning.report = report

    old_state = planning.state
    planning.n_bl = n_bl
    planning.code = Planning.generate_unique_code()
    planning.state = 'Livraison Confirmé'
    new_state = planning.state
    actor = request.user
    validation = Validation(old_state=old_state, new_state=new_state, actor=actor, miss_reason='/', planning=planning)
    planning.save()
    validation.save()
    # sendValidationMail(planning, request.user.fullname)
    messages.success(request, 'Livraison confirmé avec succès')
    url_path = reverse('view_planning', args=[planning.id])
    return JsonResponse({'status': True, 'message': 'Livraison confirmé avec succès', 'redirect': getRedirectionURL(request, url_path)})

@login_required(login_url='login')
@check_validator
def missPlanning(request, pk):
    try:
        planning = Planning.objects.get(id=pk)
    except Planning.DoesNotExist:
        messages.success(request, 'Planning Does not exit')

    url_path = reverse('view_planning', args=[planning.id])
    if planning.state == 'Raté':
        return redirect(getRedirectionURL(request, url_path))
    
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
    return redirect(getRedirectionURL(request, url_path))

@login_required(login_url='login')
@check_marker
def markPlanning(request, pk):
    try:
        planning = Planning.objects.get(id=pk)
    except Planning.DoesNotExist:
        messages.success(request, 'Planning Does not exit')

    url_path = reverse('view_planning', args=[planning.id])
    if planning.is_marked:
        return redirect(getRedirectionURL(request, url_path))
    
    planning.is_marked = True
    planning.code = None
    planning.save()

    messages.success(request, 'Planning visé avec succès')
    url_path = reverse('view_planning', args=[planning.id])
    return redirect(getRedirectionURL(request, url_path))

@login_required(login_url='login')
@check_marker
def unmarkPlanning(request, pk):
    try:
        planning = Planning.objects.get(id=pk)
    except Planning.DoesNotExist:
        messages.success(request, 'Planning Does not exit')

    url_path = reverse('view_planning', args=[planning.id])
    if not planning.is_marked:
        return redirect(getRedirectionURL(request, url_path))
    
    planning.is_marked = False
    planning.code = Planning.generate_unique_code()
    planning.save()

    messages.success(request, 'Planning non visée avec succès')
    return redirect(getRedirectionURL(request, url_path))

@login_required(login_url='login')
@checkAdminOrLogisticien
def reschedulePlanning(request, pk):
    try:
        planning = Planning.objects.get(id=pk)
    except Planning.DoesNotExist:
        messages.success(request, 'Planning Does not exit')

    url_path = reverse('view_planning', args=[planning.id])
    if planning.state == 'Planning':
        return redirect(getRedirectionURL(request, url_path))
    
    reschedule_date = request.POST.get('reschedule_date')
    old_state = planning.state
    planning.date_replanning = reschedule_date 
    planning.state = 'Planning'
    planning.date_honored = None
    planning.chauffeur = None
    planning.immatriculation = None
    planning.driver = None
    planning.vehicle = None
    planning.fournisseur = None
    planning.tonnage = None
    planning.supplier_informed = False
    new_state = planning.state
    actor = request.user
    validation = Validation(old_state=old_state, new_state=new_state, actor=actor, miss_reason='/', planning=planning)
    planning.save()
    validation.save()
    messages.success(request, 'Planning définir comme Planning avec succès')
    return redirect(getRedirectionURL(request, url_path))

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
    
    selected_plannings = Planning.objects.filter(id__in=ids, state='Planning')
    date_planning_final = selected_plannings[0].date_planning_final
    plannings_by_site = defaultdict(list)
    for planning in selected_plannings:
        plannings_by_site[planning.site].append(planning)

    for site, plannings in plannings_by_site.items():
            missed_plannings = Planning.objects.filter(state='Raté', site=site)
            today_date = timezone.localdate().strftime('%d/%m/%Y')
            subject = f"Planning {site.designation} du {today_date}."
            message = f'''<p>Bonjour l'équipe,</p>'''
            title_missing = f'''
            <h3 style="color: red;">RAPPEL ROTATION RATÉ</h3>
            <p>Le planning a été créé par <b style="color: #002060">{request.user.fullname}</b>. Veuillez trouver ci-dessous les livraisons <b>ratées</b> du <b>{today_date}</b></p>
            <ul><li><p><b>Rotation Ratés {site.designation} : {len(missed_plannings)}</b></p></li></ul>
            '''
            title_planned = f'''
            <h3 style="color: red;">PLANNING DU JOUR</h3>
            <p>Le planning a été créé par <b style="color: #002060">{request.user.fullname}</b>. Veuillez trouver ci-dessous le planning des livraisons du <b>{date_planning_final}</b></p>
            
            <ul><li><p><b>Nombres de Commandes : {len(plannings)}</b></p></li></ul>
            '''
            if missed_plannings:
                message = getTable(message, missed_plannings, title_missing, True, False)
            if plannings:
                message = getTable(message, plannings, title_planned, False, False)

            if site.address:
                recipient_list = site.address.split('&')
            else:
                recipient_list = ['mohammed.senoussaoui@grupopuma-dz.com']
            formatHtml = format_html(message)
            if plannings or missed_plannings:
                send_mail(subject, "", 'Puma Trans', recipient_list, html_message=formatHtml)
    return JsonResponse({'message': 'Les plannings ont été envoyés avec succès.', 'OK': True}, safe=False)


@login_required(login_url='login')
@checkAdminOrCommercial
def sendMissedPlannings(request):
    missed_plannings = Planning.objects.filter(state='Raté')
    today_date = timezone.localdate().strftime('%d/%m/%Y')
    plannings_by_site = defaultdict(list)
    all_sites = Site.objects.all()

    for planning in missed_plannings:
        plannings_by_site[planning.site].append(planning)

    subject = f"Planning du {today_date}."
    message = f'''<p>Bonjour l'équipe,</p>'''
    message += f'''
        <h3 style="color: red;">RAPPEL ROTATION RATÉ</h3>
        <p>Le planning a été créé par <b style="color: #002060">{request.user.fullname}</b>. Veuillez trouver ci-dessous les livraisons <b>ratées</b> du <b>{today_date}</b></p>
        <ul><li><p><b>Rotation Ratés : {len(missed_plannings)}</b></p></li>'''
    
    recipient_list = []

    for site in all_sites:
        message += f'''<li><p><b>Rotation Ratés {site.designation} : {len(site.planning_set.filter(state='Raté'))}</b></p></li>'''
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
    selected_plannings = Planning.objects.filter(id__in=ids, state='Planning en Attente', supplier_informed=False)
    date_honored = selected_plannings[0].date_honored
    
    plannings_by_fournisseur = defaultdict(lambda: defaultdict(list))

    for planning in selected_plannings:
        plannings_by_fournisseur[planning.fournisseur][planning.site].append(planning)

    for fournisseur, sites in plannings_by_fournisseur.items():
        subject = f"Planning PUMA du {timezone.localdate().strftime('%d/%m/%Y')}."
        message = f'''<p>Bonjour {fournisseur.designation},</p>'''
        style_th_header = ' colspan="7" style="font-size: 24px; color: white; background-color: #2a4767; border-bottom: 1px solid black; white-space: nowrap; text-align: center; padding: 0 10px;"'
        style_th = ' style="color: white; background-color: #2a4767; border-bottom: 1px solid black; white-space: nowrap; text-align: center; padding: 0 10px;"'
        style_td = ' style="border-left: 1px solid gray; border-bottom: 1px solid gray; white-space: nowrap; text-align: center; padding: 0 10px;"'
        style_td_last = ' style="border-right: 1px solid gray; border-left: 1px solid gray; border-bottom: 1px solid gray; white-space: nowrap; text-align: center; padding: 0 10px;"'
        message += f'''
        <h3 style="color: red;">PLANNING DU JOUR</h3>
        <p>Veuillez trouver ci-dessous notre besoin pour <b>{date_honored}</b></p>'''
        for site, plannings in sites.items():
            message += f'''<b>DEPART {site.designation.upper()} : {len(plannings)}</b>'''
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
                <td{style_td}>{ planning.date_planning_final }</td>
                <td{style_td}>{ planning.livraison.designation }</td>
                <td{style_td_last}>{ obs }</td></tr>
                '''
            message += '</tbody></table><br><br>'

        if fournisseur.address:
            recipient_list = fournisseur.address.split('&')
        else:
            recipient_list = ['mohammed.senoussaoui@grupopuma-dz.com']

        cc_settings = Setting.objects.filter(name='in_cc').values_list('value', flat=True)
        cc_list = list(cc_settings)
        email = EmailMessage( subject, message, 'Puma Trans', recipient_list, cc=cc_list)
        email.content_subtype = "html" 
        email.send(fail_silently=False)
        selected_plannings.update(supplier_informed=True)
    return JsonResponse({'message': 'Les fournisseurs ont été notifiés avec succès.', 'OK': True}, safe=False)

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
        tonnage = planning.tonnage.designation if planning.tonnage else '/'
        old_message += table_header
        rowspan = len(planning.pplanneds())
        date_row = f'<td{style_td} rowspan="{rowspan}">{ planning.date_planning_final }</td>' if addDate else ''
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
                <td{style_td} rowspan="{rowspan}">{ tonnage }</td>
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

@login_required(login_url='login')
@checkAdminOrLogisticien
def sendValidationMail(request):
    plannings = Planning.objects.filter(state = 'Planning Confirmé', site__in=request.user.sites.all())
    if not plannings:
        return JsonResponse({'message': 'Assurez-vous d\'avoir au moins une planification confirmée.', 'OK': False}, safe=False)
    
    
    subject = f"Livraison de plannings ({timezone.localdate().strftime('%d/%m/%Y')})."
    
    style_th = ' style="color: white; background-color: #002060; border-bottom: 1px solid black; white-space: nowrap; text-align: center; padding: 0 10px;"'
    style_td = ' style="border-left: 1px solid gray; border-bottom: 1px solid gray; white-space: nowrap; text-align: center; padding: 0 10px;"'
    style_td_price = ' style="border-left: 1px solid gray; border-bottom: 1px solid gray; white-space: nowrap; color: green; font-weight: bold; text-align: center; padding: 0 10px;"'

    plannings_by_site = defaultdict(list)
    for planning in plannings:
        plannings_by_site[planning.site].append(planning)
    
    recipient_list = []
    for site, planningss in plannings_by_site.items():
        date_planning_final = planningss[0].date_planning_final
        message = f'''<p>Bonjour l'équipe,</p>'''
        message += f'''
            <p>Veuillez trouver ci-dessous les plannings <b>Confirmer</b> par <b style="color: #002060">{request.user.fullname}</b> du <b>{date_planning_final}</b></p>'''
        recipient_list = site.address.split('&')
        message += f'''<b>SITE {site.designation.upper()} : {len(planningss)}</b>'''
        for planning in planningss:
            date_planning_final = planning.date_planning_final
            price = Price.objects.filter(
                depart=planning.site,
                destination=planning.destination,
                fournisseur=planning.fournisseur,
                tonnage=planning.tonnage,
                date_from__lte=date_planning_final,
            ).filter(Q(date_to__gte=date_planning_final) | Q(date_to__isnull=True)).last()
            prices = Price.objects.filter(depart=planning.site, destination=planning.destination, tonnage=planning.tonnage, date_from__lte=date_planning_final).filter(Q(date_to__gte=date_planning_final) | Q(date_to__isnull=True)).exclude(pk=price.pk).order_by('price')
            min_prices = min(len(prices), 4)
            prices = prices[:min_prices]
            prices_header = ''
            for p in prices:
                prices_header += f'<th{style_th}>{p.fournisseur.designation}</th>'
            table_header = f'''
            <table><thead><th></th><th></th><th></th><th></th><th></th><th></th><th></th><th></th><th></th><th></th><th></th><th></th><th></th><th></th>
            <th colspan="{min_prices}" style='border: 1px solid gray; white-space: nowrap; color: green; font-weight: bold;'>Prix accordé : {price.price:,.2f} DA</th></thead><thead><tr><th{style_th}>N°</th><th{style_th}>SITE</th><th{style_th}>Distributeur</th><th{style_th}>Client</th>
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
                    <td{style_td} rowspan="{rowspan}">{ planning.str_chauffeur }</td>
                    <td{style_td} rowspan="{rowspan}">{ planning.str_immatriculation }</td>
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

        if not recipient_list:
            recipient_list = ['mohammed.senoussaoui@grupopuma-dz.com']
        formatHtml = format_html(message)
        send_mail(subject, "", 'Puma Trans', recipient_list, html_message=formatHtml)
    return JsonResponse({'message': 'Les plannings confirmés ont été envoyés avec succès.', 'OK': True}, safe=False)

@login_required(login_url='login')
@checkAdminOrLogisticien
def changePlanningDates(request):
    data = json.loads(request.body)
    ids = data.get('ids', [])
    new_date_str = data.get('new_date')
    new_date = datetime.strptime(new_date_str, '%Y-%m-%d').date()
    selected_plannings = Planning.objects.filter(id__in=ids).exclude(state='Livraison Confirmé')

    selected_plannings.update(date_replanning=new_date)

    return JsonResponse({'message': f'{selected_plannings.count()} plannings ont été mis à jour avec succès.', 'OK': True}, safe=False)


class ArchivedPlanningListView(FilterView, ListView):
    model = Planning
    template_name = 'archived_list.html'
    context_object_name = 'archived_plannings'
    filterset_class = ArchivedPlanningFilter
    
    def get_queryset(self):
        return (
            super().get_queryset().filter(state='Livraison Confirmé', is_marked=True)
            .annotate(has_files=Exists(File.objects.filter(planning=OuterRef('pk'))))
            .filter(has_files=True).select_related('site', 'livraison').prefetch_related('file_set').
            annotate(year=ExtractYear('date_honored'), month=ExtractMonth('date_honored')).order_by('date_honored')
        )
    
    def get_context_data(self, **kwargs):
        filtered_qs = self.filterset.qs if hasattr(self, 'filterset') else self.get_queryset()
        
        grouped_data = {}
        for planning in filtered_qs:
            year = planning.date_honored.year
            month = (planning.date_honored.month, FRENCH_MONTHS[planning.date_honored.month].capitalize())
            site = planning.site
            client = (planning.client, planning.client_id)
            
            grouped_data.setdefault(year, {}).setdefault(month, {}).setdefault(site, {}).setdefault(client, []).append(planning)
        
        context = super().get_context_data(**kwargs)
        context['grouped_plannings'] = grouped_data
        context['filter'] = self.filterset
        
        return context

@require_GET
def planning_detail_api(request, pk):
    planning = get_object_or_404(Planning, pk=pk)
    
    files = []
    products = []
    for file in planning.files():
        filename = file.file.name.split('/')[-1]
        files.append({
            'name': filename,
            'url': file.file.url,
            'icon': 'fa-file-pdf text-danger',
            'uploaded_at': file.uploaded_at.strftime('%d/%m/%Y %H:%M') if file.uploaded_at else None
        })

    for product in planning.pplanneds():
        products.append({'name': product.__str__()})

    data = {
        'n_planning': planning.__str__(),
        'n_bl': f"{planning.site.prefix_site}{planning.n_bl:05d}/{planning.date_honored.strftime('%y')}",
        'date_honored': planning.date_honored.strftime('%d/%m/%Y') if planning.date_honored else None,
        'client': str(planning.client),
        'distributeur': planning.distributeur,
        'site': str(planning.site),
        'tonnage': str(planning.tonnage) if planning.tonnage else None,
        'destination': str(planning.destination),
        'chauffeur': planning.str_chauffeur,
        'vehicle': planning.str_immatriculation,
        'files': files,
        'products': products
    }
    
    return JsonResponse(data)

def getRedirectionURL(request, url_path):
    params = {
        'page': request.GET.get('page', '1'),
        'page_size': request.GET.get('page_size', '12'),
        'search': request.GET.get('search', ''),
        'state': request.GET.get('state', ''),
        'start_date': request.GET.get('start_date', ''),
        'end_date': request.GET.get('end_date', ''),
        'site': request.GET.get('site', ''),
        'distru': request.GET.get('distru', '')
    }
    cache_param = str(uuid.uuid4())
    query_string = '&'.join([f'{key}={value}' for key, value in params.items() if value])
    return f'{url_path}?cache={cache_param}&{query_string}'
