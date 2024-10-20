from datetime import date

from django.apps import apps
from django.conf import settings
from django.db import models
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from book.models import Book


class Borrowing(models.Model):
    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(null=True, blank=True)
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="borrowings",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="borrowings",
    )

    def __str__(self) -> str:
        return (
            f"Book: {self.book.title}, Author: {self.book.author}. "
            f"Borrowed from {self.borrow_date} to {self.expected_return_date}."
        )

    def clean(self):
        super().clean()

        if self.expected_return_date and self.expected_return_date < self.borrow_date:
            raise ValidationError(
                "Expected return date cannot be set up earlier than the borrow date."
            )

        if self.actual_return_date and self.actual_return_date < self.borrow_date:
            raise ValidationError(
                "Expected return date cannot be earlier than the borrow date."
            )

        if self.book.inventory <= 0:
            raise ValidationError(
                f"The book '{self.book.title}' is not available for borrowing."
            )

    def save(self, *args, **kwargs):
        if not self.borrow_date:
            self.borrow_date = date.today()

        self.full_clean()
        super().save(*args, **kwargs)

    def return_borrowing(self):
        if self.actual_return_date is not None:
            raise ValidationError("The book is already returned.")

        self.actual_return_date = timezone.now().date()
        self.book.inventory += 1
        self.save()

        if self.actual_return_date > self.expected_return_date:
            overdue_days = (self.actual_return_date - self.expected_return_date).days
            fine_amount = overdue_days * self.book.daily_fee * 2

            payment = apps.get_model("payment", "Payment")
            payment.objects.create(
                borrowing=self,
                money_to_pay=fine_amount,
                status="PENDING",
                type="FINE",
            )
