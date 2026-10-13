from rest_framework import serializers

from .models import Brand, Device, DeviceModel, DeviceType


class DeviceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceType
        fields = ('id', 'name')


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ('id', 'name')


class DeviceModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceModel
        fields = ('id', 'brand', 'device_type', 'name')


class DeviceSerializer(serializers.ModelSerializer):
    type_name = serializers.CharField(source='device_type.name', read_only=True)
    model_name = serializers.SerializerMethodField()

    class Meta:
        model = Device
        fields = ('id', 'internal_code', 'serial_number', 'device_type', 'type_name',
                  'model', 'model_name', 'created_at')
        read_only_fields = fields

    def get_model_name(self, obj):
        return str(obj.model) if obj.model else None
