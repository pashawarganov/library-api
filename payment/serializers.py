from rest_framework import serializers
from payment.models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = (
            "id",
            "status",
            "type",
            "borrowing",
            "session_url",
            "session_id",
            "money_to_pay",
        )


class PaymentCreateSerializer(serializers.Serializer):
    borrowing_id = serializers.IntegerField(required=True)
    money = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)
