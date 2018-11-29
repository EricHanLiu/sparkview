from django.test import TestCase, Client
from .models import MonthlyReport
from django.contrib.auth.models import User


class GetRequestTestCase(TestCase):

    client = None

    def setUp(self):
        self.credentials = {
            'username': 'abc',
            'password': 'abc'}
        User.objects.create_user(**self.credentials)
        # User.objects.create_superuser('abc', 'abc@abc.com', '1234')
        if self.client == None:
            self.client = Client()

    def test_can_view_home_page(self):
        r = self.client.get('/')
        self.assertEqual(r.status_code, 200)

    def test_can_login(self):
        response = self.client.post('/auth/login', self.credentials, follow=True)
        # should be logged in now
        print(response)
        # self.assertTrue(response.context['user'].is_active)
        # r = self.client.post('/auth/login', {'username' : 'abc', 'password' : '1234'})
        # self.assertEqual(r.status_code, 200)
