from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny

from borrowing.models import Borrowing
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
