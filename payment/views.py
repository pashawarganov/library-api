import stripe
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.urls import reverse

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets

from payment.models import Payment
from borrowing.models import Borrowing
from payment.serializers import PaymentSerializer


stripe.api_key = settings.STRIPE_SECRET_KEY
FINE_MULTIPLIER = 2

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        data = request.data
        borrowing_id = data.get("borrowing_id")
        amount = data.get("money")

        borrowing = get_object_or_404(Borrowing, id=borrowing_id)

        if (
            borrowing.actual_return_date
            and borrowing.actual_return_date > borrowing.expected_return_date
        ):
            overdue_days = (
                borrowing.actual_return_date - borrowing.expected_return_date
            ).days
            daily_fee = borrowing.book.daily_fee
            money_to_pay = overdue_days * daily_fee * FINE_MULTIPLIER

            payment_fine = Payment.objects.create(
                borrowing_id=borrowing,
                session_url="",
                session_id="",
                money_to_pay=money_to_pay,
                status="PENDING",
                type="FINE",
            )

            # Створення Stripe сесії для оплати штрафу
            success_url = (
                request.build_absolute_uri(reverse("payment:payment-success"))
                + "?session_id={CHECKOUT_SESSION_ID}"
            )
            cancel_url = request.build_absolute_uri(reverse("payment:payment-cancel"))

            try:
                session = stripe.checkout.Session.create(
                    payment_method_types=["card"],
                    line_items=[
                        {
                            "price_data": {
                                "currency": "usd",
                                "product_data": {
                                    "name": f"Fine for overdue: {borrowing.book.title}",
                                },
                                "unit_amount": int(money_to_pay * 100),
                            },
                            "quantity": 1,
                        },
                    ],
                    mode="payment",
                    success_url=success_url,
                    cancel_url=cancel_url,
                )
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

            # Оновлення сесії для оплати штрафу
            payment_fine.session_url = session.url
            payment_fine.session_id = session.id
            payment_fine.save()

            return Response(
                {
                    "fine_payment_id": payment_fine.id,
                    "session_url": session.url,
                    "amount": money_to_pay,
                },
                status=status.HTTP_200_OK,
            )

        success_url = (
            request.build_absolute_uri(reverse("payment:payment-success"))
            + "?session_id={CHECKOUT_SESSION_ID}"
        )
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
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        payment = Payment.objects.create(
            borrowing_id=borrowing,
            session_url=session.url,
            session_id=session.id,
            money_to_pay=amount,
            status="PENDING",
            type="PAYMENT",
        )

        serializer = self.get_serializer(payment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class PaymentSuccessView(APIView):
    def get(self, request):
        session_id = request.query_params.get("session_id")
        if not session_id:
            return Response(
                {"error": "Session ID not provided."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            session = stripe.checkout.Session.retrieve(session_id)
            if session.payment_status == "paid":
                payment = get_object_or_404(Payment, session_id=session_id)
                payment.status = "PAID"
                payment.save()

                return Response(
                    {"message": "Payment was successful and marked as paid."},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"message": "Payment not completed yet."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class PaymentCancelView(APIView):
    def get(self, request):
        return Response(
            {
                "message": "Payment was cancelled. You can retry payment within 24 hours."
            },
            status=status.HTTP_200_OK,
        )
