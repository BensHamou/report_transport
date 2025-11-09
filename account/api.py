from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from commercial.models import *
import json
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from .serializers import *
import json
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import NotAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from collections import defaultdict
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from firebase_admin import messaging

@csrf_exempt
def lookup_planning_by_code(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        code = data.get('code')
        try:
            planning = Planning.objects.get(code=code, is_marked=False, state='Livraison Confirmé')
            bl_number = f"{planning.site.prefix_site}{planning.n_bl:05d}/{planning.date_honored.strftime('%y')}" if planning.n_bl and planning.date_honored else '/'

            return JsonResponse({
                'planning_id': planning.id,
                'supplier': planning.fournisseur.designation if planning.fournisseur else '/',
                'driver': planning.str_chauffeur if planning.str_chauffeur else '/',
                'bl_number': '/',
                'n_invoice': bl_number,
                'destination': planning.site.designation if planning.site else '/',
                'depart': planning.destination.designation if planning.destination else '/',
                'date': planning.date_honored.strftime('%d/%m/%Y') if planning.date_honored else '/',
                
            })
        except Planning.DoesNotExist:
            return JsonResponse({'error': 'Code non trouvé'}, status=404)
    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)


@csrf_exempt
def submit_planning_data(request):
    if request.method == 'POST':
        planning_id = request.POST.get('planning_id')
        x = request.POST.get('coords_x')
        y = request.POST.get('coords_y')
        files = request.FILES.getlist('files')
        deleted_files = request.FILES.getlist('deleted_files')

        try:
            planning = Planning.objects.get(id=planning_id)
        except Planning.DoesNotExist:
            return JsonResponse({'error': 'ID planning invalide'}, status=400)

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

        return JsonResponse({'message': 'Soumission réussie'})
    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)

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

class getPlanningsView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        plannings = (
            Planning.objects
            .filter(is_marked=False, state='Livraison Confirmé', code__isnull=False)
            .select_related('site', 'destination', 'fournisseur', 'driver', 'vehicle')
            .prefetch_related('files__validations')
            .order_by('site__designation', 'date_created')
        )

        grouped_data = defaultdict(lambda: defaultdict(list))
        for p in plannings:
            site_name = p.site.designation
            files_state = p.files_state
            grouped_data[site_name][files_state].append(PlanningSerializer(p).data)

        # Convert defaultdicts to regular dicts for JSON serialization
        grouped_dict = {
            site: {state: plans for state, plans in states.items()}
            for site, states in grouped_data.items()
        }

        return Response({"plannings": grouped_dict})
    
class ApproveFileView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, file_id):
        user = request.user
        file_obj = get_object_or_404(File, id=file_id)

        old_state = file_obj.state

        file_obj.state = 'Approuvé'
        file_obj.save()

        FileValidation.objects.create(file=file_obj, old_state=old_state, new_state='Approuvé', actor=user)

        return Response({"message": "Fichier approuvé avec succès."}, status=status.HTTP_200_OK)


class RefuseFileView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, file_id):
        user = request.user
        refusal_reason = request.data.get('refusal_reason', '').strip()
        if not refusal_reason:
            return Response({"error": "Le motif de refus est requis."}, status=status.HTTP_400_BAD_REQUEST)

        file_obj = get_object_or_404(File, id=file_id)
        old_state = file_obj.state

        file_obj.state = 'Refusé'
        file_obj.save()

        FileValidation.objects.create(file=file_obj, old_state=old_state, new_state='Refusé', actor=user, refusal_reason=refusal_reason)

        planning = file_obj.planning

        if planning.driver and planning.driver.user:
            target_user = planning.driver.user
            title = "Fichier refusé"
            body = f"Le fichier pour le planning {planning.code} a été refusé."
            data = {"planning_id": str(planning.id), "file_id": str(file_obj.id), "type": "file_refused"}
            send_push_to_user(target_user, title, body, data)
        # else if internal user is planning.creator (adjust to your logic)
        elif planning.creator:
            # notify creator's app
            send_push_to_user(planning.creator, "Fichier refusé", f"Le fichier pour {planning} a été refusé.", {"planning_id": str(planning.id)})
        # else: optionally notify supplier via email (handled elsewhere)

        # 🔴 Placeholder for notifications/emails
        # if planning.driver:
        #     send_internal_notification(planning.driver, file_obj)
        # elif planning.chauffeur and planning.fournisseur and planning.fournisseur.address:
        #     send_email_to_supplier(planning.fournisseur.address, file_obj)

        return Response({"message": "Fichier refusé avec succès."}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def register_device(request):
    token = request.data.get('token')
    device_type = request.data.get('device_type', 'android')
    if not token:
        return Response({'error': 'token required'}, status=400)
    Device.objects.update_or_create(token=token, defaults={'user': request.user, 'device_type': device_type})
    return Response({'ok': True})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def unregister_device(request):
    token = request.data.get('token')
    if token:
        Device.objects.filter(token=token).delete()
    return Response({'ok': True})

def send_push_to_tokens(tokens, title, body, data=None):
    if not tokens:
        return {'success': 0, 'failure': 0}

    message = messaging.MulticastMessage(notification=messaging.Notification(title=title, body=body),
                                         data={k:str(v) for k,v in (data or {}).items()}, tokens=tokens )

    response = messaging.send_multicast(message)
    return {
        'success': response.success_count,
        'failure': response.failure_count,
        'responses': [r.__dict__ for r in response.responses]
    }

def send_push_to_user(user, title, body, data=None):
    tokens = list(Device.objects.filter(user=user).values_list('token', flat=True))
    return send_push_to_tokens(tokens, title, body, data)