from rest_framework import serializers

from inventory.models import DeviceModel, DeviceType
from inventory.serializers import DeviceSerializer

from .models import DossierSAV, StatusHistory


class StatusHistorySerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)

    class Meta:
        model = StatusHistory
        fields = ('id', 'dossier', 'from_status', 'to_status', 'user', 'user_name', 'comment', 'at')


class DossierSerializer(serializers.ModelSerializer):
    device = DeviceSerializer(read_only=True)
    status_label = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = DossierSAV
        fields = ('id', 'reference', 'device', 'status', 'status_label', 'commercial', 'biohazard',
                  'visual_state', 'missing_accessories', 'comment', 'received_by', 'received_at')
        read_only_fields = fields


class ReceptionSerializer(serializers.Serializer):
    serial_number = serializers.CharField(max_length=100)
    device_type = serializers.PrimaryKeyRelatedField(queryset=DeviceType.objects.all())
    model = serializers.PrimaryKeyRelatedField(queryset=DeviceModel.objects.all(), required=False,
                                               allow_null=True)
    commercial = serializers.CharField(max_length=100, required=False, allow_blank=True)
    biohazard = serializers.BooleanField(required=False)
    visual_state = serializers.CharField(max_length=200, required=False, allow_blank=True)
    missing_accessories = serializers.CharField(max_length=200, required=False, allow_blank=True)
    comment = serializers.CharField(required=False, allow_blank=True)

    def validate(self, data):
        m = data.get('model')
        if m and m.device_type_id != data['device_type'].id:
            raise serializers.ValidationError({'model': 'Ce modèle ne correspond pas à ce type.'})
        return data


class TransitionSerializer(serializers.Serializer):
    to_status = serializers.ChoiceField(choices=DossierSAV.Status.choices)
    comment = serializers.CharField(required=False, allow_blank=True, default='')
