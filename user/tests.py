from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from user.models import User


class UserModelTest(TestCase):
    def test_create_user_with_email(self):
        User = get_user_model()
        user = User.objects.create_user(
            email="test@example.com", password="password123"
        )
        self.assertEqual(user.email, "test@example.com")
        self.assertTrue(user.is_active)
        self.assertTrue(user.check_password("password123"))

    def test_create_superuser(self):
        User = get_user_model()
        superuser = User.objects.create_superuser(
            email="admin@example.com", password="adminpass"
        )
        self.assertEqual(superuser.email, "admin@example.com")
        self.assertTrue(superuser.is_active)
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)

    def test_create_user_without_email_raises_error(self):
        User = get_user_model()
        with self.assertRaises(ValueError):
            User.objects.create_user(email="", password="password123")


class UserManagerTest(TestCase):
    def test_create_user_with_manager(self):
        user = User.objects.create_user(
            email="manager@example.com", password="password123"
        )
        self.assertEqual(user.email, "manager@example.com")
        self.assertTrue(user.check_password("password123"))

    def test_create_superuser_with_manager(self):
        superuser = User.objects.create_superuser(
            email="superuser@example.com", password="superpass"
        )
        self.assertEqual(superuser.email, "superuser@example.com")
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)

    def test_create_user_without_email_raises_value_error(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(email="", password="password123")


class ManageUserViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="testuser@example.com", password="password123"
        )

    def test_manage_user_view_authenticated(self):
        response = self.client.post(
            reverse("user:token_obtain_pair"),
            {"email": "testuser@example.com", "password": "password123"},
        )
        token = response.data["access"]

        self.client.credentials(HTTP_AUTHORIZE="Bearer " + token)
        response = self.client.get(reverse("user:manage"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "testuser@example.com")

    def test_manage_user_view_unauthenticated(self):
        response = self.client.get(reverse("user:manage"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
