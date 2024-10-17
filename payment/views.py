from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
import stripe
from django.conf import settings
from django.urls import reverse
from django.shortcuts import get_object_or_404
from .models import Payment
from borrowing.models import Borrowing
from rest_framework.permissions import IsAuthenticated
from .serializers import PaymentSerializer
from rest_framework.views import APIView


stripe.api_key = settings.STRIPE_SECRET_KEY

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        data = request.data
        borrowing_id = data.get("borrowing_id")
        amount = data.get("money")

        borrowing = get_object_or_404(Borrowing, id=borrowing_id)

        success_url = request.build_absolute_uri(reverse("payment:payment-success"))
        cancel_url = request.build_absolute_uri(reverse("payment:payment-cancel"))

        try:
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[
                    {
                        "price_data": {
                            "currency": "usd",
                            "product_data": {
                                "name": borrowing.book.title,
                            },
                            "unit_amount": int(amount * 100),
                        },
                        "quantity": 1,
                    },
                ],
                mode="payment",
                success_url=success_url,
                cancel_url=cancel_url,
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        payment = Payment.objects.create(
            borrowing_id=borrowing,
            session_url=session.url,
            session_id=session.id,
            money_to_pay=amount,
            status="PENDING",
            type="PAYMENT"
        )

        serializer = self.get_serializer(payment)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )


class PaymentSuccessView(APIView):
    def get(self, request):
        return Response(
            {
                "message": "Payment Successful!"
            }, status=status.HTTP_200_OK
        )

class PaymentCancelView(APIView):
    def get(self, request):
        return Response(
            {
                "message": "Payment Cancelled."
            }, status=status.HTTP_200_OK
        )
