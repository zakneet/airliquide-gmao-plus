from django.db import transaction
from rest_framework.exceptions import ValidationError

from accounts.models import User
from inventory.models import Device

from .models import (QC_CHECKLIST, BiohazardStatus, VisualCondition, DetectedFault, Delivery, Diagnosis, Disinfection, DossierSAV,
                     QualityControl, Repair, ReplacedPart, StatusHistory, StockMovement)

S = DossierSAV.Status
ORDER = [s.value for s in S]


def _fail(field, msg):
    raise ValidationError({field: msg})


def _check_prerequisite(dossier, to_status):
    """Règles métier : on ne franchit une étape que si ses données obligatoires existent."""
    if to_status == S.DESINFECTE:
        d = getattr(dossier, 'disinfection', None)
        if not (d and d.validated):
            _fail('to_status', 'Désinfection validée requise.')
    elif to_status == S.DIAGNOSTIC_TERMINE:
        if not hasattr(dossier, 'diagnosis'):
            _fail('to_status', 'Diagnostic requis.')
    elif to_status == S.REPARE:
        if not hasattr(dossier, 'repair'):
            _fail('to_status', 'Réparation enregistrée requise.')
    elif to_status == S.QC_VALIDE:
        last = dossier.quality_controls.last()
        if not (last and last.result == QualityControl.Result.CONFORME):
            _fail('to_status', 'Contrôle qualité conforme requis.')
    elif to_status == S.EN_STOCK:
        if not dossier.stock_movements.filter(kind=StockMovement.Kind.ENTREE).exists():
            _fail('to_status', "Entrée en stock requise.")
    elif to_status == S.LIVRE:
        if not hasattr(dossier, 'delivery'):
            _fail('to_status', 'Livraison enregistrée requise.')


@transaction.atomic
def receive_device(*, user, serial_number, device_type, model=None, return_declaration=None,
                   **dossier_fields):
    """Réception : retrouve l'appareil par n° de série (ou le crée) et ouvre un dossier SAV.

    Si un questionnaire de retour est fourni, il doit correspondre au numéro de série et ne
    pas avoir déjà été reçu ; il est alors rattaché au dossier.
    """
    serial = Device.normalize_serial(serial_number)
    if return_declaration is not None:
        if Device.normalize_serial(return_declaration.serial_number) != serial:
            _fail('return_declaration', 'Le numéro de série ne correspond pas au questionnaire de retour.')
        if DossierSAV.objects.filter(return_declaration=return_declaration).exists():
            _fail('return_declaration', 'Ce retour a déjà été réceptionné.')
        dossier_fields['return_declaration'] = return_declaration
    device, created = Device.objects.get_or_create(
        serial_number=serial,
        defaults={'device_type': device_type, 'model': model, 'created_by': user},
    )
    if not created and device.dossiers.exclude(status=S.LIVRE).exists():
        _fail('serial_number', 'Cet appareil a déjà un dossier SAV ouvert.')
    # Le risque biologique est déduit des réponses : « Inconnu » est traité comme un risque.
    dossier_fields['biohazard'] = (
        dossier_fields.get('biohazard', False)
        or dossier_fields.get('biohazard_status', BiohazardStatus.UNKNOWN) != BiohazardStatus.NORMAL
        or dossier_fields.get('visual_condition') == VisualCondition.BIOHAZARD
    )
    dossier = DossierSAV.objects.create(device=device, received_by=user, **dossier_fields)
    StatusHistory.objects.create(dossier=dossier, from_status='', to_status=dossier.status,
                                 user=user, comment='Réception')
    return dossier


def _lock(dossier):
    return DossierSAV.objects.select_for_update().get(pk=dossier.pk)


def _advance(dossier, to_status, user, comment=''):
    old = dossier.status
    dossier.status = to_status
    dossier.save(update_fields=['status'])
    StatusHistory.objects.create(dossier=dossier, from_status=old, to_status=to_status,
                                 user=user, comment=comment)
    return dossier


@transaction.atomic
def change_status(dossier, to_status, user, comment=''):
    """Transition manuelle. Avance d'une étape (prérequis contrôlés) ; recul réservé au Responsable SAV."""
    dossier = _lock(dossier)
    if to_status not in ORDER:
        _fail('to_status', 'Statut inconnu.')
    delta = ORDER.index(to_status) - ORDER.index(dossier.status)
    if delta == 1:
        _check_prerequisite(dossier, to_status)
    elif delta == -1:
        if user.role != User.Role.RESPONSABLE_SAV:
            _fail('to_status', 'Le retour en arrière requiert un Responsable SAV.')
        if not comment.strip():
            _fail('comment', 'Un commentaire est obligatoire pour un retour en arrière.')
        if dossier.status == S.LIVRE:
            _fail('to_status', 'Un dossier livré ne peut pas être rouvert.')
    else:
        _fail('to_status', f'Transition {dossier.status} vers {to_status} interdite.')
    return _advance(dossier, to_status, user, comment)


def _require_status(dossier, expected, label):
    if dossier.status != expected:
        _fail('status', f'{label} possible uniquement au statut « {S(expected).label} » '
                        f'(statut actuel : « {dossier.get_status_display()} »).')


@transaction.atomic
def record_disinfection(dossier, user, *, product='', comment='', validated=True):
    dossier = _lock(dossier)
    _require_status(dossier, S.RECU, 'La désinfection')
    if not validated:
        _fail('validated', 'La désinfection doit être validée pour poursuivre.')
    Disinfection.objects.create(dossier=dossier, technician=user, product=product,
                                comment=comment, validated=True)
    return _advance(dossier, S.DESINFECTE, user, 'Désinfection validée')


@transaction.atomic
def record_diagnosis(dossier, user, *, faults, comment=''):
    dossier = _lock(dossier)
    _require_status(dossier, S.DESINFECTE, 'Le diagnostic')
    device_type = dossier.device.device_type_id
    diag = Diagnosis.objects.create(dossier=dossier, technician=user, comment=comment)
    seen = set()
    for f in faults:
        fault = f['fault']
        if fault.device_type_id != device_type:
            _fail('faults', f'« {fault.name} » ne correspond pas au type de cet appareil.')
        if fault.id in seen:
            _fail('faults', f'« {fault.name} » est renseignée deux fois.')
        seen.add(fault.id)
        DetectedFault.objects.create(diagnosis=diag, fault=fault,
                                     severity=f.get('severity', 'MAJEURE'),
                                     comment=f.get('comment', ''))
    return _advance(dossier, S.DIAGNOSTIC_TERMINE, user, 'Diagnostic terminé')


@transaction.atomic
def record_repair(dossier, user, *, started_at, ended_at, parts=(), tests='', comment='',
                  parts_exit_document=''):
    dossier = _lock(dossier)
    _require_status(dossier, S.DIAGNOSTIC_TERMINE, 'La réparation')
    if ended_at <= started_at:
        _fail('ended_at', 'La fin doit être postérieure au début.')
    repair = Repair.objects.create(dossier=dossier, technician=user, started_at=started_at,
                                   ended_at=ended_at, tests=tests, comment=comment,
                                   parts_exit_document=parts_exit_document)
    for p in parts:
        ReplacedPart.objects.create(repair=repair, part=p['part'], quantity=p.get('quantity', 1))
    return _advance(dossier, S.REPARE, user, 'Réparation terminée')


@transaction.atomic
def record_quality_control(dossier, user, *, checklist, comment='', purity=None, flow_pressure='',
                           audible_alarm_ok=None):
    dossier = _lock(dossier)
    _require_status(dossier, S.REPARE, 'Le contrôle qualité')
    unknown = set(checklist) - set(QC_CHECKLIST)
    missing = [i for i in QC_CHECKLIST if i not in checklist]
    if unknown or missing:
        _fail('checklist', f'Checklist invalide. Éléments attendus : {", ".join(QC_CHECKLIST)}.')
    ok = all(checklist[i] is True for i in QC_CHECKLIST)
    result = QualityControl.Result.CONFORME if ok else QualityControl.Result.NON_CONFORME
    if not ok and not comment.strip():
        _fail('comment', 'Un commentaire est obligatoire en cas de non-conformité.')
    QualityControl.objects.create(dossier=dossier, technician=user, checklist=checklist,
                                  result=result, comment=comment, purity=purity,
                                  flow_pressure=flow_pressure, audible_alarm_ok=audible_alarm_ok)
    if ok:
        return _advance(dossier, S.QC_VALIDE, user, 'Contrôle qualité conforme')
    StatusHistory.objects.create(dossier=dossier, from_status=dossier.status,
                                 to_status=dossier.status, user=user,
                                 comment=f'Contrôle qualité NON conforme : {comment}')
    return dossier


@transaction.atomic
def enter_stock(dossier, user, *, location):
    dossier = _lock(dossier)
    _require_status(dossier, S.QC_VALIDE, "L'entrée en stock")
    if not location.strip():
        _fail('location', 'Emplacement obligatoire.')
    StockMovement.objects.create(device=dossier.device, dossier=dossier, user=user,
                                 kind=StockMovement.Kind.ENTREE, location=location.strip())
    return _advance(dossier, S.EN_STOCK, user, f'Entrée en stock : {location.strip()}')


@transaction.atomic
def deliver(dossier, user, *, recipient, delivery_note='', comment=''):
    dossier = _lock(dossier)
    _require_status(dossier, S.EN_STOCK, 'La livraison')
    if not recipient.strip():
        _fail('recipient', 'Destinataire obligatoire.')
    Delivery.objects.create(dossier=dossier, recipient=recipient, delivery_note=delivery_note,
                            delivered_by=user, comment=comment)
    StockMovement.objects.create(device=dossier.device, dossier=dossier, user=user,
                                 kind=StockMovement.Kind.SORTIE)
    return _advance(dossier, S.LIVRE, user, f'Livré à {recipient}')
