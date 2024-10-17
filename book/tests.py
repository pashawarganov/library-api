from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from book.models import Book


class BookTests(APITestCase):
    def setUp(self):
        self.admin_user = get_user_model().objects.create_superuser(
            email="admin@admin.com", password="admin123"
        )
        self.user = get_user_model().objects.create_user(email="user@user.com", password="user123")
        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            cover="HARD",
            inventory=10,
            daily_fee=5.00,
        )

        response = self.client.post(
            reverse("user:token_obtain_pair"),
            {"email": "admin@admin.com", "password": "admin123"},
        )
        self.admin_token = response.data["access"]

        response = self.client.post(
            reverse("user:token_obtain_pair"),
            {"email": "user@user.com", "password": "user123"},
        )
        self.user_token = response.data["access"]

    def test_list_books(self):
        response = self.client.get(reverse("book:book-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_book_as_admin(self):
        self.client.credentials(HTTP_AUTHORIZE="Bearer " + self.admin_token)
        response = self.client.post(
            reverse("book:book-list"),
            {
                "title": "New Book",
                "author": "New Author",
                "cover": "SOFT",
                "inventory": 5,
                "daily_fee": 3.50,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_book_as_user(self):
        self.client.credentials(HTTP_AUTHORIZE="Bearer " + self.user_token)
        response = self.client.post(
            reverse("book:book-list"),
            {
                "title": "New Book",
                "author": "New Author",
                "cover": "SOFT",
                "inventory": 5,
                "daily_fee": 3.50,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_book_as_admin(self):
        self.client.credentials(HTTP_AUTHORIZE="Bearer " + self.admin_token)
        response = self.client.put(
            reverse("book:book-detail", args=[self.book.id]),
            {
                "title": "Updated Book",
                "author": "Updated Author",
                "cover": "SOFT",
                "inventory": 7,
                "daily_fee": 4.00,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.book.refresh_from_db()
        self.assertEqual(self.book.title, "Updated Book")

    def test_delete_book_as_admin(self):
        self.client.credentials(HTTP_AUTHORIZE="Bearer " + self.admin_token)
        response = self.client.delete(reverse("book:book-detail", args=[self.book.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Book.objects.filter(id=self.book.id).exists())
