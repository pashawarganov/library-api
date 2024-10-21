from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from book.models import Book
from borrowing.models import Borrowing
from payment.models import Payment


class TestBorrowingModel(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="testuser@example.com", password="password123"
        )
        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            cover="HARD",
            inventory=10,
            daily_fee=5.00,
        )

    def test_create_borrowing(self):
        borrowing = Borrowing.objects.create(
            book=self.book,
            user=self.user,
            expected_return_date=date.today() + timedelta(days=7),
        )

        self.assertEqual(borrowing.book, self.book)
        self.assertEqual(borrowing.user, self.user)
        self.assertIsNotNone(borrowing.borrow_date)
        self.assertEqual(borrowing.borrow_date, date.today())

    def test_raise_error_if_inventory_empty(self):
        self.book.inventory = 0
        self.book.save()

        with self.assertRaises(ValidationError):
            Borrowing.objects.create(
                book=self.book,
                user=self.user,
                expected_return_date=date.today() + timedelta(days=7),
            )


class TestBorrowingUnauthenticatedUser(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(reverse("borrowing:borrowing-list"))

        self.assertEqual(response.status_code, 401)


class TestBorrowingAuthenticatedUser(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="testuser@example.com", password="password123"
        )
        self.user_2 = get_user_model().objects.create_user(
            email="testuser2@example.com", password="password123"
        )
        self.client.force_authenticate(user=self.user)
        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            cover="HARD",
            inventory=10,
            daily_fee=5.00,
        )
        self.borrowing = Borrowing.objects.create(
            book=self.book,
            user=self.user,
            borrow_date=timezone.now().date(),
            expected_return_date=timezone.now().date() + timezone.timedelta(days=7),
        )
        self.borrowing = Borrowing.objects.create(
            book=self.book,
            user=self.user,
            borrow_date=timezone.now().date() - timezone.timedelta(days=5),
            expected_return_date=timezone.now().date() + timezone.timedelta(days=2),
            actual_return_date=timezone.now().date(),
        )
        self.borrowing = Borrowing.objects.create(
            book=self.book,
            user=self.user_2,
            borrow_date=timezone.now().date(),
            expected_return_date=timezone.now().date() + timezone.timedelta(days=7),
        )

    def test_list_borrowings(self):
        url = reverse("borrowing:borrowing-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_filter_by_user_if_staff(self):
        user_staff = get_user_model().objects.create_superuser(
            email="staff@example.com", password="password123"
        )
        self.client.force_authenticate(user=user_staff)
        url = reverse("borrowing:borrowing-list") + "?user_id={}".format(self.user.id)
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_filter_by_user_if_not_staff(self):
        url = reverse("borrowing:borrowing-list") + "?user_id={}".format(self.user_2.id)
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

        for borrowing in response.data:
            self.assertEqual(borrowing["user"], self.user.email)

    def test_filter_by_is_active_true(self):
        url = reverse("borrowing:borrowing-list") + "?is_active=true"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_filter_by_is_active_false(self):
        url = reverse("borrowing:borrowing-list") + "?is_active=false"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


class TestReturnBorrowing(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="testuser@example.com", password="password123"
        )
        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            cover="HARD",
            inventory=10,
            daily_fee=5.00,
        )
        self.borrowing_on_time = Borrowing.objects.create(
            book=self.book,
            user=self.user,
            expected_return_date=timezone.now().date() + timezone.timedelta(days=5),
        )
        self.borrowing_overdue = Borrowing.objects.create(
            book=self.book,
            user=self.user,
            expected_return_date=timezone.now().date() + timezone.timedelta(days=5),
        )
        self.client.force_authenticate(user=self.user)

    def test_return_borrowing(self):
        url = reverse(
            "borrowing:borrowing-return-book", kwargs={"pk": self.borrowing_on_time.id}
        )
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Book was successfully returned.", response.data["message"])
        self.borrowing_on_time.refresh_from_db()
        self.assertIsNotNone(self.borrowing_on_time.actual_return_date)
        self.assertFalse(
            Payment.objects.filter(borrowing_id=self.borrowing_on_time.id).exists()
        )
