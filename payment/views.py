from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

from payment.models import Payment
from payment.serializers import PaymentSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Payment.objects.all()
        return Payment.objects.filter(borrowing__user=user)

    def perform_create(self, serializer):
        raise PermissionDenied("You cannot create payments directly.")
