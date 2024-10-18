from asgiref.sync import async_to_sync
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny

from borrowing.models import Borrowing
from borrowing.notification_when_borrowing_created import \
    send_borrowing_notification
from borrowing.serializers import (
    BorrowingListSerializer,
    BorrowingDetailSerializer,
    BorrowingSerializer,
    BorrowingCreateSerializer,
)


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
            message = f"New borrowing created: {borrowing["id"]}"

            async_to_sync(send_borrowing_notification)(message)

        return response
