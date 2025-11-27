from rest_framework import serializers
from commercial.models import *
from .models import *

class FileValidationSerializer(serializers.ModelSerializer):
    actor = serializers.CharField(source='actor.fullname', read_only=True)

    class Meta:
        model = FileValidation
        fields = ['id', 'old_state', 'new_state', 'date', 'actor', 'refusal_reason']

class FileSerializer(serializers.ModelSerializer):
    validations = FileValidationSerializer(many=True, read_only=True)
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = File
        fields = ['id', 'file_url', 'uploaded_at', 'state', 'validations']

    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and hasattr(obj.file, 'url'):
            return request.build_absolute_uri(obj.file.url) if request else obj.file.url
        return None

class PlanningSerializer(serializers.ModelSerializer):

    site = serializers.CharField(source='site.designation', read_only=True)
    destination = serializers.CharField(source='destination.designation', read_only=True)
    fournisseur = serializers.CharField(source='fournisseur.designation', read_only=True)
    client = serializers.CharField(read_only=True)

    sequence = serializers.ReadOnlyField()
    n_bl = serializers.ReadOnlyField()
    google_maps_coords = serializers.ReadOnlyField()
    date_delivered = serializers.ReadOnlyField()

    driver_last_name = serializers.CharField(source='driver.last_name', read_only=True)
    driver_first_name = serializers.CharField(source='driver.first_name', read_only=True)
    driver_phone = serializers.CharField(source='driver.phone', read_only=True)
    driver_address = serializers.CharField(source='driver.address', read_only=True)
    immatriculation = serializers.CharField(source='vehicle.immatriculation', read_only=True)
    vehicle_code = serializers.CharField(source='vehicle.designation', read_only=True)

    files = FileSerializer(many=True, read_only=True)

    class Meta:
        model = Planning
        fields = [
            'id', 'site', 'destination', 'fournisseur', 'date_planning', 'n_bl', 'client',
            'google_maps_coords', 'sequence', 'code', 'vehicle_code',
            'driver_last_name', 'driver_first_name', 'driver_phone',
            'driver_address', 'immatriculation', 'files', 'date_delivered'
            ]

class PlanningExternSerializer(serializers.ModelSerializer):

    site = serializers.CharField(source='site.designation', read_only=True)
    destination = serializers.CharField(source='destination.designation', read_only=True)
    fournisseur = serializers.CharField(source='fournisseur.designation', read_only=True)
    client = serializers.CharField(read_only=True)

    sequence = serializers.ReadOnlyField()
    n_bl = serializers.ReadOnlyField()
    google_maps_coords = serializers.ReadOnlyField()
    date_delivered = serializers.ReadOnlyField()


    files = FileSerializer(many=True, read_only=True)

    class Meta:
        model = Planning
        fields = [
            'id', 'site', 'destination', 'fournisseur', 'date_planning', 'n_bl', 'client',
            'google_maps_coords', 'sequence', 'code', 'chauffeur', 'immatriculation', 'files', 'date_delivered']
