from rest_framework.test import APITestCase

from .models import User

PWD = 'Str0ng-Test-Pass!'


class AuthTests(APITestCase):
    def setUp(self):
        self.tech = User.objects.create_user('tech@example.test', PWD, role=User.Role.TECHNICIEN)
        self.resp = User.objects.create_user('resp@example.test', PWD, role=User.Role.RESPONSABLE_SAV)

    def _login(self, email):
        r = self.client.post('/api/auth/login/', {'email': email, 'password': PWD})
        self.assertEqual(r.status_code, 200)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + r.data['access'])

    def test_login_wrong_password(self):
        r = self.client.post('/api/auth/login/', {'email': 'tech@example.test', 'password': 'x'})
        self.assertEqual(r.status_code, 401)

    def test_me_requires_auth(self):
        self.assertEqual(self.client.get('/api/auth/me/').status_code, 401)

    def test_me_returns_profile_without_password(self):
        self._login('tech@example.test')
        r = self.client.get('/api/auth/me/')
        self.assertEqual(r.data['role'], 'TECHNICIEN')
        self.assertNotIn('password', r.data)

    def test_technicien_cannot_list_users(self):
        self._login('tech@example.test')
        self.assertEqual(self.client.get('/api/users/').status_code, 403)

    def test_responsable_can_create_user(self):
        self._login('resp@example.test')
        r = self.client.post('/api/users/', {'email': 'new@example.test', 'password': PWD,
                                             'first_name': 'A', 'last_name': 'B'})
        self.assertEqual(r.status_code, 201)
        self.assertTrue(User.objects.get(email='new@example.test').check_password(PWD))

    def test_weak_password_rejected(self):
        self._login('resp@example.test')
        r = self.client.post('/api/users/', {'email': 'w@example.test', 'password': '123'})
        self.assertEqual(r.status_code, 400)

    def test_duplicate_email_rejected(self):
        self._login('resp@example.test')
        r = self.client.post('/api/users/', {'email': 'tech@example.test', 'password': PWD})
        self.assertEqual(r.status_code, 400)
