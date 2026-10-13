from django.conf import settings
from django.db import models, transaction


class DeviceType(models.Model):
    name = models.CharField('nom', max_length=100, unique=True)

    def __str__(self):
        return self.name


class Brand(models.Model):
    name = models.CharField('nom', max_length=100, unique=True)

    def __str__(self):
        return self.name


class DeviceModel(models.Model):
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, related_name='models')
    device_type = models.ForeignKey(DeviceType, on_delete=models.PROTECT, related_name='models')
    name = models.CharField('nom', max_length=100)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['brand', 'name'], name='uniq_model_per_brand')]

    def __str__(self):
        return f'{self.brand} {self.name}'


class Device(models.Model):
    """Appareil physique : une seule fiche de vie, jamais recréée."""

    serial_number = models.CharField('numéro de série', max_length=100, unique=True)
    internal_code = models.CharField('code interne', max_length=20, unique=True, null=True,
                                     blank=True, editable=False)
    device_type = models.ForeignKey(DeviceType, on_delete=models.PROTECT, related_name='devices')
    model = models.ForeignKey(DeviceModel, on_delete=models.PROTECT, null=True, blank=True,
                              related_name='devices')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
                                   related_name='+')
    created_at = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def normalize_serial(value):
        return ''.join(value.split()).upper()

    def save(self, *args, **kwargs):
        self.serial_number = self.normalize_serial(self.serial_number)
        with transaction.atomic():
            super().save(*args, **kwargs)
            if not self.internal_code:
                self.internal_code = f'APP-{self.pk:06d}'
                super().save(update_fields=['internal_code'])

    def __str__(self):
        return f'{self.internal_code} · {self.serial_number}'
