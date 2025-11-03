from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from commercial.models import *
import json
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate

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