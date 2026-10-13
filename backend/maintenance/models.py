from django.conf import settings
from django.db import models, transaction
from django.db.models import Q

from inventory.models import Device


class DossierSAV(models.Model):
    """Un retour SAV d'un appareil. Un appareil peut en avoir plusieurs au fil du temps."""

    class Status(models.TextChoices):
        RECU = 'RECU', 'Reçu'
        DESINFECTE = 'DESINFECTE', 'Désinfecté'
        DIAGNOSTIC_TERMINE = 'DIAGNOSTIC_TERMINE', 'Diagnostic terminé'
        REPARE = 'REPARE', 'Réparé'
        QC_VALIDE = 'QC_VALIDE', 'Contrôle qualité validé'
        EN_STOCK = 'EN_STOCK', 'En stock livrable'
        LIVRE = 'LIVRE', 'Livré'

    reference = models.CharField(max_length=20, unique=True, null=True, blank=True, editable=False)
    device = models.ForeignKey(Device, on_delete=models.PROTECT, related_name='dossiers')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.RECU)
    commercial = models.CharField(max_length=100, blank=True)
    biohazard = models.BooleanField('risque biologique', default=False)
    visual_state = models.CharField('état visuel', max_length=200, blank=True)
    missing_accessories = models.CharField('accessoires manquants', max_length=200, blank=True)
    comment = models.TextField(blank=True)
    received_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
                                    related_name='+')
    received_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-received_at']
        constraints = [
            # Un seul dossier ouvert par appareil.
            models.UniqueConstraint(fields=['device'], condition=~Q(status='LIVRE'),
                                    name='one_open_dossier_per_device'),
        ]

    def save(self, *args, **kwargs):
        with transaction.atomic():
            super().save(*args, **kwargs)
            if not self.reference:
                self.reference = f'SAV-{self.received_at.year}-{self.pk:05d}'
                super().save(update_fields=['reference'])

    def __str__(self):
        return self.reference or f'SAV-{self.pk}'


class StatusHistory(models.Model):
    """Journal immuable des changements de statut."""

    dossier = models.ForeignKey(DossierSAV, on_delete=models.PROTECT, related_name='history')
    from_status = models.CharField(max_length=20, blank=True)
    to_status = models.CharField(max_length=20)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='+')
    comment = models.TextField(blank=True)
    at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['at', 'id']

    def save(self, *args, **kwargs):
        if self.pk:
            raise ValueError("L'historique ne peut pas être modifié.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValueError("L'historique ne peut pas être supprimé.")
