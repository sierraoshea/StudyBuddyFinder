from django.test import TestCase, Client
from django.urls import reverse
from allauth.account.models import EmailAddress
from django.contrib.auth.models import User
from .models import UserClasses

def create_user(username):
    user = User.objects.create(username=username)
    user.set_password('test')
    user.save()

    return user

class GoogleLoginTests(TestCase):
    def test_is_not_logged_in(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Login with Google")


    def test_logged_in(self):
        user = create_user("test")

        self.client.login(username='test', password='test')
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Current Classes")


def create_class(usr, subj, cat_num, comp, sect, prof):
    return UserClasses.objects.create(user=usr,subject=subj, catalog_number=cat_num, component=comp, section=sect, professor=prof)

class ProfileViewTests(TestCase):

    def test_no_classes(self):
        user = create_user("test")

        self.client.login(username='test', password='test')
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "You have no classes added to your profile.")

    def test_one_class_added(self):
        user = create_user("test")

        self.client.login(username='test', password='test')
        response = self.client.get(reverse('profile'))
        create_class(response.wsgi_request.user, "CS", 3100, "LEC", 2, "Mark Floryan")
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "CS 3100 LEC Section 2 w/ Mark Floryan")

    def test_multiple_classes(self):
        user = create_user("test")
        self.client.login(username='test', password='test')
        response = self.client.get(reverse('profile'))
        create_class(response.wsgi_request.user, "CS", 3100, "LEC", 2, "Mark Floryan")
        create_class(response.wsgi_request.user, "CS", 3240, "LEC", 1, "Paul McBurney")
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "CS 3100 LEC Section 2 w/ Mark Floryan")
        self.assertContains(response, "CS 3240 LEC Section 1 w/ Paul McBurney")

class IndexViewTests(TestCase):
    def test_no_classes(self):
        user = create_user("test")
        self.client.login(username='test', password='test')
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "You have no classes added to your profile.")
        self.assertContains(response, "You are not currently available for any classes.")
        self.assertContains(response, "You currently have no upcoming meetings")

    def test_one_class_unavailble(self):
        user = create_user("test")

        self.client.login(username='test', password='test')
        response = self.client.get(reverse('index'))
        create_class(response.wsgi_request.user, "CS", 3100, "LEC", 2, "Mark Floryan")
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "CS 3100 LEC Section 2 w/ Mark Floryan")
        self.assertContains(response, "You are not currently available for any classes.")

    def test_one_class_available(self):
        user = create_user("test")

        self.client.login(username='test', password='test')
        response = self.client.get(reverse('index'))
        c = create_class(response.wsgi_request.user, "CS", 3100, "LEC", 2, "Mark Floryan")
        self.client.post('/update', data={"class_to_update": [c.id]})
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "CS 3100 LEC Section 2 w/ Mark Floryan")
        self.assertNotContains(response, "You are not currently available for any classes.")

