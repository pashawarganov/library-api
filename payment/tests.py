from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from unittest.mock import patch
from borrowing.models import Borrowing
from book.models import Book
from payment.models import Payment
from datetime import timedelta
from django.utils import timezone


class PaymentTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = get_user_model().objects.create_user(
            email="testuser@example.com", password="password123"
        )
        self.client.force_authenticate(user=self.user)

        self.book = Book.objects.create(
            title="Test Book",
            author="Author Name",
            cover="HARD",
            inventory=5,
            daily_fee=5.00,
        )

        self.borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            expected_return_date=timezone.now() + timedelta(days=5),
        )

        self.payment_url = reverse("payment:payment-list")

    def test_create_payment(self):
        data = {"borrowing_id": self.borrowing.id, "money": 20.00}

        response = self.client.post(self.payment_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        payment = Payment.objects.get(borrowing_id=self.borrowing.id)
        self.assertEqual(payment.money_to_pay, 20.00)
        self.assertEqual(payment.status, "PENDING")
        self.assertEqual(payment.type, "PAYMENT")

    def test_create_fine_payment(self):
        self.borrowing.actual_return_date = timezone.now() + timedelta(days=10)
        self.borrowing.save()

        overdue_days = 10
        daily_fee = self.borrowing.book.daily_fee
        money_to_pay = overdue_days * daily_fee * 2

        data = {
            "borrowing_id": self.borrowing.id,
            "money": money_to_pay,
        }

        response = self.client.post(self.payment_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        payment = Payment.objects.get(borrowing_id=self.borrowing.id, type="FINE")
        self.assertEqual(payment.status, "PENDING")
        self.assertEqual(payment.type, "FINE")

    @patch("stripe.checkout.Session.create")
    @patch("stripe.checkout.Session.retrieve")
    def test_payment_success(self, mock_retrieve, mock_create):
        payment = Payment.objects.create(
            borrowing=self.borrowing,
            session_url="http://test.com/session",
            session_id="test_session_id",
            money_to_pay=15.00,
            status="PENDING",
            type="PAYMENT",
        )

        mock_create.return_value = type(
            "Session", (object,), {"id": "test_session_id", "payment_status": "paid"}
        )

        mock_retrieve.return_value = type(
            "Session", (object,), {"id": "test_session_id", "payment_status": "paid"}
        )

        success_url = reverse("payment:payment-success") + "?session_id=test_session_id"
        response = self.client.get(success_url)

        print(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        payment.refresh_from_db()
        self.assertEqual(payment.status, "PAID")

    def test_payment_cancel(self):
        cancel_url = reverse("payment:payment-cancel")
        response = self.client.get(cancel_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["message"],
            "Payment was cancelled. You can retry payment within 24 hours.",
        )
