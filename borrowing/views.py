from asgiref.sync import async_to_sync
from django.apps import apps
from django.db import transaction
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from borrowing.models import Borrowing
from borrowing.serializers import (
    BorrowingListSerializer,
    BorrowingDetailSerializer,
    BorrowingSerializer,
    BorrowingCreateSerializer,
    BorrowingReturnSerializer,
)
from telegram_bot import send_borrowing_notification


class BorrowingViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = Borrowing.objects.all()
        is_active = self.request.query_params.get("is_active")

        if self.request.user.is_staff:
            user_id = self.request.query_params.get("user_id", None)
            if user_id:
                queryset = queryset.filter(user_id=user_id)
        else:
            queryset = queryset.filter(user=self.request.user)

        if is_active:
            if is_active.lower() == "true":
                queryset = queryset.filter(actual_return_date__isnull=True)
            elif is_active.lower() == "false":
                queryset = queryset.exclude(actual_return_date__isnull=True)

        if self.action in ["list", "retrieve"]:
            queryset = queryset.select_related("book", "user")

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return BorrowingListSerializer
        elif self.action == "retrieve":
            return BorrowingDetailSerializer
        elif self.action == "create":
            return BorrowingCreateSerializer
        elif self.action == "return_book":
            return BorrowingReturnSerializer

        return BorrowingSerializer

    @action(detail=True, methods=["POST"], url_path="return", url_name="return-book")
    def return_book(self, request, pk=None):
        borrowing = self.get_object()

        serializer = self.get_serializer(borrowing, data=request.data, partial=True)

        if serializer.is_valid():
            with transaction.atomic():
                try:
                    serializer.save()

                    borrowing.actual_return_date = timezone.now().date()
                    borrowing.save()

                    if borrowing.actual_return_date > borrowing.expected_return_date:
                        overdue_days = (
                            borrowing.actual_return_date
                            - borrowing.expected_return_date
                        ).days
                        fine_amount = overdue_days * borrowing.book.daily_fee * 2
                        payment = apps.get_model("payment", "Payment")
                        payment.objects.create(
                            borrowing=borrowing,
                            money_to_pay=fine_amount,
                            status="PENDING",
                            type="FINE",
                        )
                        message = (
                            f"You have to pay {fine_amount} for overdue borrowing."
                        )

                        return Response({"message": message})
                    else:
                        return Response({"message": "Book was successfully returned."})
                except Exception as e:
                    return Response(
                        {
                            "message": "An error occurred while processing the return.",
                            "error": format(e),
                        }
                    )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)

        if response.status_code == status.HTTP_201_CREATED:
            borrowing = response.data
            message = (
                f"New Borrowing Created:\n"
                f"*ID: {borrowing['id']}\n"
                f"*Book ID: {borrowing['book']}\n"
                f"*User ID: {borrowing['user']}\n"
                f"*Borrow Date: {borrowing['borrow_date']}\n"
                f"*Expected Return Date: {borrowing['expected_return_date']}\n"
            )

            async_to_sync(send_borrowing_notification)(message)

        return response
