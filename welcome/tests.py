from django.test import TestCase
from django.urls import reverse
from allauth.account.models import EmailAddress
from django.contrib.auth.models import User

class GoogleLoginTests(TestCase):
    def test_is_not_logged_in(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Login with Google")

