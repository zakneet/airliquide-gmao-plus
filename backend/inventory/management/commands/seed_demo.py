from django.core.management.base import BaseCommand

from accounts.models import User
from inventory.models import Brand, DeviceModel, DeviceType
from maintenance.models import Fault, Part

CO, VNI, CPAP = "Concentrateur d'oxygène", 'VNI', 'CPAP / Apnée'
# Exemples issus du workflow documenté ; catalogues à compléter par le Responsable SAV.
FAULTS = {
    CO: ['Compresseur', 'Carte O₂', 'Électrovanne', 'Tamis moléculaire', 'Débitmètre', 'Batterie'],
    VNI: ['Turbine', 'Carte mère', 'Batterie', 'Écran', 'Tactile', 'Ventilateur'],
    CPAP: ['Turbine', 'Carte mère', 'Batterie', 'Écran', 'Tactile', 'Ventilateur'],
}


class Command(BaseCommand):
    help = 'Charge des données de DÉMONSTRATION fictives (catalogues, 2 comptes).'

    def handle(self, *args, **opts):
        types = {n: DeviceType.objects.get_or_create(name=n)[0] for n in (CO, VNI, CPAP)}
        brand, _ = Brand.objects.get_or_create(name='DEMO-Marque')
        for t, name in [(CO, 'DEMO-CO-1'), (VNI, 'DEMO-VNI-1'), (CPAP, 'DEMO-CPAP-1')]:
            DeviceModel.objects.get_or_create(brand=brand, name=name, device_type=types[t])
        for t, names in FAULTS.items():
            for n in names:
                Fault.objects.get_or_create(device_type=types[t], name=n)
        for ref, name in [('DEMO-P-001', 'Pièce de démonstration A'), ('DEMO-P-002', 'Pièce de démonstration B')]:
            Part.objects.get_or_create(reference=ref, defaults={'name': name, 'manufacturer': 'DEMO'})
        for email, role in [('demo.tech@example.test', User.Role.TECHNICIEN),
                            ('demo.resp@example.test', User.Role.RESPONSABLE_SAV)]:
            if not User.objects.filter(email=email).exists():
                User.objects.create_user(email, 'ChangeMe-Demo-2026!', role=role,
                                         first_name='Demo', last_name=role.label)
        self.stdout.write(self.style.SUCCESS('Données de démonstration chargées.'))
