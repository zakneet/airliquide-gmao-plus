from django.core.management.base import BaseCommand

from accounts.models import User
from inventory.models import Brand, DeviceModel, DeviceType

TYPES = ['Concentrateur d\'oxygène', 'VNI', 'CPAP / Apnée']


class Command(BaseCommand):
    help = 'Charge des données de DÉMONSTRATION fictives (types, marque et modèles factices, 2 comptes).'

    def handle(self, *args, **opts):
        types = {n: DeviceType.objects.get_or_create(name=n)[0] for n in TYPES}
        brand, _ = Brand.objects.get_or_create(name='DEMO-Marque')
        for t, name in [(TYPES[0], 'DEMO-CO-1'), (TYPES[1], 'DEMO-VNI-1'), (TYPES[2], 'DEMO-CPAP-1')]:
            DeviceModel.objects.get_or_create(brand=brand, name=name, device_type=types[t])
        for email, role in [('demo.tech@example.test', User.Role.TECHNICIEN),
                            ('demo.resp@example.test', User.Role.RESPONSABLE_SAV)]:
            if not User.objects.filter(email=email).exists():
                User.objects.create_user(email, 'ChangeMe-Demo-2026!', role=role,
                                         first_name='Demo', last_name=role.label)
        self.stdout.write(self.style.SUCCESS('Données de démonstration chargées.'))
