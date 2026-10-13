from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from rest_framework.test import APITestCase

from accounts.models import User
from inventory.models import DeviceType

from .models import QC_CHECKLIST, DossierSAV, Fault, Part, StatusHistory

PWD = 'Str0ng-Test-Pass!'
T0 = '2026-01-10T08:00:00Z'
T1 = '2026-01-10T09:30:00Z'
ALL_OK = {i: True for i in QC_CHECKLIST}


class Base(APITestCase):
    def setUp(self):
        self.tech = User.objects.create_user('tech@example.test', PWD)
        self.resp = User.objects.create_user('resp@example.test', PWD, role=User.Role.RESPONSABLE_SAV)
        self.type = DeviceType.objects.create(name='Concentrateur O2')
        self.other_type = DeviceType.objects.create(name='VNI')
        self.fault = Fault.objects.create(device_type=self.type, name='Compresseur')
        self.other_fault = Fault.objects.create(device_type=self.other_type, name='Turbine')
        self.part = Part.objects.create(reference='DEMO-001', name='Pièce démo')
        self.client.force_authenticate(self.tech)

    def reception(self, serial='sn 001', **extra):
        return self.client.post('/api/dossiers/reception/',
                                {'serial_number': serial, 'device_type': self.type.id, **extra})

    def post(self, did, action, data=None):
        return self.client.post(f'/api/dossiers/{did}/{action}/', data or {}, format='json')

    def go(self, did, to, comment=''):
        return self.post(did, 'transition', {'to_status': to, 'comment': comment})

    def full_cycle(self, serial='sn 001'):
        d = self.reception(serial).data
        i = d['id']
        steps = [
            ('disinfection', {'product': 'Démo'}),
            ('diagnosis', {'faults': [{'fault': self.fault.id, 'severity': 'MAJEURE'}]}),
            ('repair', {'started_at': T0, 'ended_at': T1,
                        'parts': [{'part': self.part.id, 'quantity': 2}]}),
            ('quality-control', {'checklist': ALL_OK}),
            ('stock-entry', {'location': 'A-01'}),
            ('delivery', {'recipient': 'Client démo'}),
        ]
        for action, data in steps:
            r = self.post(i, action, data)
            self.assertEqual(r.status_code, 200, (action, r.data))
        return d


class ReceptionAndTransitionTests(Base):
    def test_reception_creates_device_and_history(self):
        r = self.reception()
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.data['device']['serial_number'], 'SN001')
        self.assertTrue(r.data['device']['internal_code'].startswith('APP-'))
        self.assertEqual(StatusHistory.objects.filter(dossier_id=r.data['id']).count(), 1)

    def test_open_dossier_blocks_duplicate_reception(self):
        self.reception()
        self.assertEqual(self.reception('SN001').status_code, 400)

    def test_cannot_skip_steps(self):
        d = self.reception().data
        self.assertEqual(self.go(d['id'], 'EN_STOCK').status_code, 400)
        self.assertEqual(DossierSAV.objects.get(pk=d['id']).status, 'RECU')

    def test_manual_forward_requires_prerequisite_record(self):
        d = self.reception().data
        r = self.go(d['id'], 'DESINFECTE')
        self.assertEqual(r.status_code, 400)

    def test_technicien_cannot_go_back(self):
        d = self.reception().data
        self.post(d['id'], 'disinfection')
        self.assertEqual(self.go(d['id'], 'RECU', 'erreur').status_code, 400)

    def test_responsable_back_requires_comment(self):
        d = self.reception().data
        self.post(d['id'], 'disinfection')
        self.client.force_authenticate(self.resp)
        self.assertEqual(self.go(d['id'], 'RECU').status_code, 400)
        self.assertEqual(self.go(d['id'], 'RECU', 'saisie erronée').status_code, 200)

    def test_history_is_immutable(self):
        d = self.reception().data
        h = StatusHistory.objects.get(dossier_id=d['id'])
        with self.assertRaises(ValueError):
            h.delete()
        h.comment = 'x'
        with self.assertRaises(ValueError):
            h.save()

    def test_status_not_writable_via_api(self):
        d = self.reception().data
        self.assertEqual(self.client.patch(f"/api/dossiers/{d['id']}/", {'status': 'LIVRE'}).status_code, 405)

    def test_catalog_write_restricted(self):
        self.assertEqual(self.client.post('/api/brands/', {'name': 'X'}).status_code, 403)
        self.assertEqual(self.client.post('/api/faults/', {'device_type': self.type.id, 'name': 'Y'}).status_code, 403)
        self.client.force_authenticate(self.resp)
        self.assertEqual(self.client.post('/api/faults/', {'device_type': self.type.id, 'name': 'Y'}).status_code, 201)

    def test_requires_auth(self):
        self.client.force_authenticate(None)
        self.assertEqual(self.client.get('/api/dossiers/').status_code, 401)


class StepTests(Base):
    def test_full_cycle_and_life_sheet(self):
        d = self.full_cycle()
        self.assertEqual(DossierSAV.objects.get(pk=d['id']).status, 'LIVRE')
        sheet = self.client.get(f"/api/devices/{d['device']['id']}/life-sheet/").data
        doss = sheet['dossiers'][0]
        self.assertEqual(doss['repair']['duration_minutes'], 90)
        self.assertEqual(doss['repair']['parts'][0]['quantity'], 2)
        self.assertEqual(doss['diagnosis']['faults'][0]['name'], 'Compresseur')
        self.assertEqual(doss['delivery']['recipient'], 'Client démo')
        self.assertEqual([m['kind'] for m in doss['stock_movements']], ['ENTREE', 'SORTIE'])
        self.assertEqual(len(sheet['timeline']), 7)

    def test_returning_device_reuses_same_device(self):
        d = self.full_cycle()
        d2 = self.reception('sn001').data
        self.assertEqual(d2['device']['id'], d['device']['id'])
        sheet = self.client.get(f"/api/devices/{d['device']['id']}/life-sheet/").data
        self.assertEqual(len(sheet['dossiers']), 2)

    def test_step_out_of_order_rejected(self):
        d = self.reception().data
        r = self.post(d['id'], 'diagnosis', {'faults': []})
        self.assertEqual(r.status_code, 400)
        r = self.post(d['id'], 'delivery', {'recipient': 'X'})
        self.assertEqual(r.status_code, 400)

    def test_step_cannot_be_repeated(self):
        d = self.reception().data
        self.post(d['id'], 'disinfection')
        self.assertEqual(self.post(d['id'], 'disinfection').status_code, 400)

    def test_unvalidated_disinfection_rejected(self):
        d = self.reception().data
        self.assertEqual(self.post(d['id'], 'disinfection', {'validated': False}).status_code, 400)

    def test_fault_must_match_device_type(self):
        d = self.reception().data
        self.post(d['id'], 'disinfection')
        r = self.post(d['id'], 'diagnosis', {'faults': [{'fault': self.other_fault.id}]})
        self.assertEqual(r.status_code, 400)
        self.assertEqual(DossierSAV.objects.get(pk=d['id']).status, 'DESINFECTE')

    def test_repair_end_before_start_rejected(self):
        d = self.reception().data
        self.post(d['id'], 'disinfection')
        self.post(d['id'], 'diagnosis', {'faults': []})
        r = self.post(d['id'], 'repair', {'started_at': T1, 'ended_at': T0})
        self.assertEqual(r.status_code, 400)

    def test_failed_qc_blocks_stock_and_requires_comment(self):
        d = self.reception().data
        i = d['id']
        self.post(i, 'disinfection')
        self.post(i, 'diagnosis', {'faults': []})
        self.post(i, 'repair', {'started_at': T0, 'ended_at': T1})
        bad = {**ALL_OK, 'Débit': False}
        self.assertEqual(self.post(i, 'quality-control', {'checklist': bad}).status_code, 400)
        r = self.post(i, 'quality-control', {'checklist': bad, 'comment': 'Débit insuffisant'})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['status'], 'REPARE')
        self.assertEqual(self.post(i, 'stock-entry', {'location': 'A'}).status_code, 400)
        self.assertEqual(self.go(i, 'QC_VALIDE').status_code, 400)
        r = self.post(i, 'quality-control', {'checklist': ALL_OK})
        self.assertEqual(r.data['status'], 'QC_VALIDE')
        self.assertEqual(len(r.data['quality_controls']), 2)

    def test_incomplete_qc_checklist_rejected(self):
        d = self.reception().data
        i = d['id']
        self.post(i, 'disinfection')
        self.post(i, 'diagnosis', {'faults': []})
        self.post(i, 'repair', {'started_at': T0, 'ended_at': T1})
        self.assertEqual(self.post(i, 'quality-control', {'checklist': {'Débit': True}}).status_code, 400)

    def test_cannot_deliver_without_stock_entry(self):
        d = self.reception().data
        self.assertEqual(self.post(d['id'], 'delivery', {'recipient': 'X'}).status_code, 400)

    def test_delivered_dossier_cannot_be_reopened(self):
        d = self.full_cycle()
        self.client.force_authenticate(self.resp)
        self.assertEqual(self.go(d['id'], 'EN_STOCK', 'test').status_code, 400)


class PhotoTests(Base):
    def _img(self, name='a.png', fmt='PNG', ctype='image/png'):
        buf = BytesIO()
        Image.new('RGB', (10, 10)).save(buf, fmt)
        return SimpleUploadedFile(name, buf.getvalue(), content_type=ctype)

    def test_valid_photo_uploaded(self):
        d = self.reception().data
        r = self.client.post(f"/api/dossiers/{d['id']}/photos/",
                            {'image': self._img(), 'kind': 'RECEPTION'}, format='multipart')
        self.assertEqual(r.status_code, 201, r.data)

    def test_non_image_rejected(self):
        d = self.reception().data
        f = SimpleUploadedFile('x.png', b'not an image', content_type='image/png')
        r = self.client.post(f"/api/dossiers/{d['id']}/photos/", {'image': f}, format='multipart')
        self.assertEqual(r.status_code, 400)

    def test_wrong_content_type_rejected(self):
        d = self.reception().data
        f = self._img('a.gif', 'GIF', 'image/gif')
        r = self.client.post(f"/api/dossiers/{d['id']}/photos/", {'image': f}, format='multipart')
        self.assertEqual(r.status_code, 400)


class DashboardReportTests(Base):
    def test_dashboard_counts(self):
        self.full_cycle('s1')
        self.reception('s2')
        r = self.client.get('/api/dashboard/').data
        self.assertEqual(r['by_status']['LIVRE'], 1)
        self.assertEqual(r['by_status']['RECU'], 1)
        self.assertEqual(r['open_dossiers'], 1)
        self.assertEqual(r['avg_repair_minutes'], 90)
        self.assertEqual(r['top_faults'][0]['name'], 'Compresseur')

    def test_report_reserved_to_responsable(self):
        self.reception()
        self.assertEqual(self.client.get('/api/reports/dossiers.csv').status_code, 403)
        self.client.force_authenticate(self.resp)
        r = self.client.get('/api/reports/dossiers.csv')
        self.assertEqual(r.status_code, 200)
        self.assertIn('SN001', r.content.decode('utf-8-sig'))
