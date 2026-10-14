from rest_framework import serializers

from inventory.models import Device, DeviceModel, DeviceType
from inventory.serializers import DeviceSerializer

from .models import (BiohazardStatus, ReturnDeclaration, VisualCondition, Delivery, DetectedFault, Diagnosis, Disinfection, DossierSAV, Fault, Part,
                     Photo, QualityControl, Repair, ReplacedPart, StatusHistory, StockMovement)

MAX_PHOTO_BYTES = 5 * 1024 * 1024
PHOTO_TYPES = {'image/jpeg', 'image/png', 'image/webp'}


# --- Catalogues ---
class FaultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fault
        fields = ('id', 'device_type', 'name', 'active')


class PartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Part
        fields = ('id', 'reference', 'name', 'manufacturer', 'device_types', 'active')


# --- Lecture ---
class StatusHistorySerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)

    class Meta:
        model = StatusHistory
        fields = ('id', 'dossier', 'from_status', 'to_status', 'user', 'user_name', 'comment', 'at')


class DisinfectionSerializer(serializers.ModelSerializer):
    technician_name = serializers.CharField(source='technician.get_full_name', read_only=True)

    class Meta:
        model = Disinfection
        fields = ('product', 'validated', 'comment', 'technician', 'technician_name', 'at')


class DetectedFaultSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='fault.name', read_only=True)

    class Meta:
        model = DetectedFault
        fields = ('fault', 'name', 'severity', 'comment')


class DiagnosisSerializer(serializers.ModelSerializer):
    faults = DetectedFaultSerializer(many=True, read_only=True)

    class Meta:
        model = Diagnosis
        fields = ('comment', 'technician', 'at', 'faults')


class ReplacedPartSerializer(serializers.ModelSerializer):
    reference = serializers.CharField(source='part.reference', read_only=True)
    name = serializers.CharField(source='part.name', read_only=True)

    class Meta:
        model = ReplacedPart
        fields = ('part', 'reference', 'name', 'quantity')


class RepairSerializer(serializers.ModelSerializer):
    parts = ReplacedPartSerializer(many=True, read_only=True)
    duration_minutes = serializers.IntegerField(read_only=True)

    class Meta:
        model = Repair
        fields = ('started_at', 'ended_at', 'duration_minutes', 'tests', 'parts_exit_document', 'comment',
                  'technician', 'parts')


class QualityControlSerializer(serializers.ModelSerializer):
    class Meta:
        model = QualityControl
        fields = ('id', 'result', 'checklist', 'purity', 'flow_pressure', 'audible_alarm_ok',
                  'comment', 'technician', 'at')


class StockMovementSerializer(serializers.ModelSerializer):
    device_code = serializers.CharField(source='device.internal_code', read_only=True)
    dossier_reference = serializers.CharField(source='dossier.reference', read_only=True)

    class Meta:
        model = StockMovement
        fields = ('id', 'device', 'device_code', 'dossier', 'dossier_reference', 'kind',
                  'location', 'user', 'at')


class DeliverySerializer(serializers.ModelSerializer):
    class Meta:
        model = Delivery
        fields = ('recipient', 'delivery_note', 'comment', 'delivered_by', 'at')


class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ('id', 'kind', 'image', 'uploaded_by', 'at')
        read_only_fields = ('id', 'uploaded_by', 'at')

    def validate_image(self, f):
        if f.size > MAX_PHOTO_BYTES:
            raise serializers.ValidationError('Image trop volumineuse (5 Mo maximum).')
        if getattr(f, 'content_type', None) not in PHOTO_TYPES:
            raise serializers.ValidationError('Formats acceptés : JPEG, PNG, WebP.')
        return f


class DossierSerializer(serializers.ModelSerializer):
    device = DeviceSerializer(read_only=True)
    status_label = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = DossierSAV
        fields = ('id', 'reference', 'device', 'status', 'status_label', 'commercial', 'biohazard',
                  'biohazard_status', 'visual_condition', 'visual_state', 'hour_counter',
                  'return_declaration', 'missing_accessories', 'comment', 'received_by', 'received_at')
        read_only_fields = fields


def _opt(obj, attr):
    return getattr(obj, attr, None)


class DossierDetailSerializer(DossierSerializer):
    """Dossier complet : toutes les étapes réalisées."""

    disinfection = serializers.SerializerMethodField()
    diagnosis = serializers.SerializerMethodField()
    repair = serializers.SerializerMethodField()
    quality_controls = QualityControlSerializer(many=True, read_only=True)
    stock_movements = StockMovementSerializer(many=True, read_only=True)
    delivery = serializers.SerializerMethodField()
    photos = PhotoSerializer(many=True, read_only=True)
    history = StatusHistorySerializer(many=True, read_only=True)

    class Meta(DossierSerializer.Meta):
        fields = DossierSerializer.Meta.fields + (
            'disinfection', 'diagnosis', 'repair', 'quality_controls', 'stock_movements',
            'delivery', 'photos', 'history')
        read_only_fields = fields

    def get_disinfection(self, o):
        v = _opt(o, 'disinfection')
        return DisinfectionSerializer(v).data if v else None

    def get_diagnosis(self, o):
        v = _opt(o, 'diagnosis')
        return DiagnosisSerializer(v).data if v else None

    def get_repair(self, o):
        v = _opt(o, 'repair')
        return RepairSerializer(v).data if v else None

    def get_delivery(self, o):
        v = _opt(o, 'delivery')
        return DeliverySerializer(v).data if v else None


# --- Entrées (actions) ---
class ReturnDeclarationSerializer(serializers.ModelSerializer):
    received = serializers.SerializerMethodField()
    dossier_id = serializers.SerializerMethodField()
    declared_by_name = serializers.CharField(source='declared_by.get_full_name', read_only=True)

    class Meta:
        model = ReturnDeclaration
        fields = ('id', 'return_id', 'serial_number', 'visual_condition', 'missing_accessories',
                  'biohazard_status', 'declared_by', 'declared_by_name', 'declared_at',
                  'received', 'dossier_id')
        read_only_fields = ('id', 'declared_by', 'declared_at')

    def get_received(self, o):
        return hasattr(o, 'dossier')

    def get_dossier_id(self, o):
        return o.dossier.id if hasattr(o, 'dossier') else None

    def validate_serial_number(self, v):
        v = Device.normalize_serial(v)
        if not v:
            raise serializers.ValidationError('Numéro de série obligatoire.')
        return v

    def validate_return_id(self, v):
        v = v.strip()
        if not v:
            raise serializers.ValidationError("L'ID de retour est obligatoire.")
        return v


class ReceptionSerializer(serializers.Serializer):
    return_declaration = serializers.PrimaryKeyRelatedField(
        queryset=ReturnDeclaration.objects.all(), required=False, allow_null=True)
    serial_number = serializers.CharField(max_length=100)
    visual_condition = serializers.ChoiceField(choices=VisualCondition.choices, default='GOOD')
    biohazard_status = serializers.ChoiceField(choices=BiohazardStatus.choices, default='UNKNOWN')
    hour_counter = serializers.DecimalField(max_digits=9, decimal_places=1, required=False,
                                            allow_null=True, min_value=0)
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


class DisinfectionInput(serializers.Serializer):
    product = serializers.CharField(max_length=150, required=False, allow_blank=True, default='')
    validated = serializers.BooleanField(default=True)
    comment = serializers.CharField(required=False, allow_blank=True, default='')


class DetectedFaultInput(serializers.Serializer):
    fault = serializers.PrimaryKeyRelatedField(queryset=Fault.objects.filter(active=True))
    severity = serializers.ChoiceField(choices=DetectedFault.Severity.choices, default='MAJEURE')
    comment = serializers.CharField(max_length=300, required=False, allow_blank=True, default='')


class DiagnosisInput(serializers.Serializer):
    faults = DetectedFaultInput(many=True, allow_empty=True)
    comment = serializers.CharField(required=False, allow_blank=True, default='')


class PartInput(serializers.Serializer):
    part = serializers.PrimaryKeyRelatedField(queryset=Part.objects.filter(active=True))
    quantity = serializers.IntegerField(min_value=1, default=1)


class RepairInput(serializers.Serializer):
    parts_exit_document = serializers.CharField(max_length=60, required=False, allow_blank=True, default='')
    started_at = serializers.DateTimeField()
    ended_at = serializers.DateTimeField()
    parts = PartInput(many=True, required=False, default=list)
    tests = serializers.CharField(required=False, allow_blank=True, default='')
    comment = serializers.CharField(required=False, allow_blank=True, default='')


class QualityControlInput(serializers.Serializer):
    checklist = serializers.DictField(child=serializers.BooleanField())
    purity = serializers.DecimalField(max_digits=4, decimal_places=1, required=False, allow_null=True,
                                      min_value=0, max_value=100)
    flow_pressure = serializers.CharField(max_length=50, required=False, allow_blank=True, default='')
    audible_alarm_ok = serializers.BooleanField(required=False, allow_null=True, default=None)
    comment = serializers.CharField(required=False, allow_blank=True, default='')


class StockInput(serializers.Serializer):
    location = serializers.CharField(max_length=100)


class DeliveryInput(serializers.Serializer):
    recipient = serializers.CharField(max_length=150)
    delivery_note = serializers.CharField(max_length=60, required=False, allow_blank=True, default='')
    comment = serializers.CharField(required=False, allow_blank=True, default='')
