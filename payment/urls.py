from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import PaymentViewSet, PaymentSuccessView, PaymentCancelView

router = DefaultRouter()
router.register("create-payment", PaymentViewSet, basename="payment")

urlpatterns = [
    path("", include(router.urls)),
    path("payment/success/", PaymentSuccessView.as_view(), name="payment-success"),
    path("payment/cancel/", PaymentCancelView.as_view(), name="payment-cancel"),
]

app_name = "payment"
