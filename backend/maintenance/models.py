from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models, transaction
from django.db.models import Q

from inventory.models import Device, DeviceType

User = settings.AUTH_USER_MODEL


class VisualCondition(models.TextChoices):
    GOOD = 'GOOD', 'Bon état'
    MINOR_DAMAGE = 'MINOR_DAMAGE', 'Dégâts mineurs'
    NEED_REPAIR = 'NEED_REPAIR', 'Réparation nécessaire'
    BIOHAZARD = 'BIOHAZARD', 'Risque biologique'


class BiohazardStatus(models.TextChoices):
    NORMAL = 'NORMAL', 'Normal'
    HEAVY_CONTAMINATION = 'HEAVY_CONTAMINATION', 'Contamination importante'
    UNKNOWN = 'UNKNOWN', 'Inconnu'


class ReturnDeclaration(models.Model):
    """Questionnaire rempli AVANT l'arrivée de l'appareil (annonce de retour)."""

    return_id = models.CharField('ID de retour', max_length=60, unique=True)
    serial_number = models.CharField('numéro de série', max_length=100)
    visual_condition = models.CharField(max_length=20, choices=VisualCondition.choices)
    missing_accessories = models.CharField('accessoires manquants', max_length=200, blank=True)
    biohazard_status = models.CharField(max_length=20, choices=BiohazardStatus.choices)
    declared_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='+')
    declared_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-declared_at']

    def __str__(self):
        return f'{self.return_id} · {self.serial_number}'

    @property
    def received(self):
        return hasattr(self, 'dossier') and self.dossier is not None


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
    biohazard_status = models.CharField(max_length=20, choices=BiohazardStatus.choices,
                                        default=BiohazardStatus.UNKNOWN)
    visual_condition = models.CharField(max_length=20, choices=VisualCondition.choices,
                                        default=VisualCondition.GOOD)
    visual_state = models.CharField('état visuel (précisions)', max_length=200, blank=True)
    hour_counter = models.DecimalField('compteur horaire (C.H)', max_digits=9, decimal_places=1,
                                       null=True, blank=True)
    return_declaration = models.OneToOneField(ReturnDeclaration, on_delete=models.PROTECT,
                                              null=True, blank=True, related_name='dossier')
    missing_accessories = models.CharField('accessoires manquants', max_length=200, blank=True)
    comment = models.TextField(blank=True)
    received_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='+')
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
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='+')
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


# --- Catalogues -------------------------------------------------------------

class Fault(models.Model):
    """Catalogue des pannes, associé à un type d'appareil."""

    device_type = models.ForeignKey(DeviceType, on_delete=models.PROTECT, related_name='faults')
    name = models.CharField('nom', max_length=100)
    active = models.BooleanField(default=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['device_type', 'name'],
                                               name='uniq_fault_per_type')]

    def __str__(self):
        return f'{self.name} ({self.device_type})'


class Part(models.Model):
    """Catalogue des pièces."""

    reference = models.CharField('référence', max_length=60, unique=True)
    name = models.CharField('nom', max_length=100)
    manufacturer = models.CharField('fabricant', max_length=100, blank=True)
    device_types = models.ManyToManyField(DeviceType, blank=True, related_name='parts')
    active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.reference} · {self.name}'


# --- Étapes du dossier ------------------------------------------------------

class Disinfection(models.Model):
    dossier = models.OneToOneField(DossierSAV, on_delete=models.PROTECT, related_name='disinfection')
    technician = models.ForeignKey(User, on_delete=models.PROTECT, related_name='+')
    product = models.CharField('produit / méthode', max_length=150, blank=True)
    validated = models.BooleanField(default=False)
    comment = models.TextField(blank=True)
    at = models.DateTimeField(auto_now_add=True)


class Diagnosis(models.Model):
    dossier = models.OneToOneField(DossierSAV, on_delete=models.PROTECT, related_name='diagnosis')
    technician = models.ForeignKey(User, on_delete=models.PROTECT, related_name='+')
    comment = models.TextField(blank=True)
    at = models.DateTimeField(auto_now_add=True)


class DetectedFault(models.Model):
    class Severity(models.TextChoices):
        MINEURE = 'MINEURE', 'Mineure'
        MAJEURE = 'MAJEURE', 'Majeure'
        CRITIQUE = 'CRITIQUE', 'Critique'

    diagnosis = models.ForeignKey(Diagnosis, on_delete=models.CASCADE, related_name='faults')
    fault = models.ForeignKey(Fault, on_delete=models.PROTECT, related_name='+')
    severity = models.CharField(max_length=10, choices=Severity.choices, default=Severity.MAJEURE)
    comment = models.CharField(max_length=300, blank=True)


class Repair(models.Model):
    dossier = models.OneToOneField(DossierSAV, on_delete=models.PROTECT, related_name='repair')
    technician = models.ForeignKey(User, on_delete=models.PROTECT, related_name='+')
    started_at = models.DateTimeField()
    ended_at = models.DateTimeField()
    tests = models.TextField('tests effectués', blank=True)
    parts_exit_document = models.CharField('document de sortie pièces (PR)', max_length=60, blank=True)
    comment = models.TextField(blank=True)

    @property
    def duration_minutes(self):
        return int((self.ended_at - self.started_at).total_seconds() // 60)


class ReplacedPart(models.Model):
    repair = models.ForeignKey(Repair, on_delete=models.CASCADE, related_name='parts')
    part = models.ForeignKey(Part, on_delete=models.PROTECT, related_name='+')
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])


QC_CHECKLIST = ['Fonctionnement', 'Alarmes', 'Débit', 'Pression', 'Batterie', 'Affichage', 'Nettoyage']


class QualityControl(models.Model):
    """Plusieurs contrôles possibles par dossier (échec puis nouveau contrôle)."""

    class Result(models.TextChoices):
        CONFORME = 'CONFORME', 'Conforme'
        NON_CONFORME = 'NON_CONFORME', 'Non conforme'

    dossier = models.ForeignKey(DossierSAV, on_delete=models.PROTECT, related_name='quality_controls')
    technician = models.ForeignKey(User, on_delete=models.PROTECT, related_name='+')
    checklist = models.JSONField(default=dict)
    result = models.CharField(max_length=15, choices=Result.choices)
    purity = models.DecimalField('pureté O₂ (%)', max_digits=4, decimal_places=1, null=True, blank=True,
                                 validators=[MinValueValidator(0), MaxValueValidator(100)])
    flow_pressure = models.CharField('débit / pression', max_length=50, blank=True)
    audible_alarm_ok = models.BooleanField('alarme sonore conforme', null=True, blank=True)
    comment = models.TextField(blank=True)
    at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['at', 'id']


class StockMovement(models.Model):
    class Kind(models.TextChoices):
        ENTREE = 'ENTREE', 'Entrée'
        SORTIE = 'SORTIE', 'Sortie'

    device = models.ForeignKey(Device, on_delete=models.PROTECT, related_name='stock_movements')
    dossier = models.ForeignKey(DossierSAV, on_delete=models.PROTECT, related_name='stock_movements')
    kind = models.CharField(max_length=6, choices=Kind.choices)
    location = models.CharField('emplacement', max_length=100, blank=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='+')
    at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['at', 'id']
        constraints = [
            models.UniqueConstraint(fields=['dossier', 'kind'], name='one_movement_kind_per_dossier'),
        ]


class Delivery(models.Model):
    dossier = models.OneToOneField(DossierSAV, on_delete=models.PROTECT, related_name='delivery')
    recipient = models.CharField('destinataire', max_length=150)
    delivery_note = models.CharField('bon de livraison', max_length=60, blank=True)
    delivered_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='+')
    comment = models.TextField(blank=True)
    at = models.DateTimeField(auto_now_add=True)


class Photo(models.Model):
    class Kind(models.TextChoices):
        RECEPTION = 'RECEPTION', 'Réception'
        DIAGNOSTIC = 'DIAGNOSTIC', 'Diagnostic'
        REPARATION = 'REPARATION', 'Réparation'
        AUTRE = 'AUTRE', 'Autre'

    dossier = models.ForeignKey(DossierSAV, on_delete=models.PROTECT, related_name='photos')
    kind = models.CharField(max_length=12, choices=Kind.choices, default=Kind.AUTRE)
    image = models.ImageField(upload_to='photos/%Y/%m/')
    uploaded_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='+')
    at = models.DateTimeField(auto_now_add=True)
