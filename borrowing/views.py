from asgiref.sync import async_to_sync
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny

from borrowing.models import Borrowing
from borrowing.serializers import (
    BorrowingListSerializer,
    BorrowingDetailSerializer,
    BorrowingSerializer,
    BorrowingCreateSerializer,
)
from telegram_bot import send_borrowing_notification


class BorrowingViewSet(viewsets.ModelViewSet):
    permission_classes = (AllowAny,)

    def get_queryset(self):
        queryset = Borrowing.objects.all()

        if self.action in ["list", "retrieve"]:
            return queryset.select_related("book", "user").filter(
                user=self.request.user
            )

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return BorrowingListSerializer
        elif self.action == "retrieve":
            return BorrowingDetailSerializer
        elif self.action == "create":
            return BorrowingCreateSerializer

        return BorrowingSerializer

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
                f"*Actual Return Date: {borrowing['actual_return_date']}"
            )

            async_to_sync(send_borrowing_notification)(message)

        return response
