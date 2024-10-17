from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import PaymentViewSet

router = DefaultRouter()
router.register("payments", PaymentViewSet, basename="payment")

urlpatterns = [
    path('', include(router.urls)),
]

app_name = "payment"
