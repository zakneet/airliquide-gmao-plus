from rest_framework.test import APITestCase

from accounts.models import User
from inventory.models import DeviceType

from .models import DossierSAV, StatusHistory

PWD = 'Str0ng-Test-Pass!'


class WorkflowTests(APITestCase):
    def setUp(self):
        self.tech = User.objects.create_user('tech@example.test', PWD)
        self.resp = User.objects.create_user('resp@example.test', PWD, role=User.Role.RESPONSABLE_SAV)
        self.type = DeviceType.objects.create(name='Concentrateur O2')
        self.client.force_authenticate(self.tech)

    def reception(self, serial='sn 001'):
        return self.client.post('/api/dossiers/reception/',
                                {'serial_number': serial, 'device_type': self.type.id})

    def go(self, dossier_id, to, comment=''):
        return self.client.post(f'/api/dossiers/{dossier_id}/transition/',
                                {'to_status': to, 'comment': comment})

    def test_reception_creates_device_and_history(self):
        r = self.reception()
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.data['device']['serial_number'], 'SN001')
        self.assertTrue(r.data['device']['internal_code'].startswith('APP-'))
        self.assertEqual(StatusHistory.objects.filter(dossier_id=r.data['id']).count(), 1)

    def test_open_dossier_blocks_duplicate_reception(self):
        self.reception()
        self.assertEqual(self.reception('SN001').status_code, 400)

    def test_returning_device_reuses_same_device(self):
        d = self.reception().data
        for s in ['DESINFECTE', 'DIAGNOSTIC_TERMINE', 'REPARE', 'QC_VALIDE', 'EN_STOCK', 'LIVRE']:
            self.assertEqual(self.go(d['id'], s).status_code, 200, s)
        d2 = self.reception('sn001').data
        self.assertEqual(d2['device']['id'], d['device']['id'])
        self.assertNotEqual(d2['id'], d['id'])
        sheet = self.client.get(f"/api/devices/{d['device']['id']}/life-sheet/").data
        self.assertEqual(len(sheet['dossiers']), 2)
        self.assertEqual(len(sheet['timeline']), 8)

    def test_cannot_skip_steps(self):
        d = self.reception().data
        self.assertEqual(self.go(d['id'], 'EN_STOCK').status_code, 400)
        self.assertEqual(DossierSAV.objects.get(pk=d['id']).status, 'RECU')

    def test_technicien_cannot_go_back(self):
        d = self.reception().data
        self.go(d['id'], 'DESINFECTE')
        self.assertEqual(self.go(d['id'], 'RECU', 'erreur').status_code, 400)

    def test_responsable_back_requires_comment(self):
        d = self.reception().data
        self.go(d['id'], 'DESINFECTE')
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
        r = self.client.patch(f"/api/dossiers/{d['id']}/", {'status': 'LIVRE'})
        self.assertEqual(r.status_code, 405)

    def test_catalog_write_restricted(self):
        self.assertEqual(self.client.post('/api/brands/', {'name': 'X'}).status_code, 403)
        self.client.force_authenticate(self.resp)
        self.assertEqual(self.client.post('/api/brands/', {'name': 'X'}).status_code, 201)

    def test_requires_auth(self):
        self.client.force_authenticate(None)
        self.assertEqual(self.client.get('/api/dossiers/').status_code, 401)
