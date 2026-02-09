from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from commercial.models import *
import json
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from .serializers import *
from rest_framework.authentication import TokenAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response
from collections import defaultdict
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from firebase_admin import messaging
from django.db.models import Q, Count, Case, When, Value, CharField, F, Max
from rest_framework.pagination import PageNumberPagination

@csrf_exempt
def lookup_planning_by_code(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            code = data.get('code')
            planning = Planning.objects.get(code=code, is_marked=False, state='Livraison Confirmé')
            if planning.driver:
                return JsonResponse({'error': 'Ce planning est interne. Authentification requise.'}, status=403)
            
            serializer = PlanningExternSerializer(planning)
            if serializer.data:
                return JsonResponse({'planning': serializer.data})
            else:
                return JsonResponse({'error': 'Aucun planning trouvé'}, status=404)

        except Planning.DoesNotExist:
            return JsonResponse({'error': 'Code non trouvé'}, status=404)
    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def lookup_planning_by_code_internal(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            code = data.get('code')
            
            user_role = request.user.role
            if user_role not in ['Admin', 'Chauffeur']:
                return JsonResponse({'error': 'Accès non autorisé. Seul Admin ou Chauffeur peut accéder à cette fonctionnalité.'}, status=403)
            
            planning = Planning.objects.get(code=code)
            if not planning.driver:
                return JsonResponse({'error': 'Ce planning est externe, accès non autorisé.'}, status=403)
            
            serializer = PlanningSerializer(planning)
            if serializer.data:
                return JsonResponse({'planning': serializer.data})
            else:
                return JsonResponse({'error': 'Aucun planning trouvé'}, status=404)

        except Planning.DoesNotExist:
            return JsonResponse({'error': 'Code non trouvé'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Données JSON invalides'}, status=400)
    
    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)

@csrf_exempt
def submit_planning_data(request):
    if request.method == 'POST':
        planning_id = request.POST.get('planning_id')
        x = request.POST.get('coords_x')
        y = request.POST.get('coords_y')
        files = request.FILES.getlist('files')

        deleted_files_raw = request.data.get('deleted_files', '[]')
        
        try:
            deleted_files = json.loads(deleted_files_raw)
        except (TypeError, json.JSONDecodeError):
            deleted_files = []

        try:
            planning = Planning.objects.get(id=planning_id)
        except Planning.DoesNotExist:
            return JsonResponse({'error': 'ID planning invalide'}, status=400)

        if planning.driver:
            return JsonResponse({'error': 'Ce planning est interne. Authentification requise.'}, status=403)
        
        files_state = planning.files_state
        
        if planning.files_state == 'Refusé':
            refused_files = File.objects.filter(planning=planning, state='Refusé')
            for file in refused_files:
                file.corrected = True
                file.save()

        if x and y:
            planning.google_maps_coords = f"{x},{y}"
            planning.save()

        for file in files:
            File.objects.create(planning=planning, file=file)

        for file in deleted_files:
            try:
                file_instance = File.objects.get(id=file)
                file_instance.delete()
            except File.DoesNotExist:
                continue

        users_to_notify = User.objects.filter(role__in=['Admin', 'Logisticien'], sites=planning.site).distinct()
        for user in users_to_notify:
            title = "Nouveaux fichiers ajoutés" if files_state != 'Refusé' else "Fichiers corrigés"
            body = f"Le planning {planning.code} a de nouveaux fichiers ajoutés."
            data = {"planning_id": str(planning.id), "type": "new_files", "planning_code": planning.code}
            results = send_push_to_user(user, title, body, data)

        return JsonResponse({'message': 'Soumission réussie', "firebase_results": results})
    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def submit_planning_data_internal(request):
    if request.method == 'POST':
        planning_id = request.data.get('planning_id')
        x = request.data.get('coords_x')
        y = request.data.get('coords_y')
        files = request.FILES.getlist('files')

        deleted_files_raw = request.data.get('deleted_files', '[]')
        
        try:
            deleted_files = json.loads(deleted_files_raw)
        except (TypeError, json.JSONDecodeError):
            deleted_files = []

        try:
            planning = Planning.objects.get(id=planning_id)
        except Planning.DoesNotExist:
            return Response({'error': 'ID planning invalide'}, status=400)
        
        files_state = planning.files_state
        
        if files_state == 'Refusé':
            refused_files = File.objects.filter(planning=planning, state='Refusé')
            for file in refused_files:
                file.corrected = True
                file.save()

        user_role = request.user.role
        if user_role not in ['Admin', 'Chauffeur']:
            return Response({'error': 'Accès non autorisé. Seul Admin ou Chauffeur peut accéder à cette fonctionnalité.'}, status=403)

        if x and y:
            planning.google_maps_coords = f"{x},{y}"
            planning.save()

        for file in files:
            File.objects.create(planning=planning, file=file)

        for file in deleted_files:
            try:
                file_instance = File.objects.get(id=file)
                file_instance.delete()
            except File.DoesNotExist:
                continue

        users_to_notify = User.objects.filter(role__in=['Admin', 'Logisticien'], sites=planning.site).distinct()
        for user in users_to_notify:
            title = "Nouveaux fichiers ajoutés" if files_state != 'Refusé' else "Fichiers corrigés"
            body = f"Le planning {planning.code} a de nouveaux fichiers ajoutés - par {request.user.fullname}."
            data = {"planning_id": str(planning.id), "type": "new_files", "planning_code": planning.code}
            results = send_push_to_user(user, title, body, data)

        return Response({'message': 'Soumission réussie', "firebase_results": results})
    return Response({'error': 'Méthode non autorisée'}, status=405)

@csrf_exempt
def login_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')

            if not username or not password:
                return JsonResponse({'success': False, 'message': 'Nom d\'utilisateur et mot de passe requis.'}, status=400)

            user = authenticate(request, username=username, password=password)

            if user is not None:
                token, _ = Token.objects.get_or_create(user=user)
                return JsonResponse({'success': True, 'token': token.key, 'fullname': user.fullname, 'role': user.role}, status=200)
            else:
                return JsonResponse({'success': False, 'message': 'Identifiants invalides.'}, status=401)

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Données JSON invalides.'}, status=400)

    return JsonResponse({'success': False, 'message': 'Méthode non autorisée.'}, status=405)

class PlanningPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

class getPlanningsView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        sites = user.sites.all()
        queryset = (
            Planning.objects
            .filter(is_marked=False, state='Livraison Confirmé', code__isnull=False, site__in=sites)
            .select_related('site', 'destination', 'fournisseur', 'driver', 'vehicle', 'tonnage')
            .prefetch_related('files__validations')
        )
        
        queryset = queryset.annotate(
            annotated_date_delivered=Max(
                'validation__date', 
                filter=Q(validation__new_state='Livraison Confirmé')
            ),
            unfilled_files_count=Count('files', filter=Q(files__corrected=False)),
            approved_files_count=Count('files', filter=Q(files__corrected=False, files__state='Approuvé')),
            refused_files_count=Count('files', filter=Q(files__corrected=False, files__state='Refusé')),
        ).annotate(
            annotated_state=Case(
                When(unfilled_files_count=0, then=Value('En route')),
                When(refused_files_count__gt=0, then=Value('Refusé')),
                When(Q(unfilled_files_count__gt=0) & Q(unfilled_files_count=F('approved_files_count')), then=Value('Approuvé')),
                default=Value('En attente'),
                output_field=CharField(),
            )
        )

        search = request.query_params.get('search')
        state = request.query_params.get('state')
        site_id = request.query_params.get('site_id')
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')

        if search:
            queryset = queryset.filter(
                Q(code__icontains=search) |
                Q(n_bl__icontains=search) |
                Q(client__icontains=search) |
                Q(destination__designation__icontains=search) |
                Q(driver__first_name__icontains=search) |
                Q(driver__last_name__icontains=search) |
                Q(vehicle__immatriculation__icontains=search) |
                Q(immatriculation__icontains=search) |
                Q(id__icontains=search) |
                Q(site__planning_prefix__icontains=search)
            ).distinct()
        if site_id:
            queryset = queryset.filter(site_id=site_id)
        if state:
            queryset = queryset.filter(annotated_state=state)
        if date_from:
            queryset = queryset.filter(annotated_date_delivered__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(annotated_date_delivered__date__lte=date_to)

        queryset = queryset.order_by('site__designation', '-date_created')
        paginator = PlanningPagination()
        page = paginator.paginate_queryset(queryset, request, view=self)
        if page is not None:
            serializer = PlanningSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        serializer = PlanningSerializer(queryset, many=True)
        return paginator.get_paginated_response(serializer.data)

class getRefusalReasonsView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        reasons = FileRefusal.objects.all().order_by('designation')
        serializer = FileRefusalSerializer(reasons, many=True)

        return Response({"refusal_reasons": serializer.data})
    
class getSitesView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        sites = user.sites.all().order_by('designation')
        serializer = SiteSerializer(sites, many=True)

        return Response({"sites": serializer.data})

class ApproveFileView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, file_id):
        user = request.user
        file_obj = get_object_or_404(File, id=file_id)

        old_state = file_obj.state

        file_obj.state = 'Approuvé'
        file_obj.save()

        if file_obj.planning.driver and file_obj.planning.driver.user:
            target_user = file_obj.planning.driver.user
            title = "Fichier approuvé"
            body = f"Le fichier pour le planning {file_obj.planning.code} a été approuvé."
            data = {"planning_id": str(file_obj.planning.id), "file_id": str(file_obj.id), "type": "file_approved", "planning_code": file_obj.planning.code}
            results = send_push_to_user(target_user, title, body, data)

        FileValidation.objects.create(file=file_obj, old_state=old_state, new_state='Approuvé', actor=user)

        return Response({"message": "Fichier approuvé avec succès.", "firebase_results": results}, status=status.HTTP_200_OK)

class RefuseFileView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, file_id):
        user = request.user
        refusal_reason = request.data.get('refusal_reason', '').strip()
        cause_id = request.data.get('cause_id', None)
        if not refusal_reason:
            return Response({"error": "Le motif de refus est requis."}, status=status.HTTP_400_BAD_REQUEST)

        file_obj = get_object_or_404(File, id=file_id)
        old_state = file_obj.state

        file_obj.state = 'Refusé'
        file_obj.save()

        try:
            cause = FileRefusal.objects.get(id=cause_id)
        except FileRefusal.DoesNotExist:
            return Response({"error": "Le motif de refus spécifié n'existe pas."}, status=status.HTTP_400_BAD_REQUEST)
        
        FileValidation.objects.create(file=file_obj, old_state=old_state, cause=cause, new_state='Refusé', actor=user, refusal_reason=refusal_reason)

        planning = file_obj.planning

        if planning.driver and planning.driver.user:
            target_user = planning.driver.user
            title = "Fichier refusé"
            body = f"Le fichier pour le planning {planning.code} a été refusé - {cause.designation}."
            data = {"planning_id": str(planning.id), "file_id": str(file_obj.id), "type": "file_refused", "planning_code": planning.code}
            results = send_push_to_user(target_user, title, body, data)
        # else if internal user is planning.creator (adjust to your logic)
        elif planning.creator:
            # notify creator's app
            results = send_push_to_user(planning.creator, "Fichier refusé", f"Le fichier pour {planning} a été refusé.", {"planning_id": str(planning.id)})
        else:
            results = ""
        # else: optionally notify supplier via email (handled elsewhere)

        # 🔴 Placeholder for notifications/emails
        # if planning.driver:
        #     send_internal_notification(planning.driver, file_obj)
        # elif planning.chauffeur and planning.fournisseur and planning.fournisseur.address:
        #     send_email_to_supplier(planning.fournisseur.address, file_obj)

        return Response({"message": "Fichier refusé avec succès.", "firebase_results": results}, status=status.HTTP_200_OK)

class ApprovePlanningView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, planning_id):
        user = request.user
        planning_obj = get_object_or_404(Planning, id=planning_id)
        
        files_to_approve = File.objects.filter(planning=planning_obj).exclude(state='Approuvé')
        
        approved_count = 0
        for file_obj in files_to_approve:
            old_state = file_obj.state
            file_obj.state = 'Approuvé'
            file_obj.save()
            FileValidation.objects.create(file=file_obj, old_state=old_state, new_state='Approuvé', actor=user)
            approved_count += 1

        if planning_obj.driver and planning_obj.driver.user:
            target_user = planning_obj.driver.user
            title = "Fichier(s) approuvés"
            body = f"Les fichiers pour le planning {planning_obj.code} ont été approuvés."
            data = {"planning_id": str(planning_obj.id), "type": "file_approved", "planning_code": planning_obj.code}
            results = send_push_to_user(target_user, title, body, data)

        return Response({"message": f"Planning approuvé avec succès. {approved_count} fichier(s) approuvé(s).", "firebase_results": results}, status=status.HTTP_200_OK)

class RefusePlanningView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, planning_id):
        user = request.user
        refusal_reason = request.data.get('refusal_reason', '').strip()
        cause_id = request.data.get('cause_id', None)
        if not refusal_reason:
            return Response({"error": "Le motif de refus est requis."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            cause = FileRefusal.objects.get(id=cause_id)
        except FileRefusal.DoesNotExist:
            return Response({"error": "Le motif de refus spécifié n'existe pas."}, status=status.HTTP_400_BAD_REQUEST)
        planning_obj = get_object_or_404(Planning, id=planning_id)
        
        files_to_refuse = File.objects.filter(planning=planning_obj).exclude(state='Refusé')
        
        refused_count = 0
        for file_obj in files_to_refuse:
            old_state = file_obj.state
            file_obj.state = 'Refusé'
            file_obj.save()
            FileValidation.objects.create(file=file_obj, old_state=old_state, cause=cause, new_state='Refusé', actor=user, refusal_reason=refusal_reason)
            refused_count += 1

        if planning_obj.driver and planning_obj.driver.user:
            target_user = planning_obj.driver.user
            title = "Planning refusé"
            body = f"Le planning {planning_obj.code} a été refusé - {cause.designation}."
            data = {"planning_id": str(planning_obj.id), "type": "planning_refused", "planning_code": planning_obj.code}
            results = send_push_to_user(target_user, title, body, data)
        elif planning_obj.creator:
            results = send_push_to_user(planning_obj.creator, "Planning refusé", f"Le planning {planning_obj} a été refusé.", {"planning_id": str(planning_obj.id)})
        else: 
            results = ""

        return Response({"message": f"Planning refusé avec succès. {refused_count} fichier(s) refusé(s).", "firebase_results": results}, status=status.HTTP_200_OK)

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def register_device(request):
    token = request.data.get('token')
    device_type = request.data.get('device_type', 'android')
    if not token:
        return Response({'error': 'token required'}, status=400)
    Device.objects.update_or_create(token=token, defaults={'user': request.user, 'device_type': device_type})
    return Response({'ok': True})

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def unregister_device(request):
    token = request.data.get('token')
    if token:
        Device.objects.filter(token=token).delete()
    return Response({'ok': True})

def send_push_to_tokens(tokens, title, body, data=None):
    if not tokens:
        return {'success': 0, 'failure': 0}

    success, failure = 0, 0
    results = []
    for token in tokens:
        message = messaging.Message(notification=messaging.Notification(title=title, body=body), data={k: str(v) for k, v in (data or {}).items()}, token=token)
        try:
            response = messaging.send(message)
            success += 1
            results.append({'token': token, 'response': response})
        except Exception as e:
            failure += 1
            results.append({'token': token, 'error': str(e)})

    return {'success': success, 'failure': failure, 'responses': results}

def send_push_to_user(user, title, body, data=None):
    tokens = list(Device.objects.filter(user=user).values_list('token', flat=True))
    return send_push_to_tokens(tokens, title, body, data)

class getPlanningCodeView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        refused_plannings_data = []
        if request.user.role == 'Chauffeur':
            refused_plannings = Planning.objects.filter(driver__user=request.user, state='Livraison Confirmé', is_marked=False).distinct()
            refused_plannings = [p for p in refused_plannings if p.files_state == 'Refusé']
            refused_plannings_data = PlanningCodeSerializer(refused_plannings, many=True).data

        return Response({"refused_plannings": refused_plannings_data})
