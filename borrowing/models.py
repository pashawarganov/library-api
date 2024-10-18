from datetime import date

from django.conf import settings
from django.db import models
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
        if not self.borrow_date:
            self.borrow_date = date.today()

        if self.expected_return_date and self.expected_return_date < self.borrow_date:
            raise ValidationError(
                "Expected return date cannot be set up earlier than the borrow date."
            )

        if self.actual_return_date and self.actual_return_date < self.borrow_date:
            raise ValidationError(
                "Expected return date cannot be earlier than the borrow date."
            )

        if self.book.inventory == 0:
            raise ValidationError(
                f"The book '{self.book.title}' is not available for borrowing."
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
