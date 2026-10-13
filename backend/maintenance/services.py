from django.db import transaction
from rest_framework.exceptions import ValidationError

from accounts.models import User
from inventory.models import Device

from .models import DossierSAV, StatusHistory

ORDER = [s.value for s in DossierSAV.Status]


@transaction.atomic
def receive_device(*, user, serial_number, device_type, model=None, **dossier_fields):
    """Réception : retrouve l'appareil par n° de série (ou le crée) et ouvre un dossier SAV."""
    serial = Device.normalize_serial(serial_number)
    device, created = Device.objects.get_or_create(
        serial_number=serial,
        defaults={'device_type': device_type, 'model': model, 'created_by': user},
    )
    if not created and device.dossiers.exclude(status=DossierSAV.Status.LIVRE).exists():
        raise ValidationError({'serial_number': 'Cet appareil a déjà un dossier SAV ouvert.'})
    dossier = DossierSAV.objects.create(device=device, received_by=user, **dossier_fields)
    StatusHistory.objects.create(dossier=dossier, from_status='', to_status=dossier.status,
                                 user=user, comment='Réception')
    return dossier


@transaction.atomic
def change_status(dossier, to_status, user, comment=''):
    """Applique une transition valide. Avance d'une étape ; recul réservé au Responsable SAV."""
    dossier = DossierSAV.objects.select_for_update().get(pk=dossier.pk)
    if to_status not in ORDER:
        raise ValidationError({'to_status': 'Statut inconnu.'})
    delta = ORDER.index(to_status) - ORDER.index(dossier.status)
    if delta == 1:
        pass
    elif delta == -1:
        if user.role != User.Role.RESPONSABLE_SAV:
            raise ValidationError({'to_status': 'Le retour en arrière requiert un Responsable SAV.'})
        if not comment.strip():
            raise ValidationError({'comment': 'Un commentaire est obligatoire pour un retour en arrière.'})
        if dossier.status == DossierSAV.Status.LIVRE:
            raise ValidationError({'to_status': 'Un dossier livré ne peut pas être rouvert.'})
    else:
        raise ValidationError({'to_status': f'Transition {dossier.status} vers {to_status} interdite.'})
    old = dossier.status
    dossier.status = to_status
    dossier.save(update_fields=['status'])
    StatusHistory.objects.create(dossier=dossier, from_status=old, to_status=to_status,
                                 user=user, comment=comment)
    return dossier
