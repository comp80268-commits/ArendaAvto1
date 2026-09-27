# rentcar/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CarViewSet, ExtraServiceViewSet, BookingViewSet,
    TouristPlaceViewSet,
    AdvantageViewSet, ReviewViewSet, RentalStepViewSet, PromotionViewSet
)

router = DefaultRouter()
router.register(r'cars', CarViewSet)
router.register(r'extra-services', ExtraServiceViewSet)
router.register(r'bookings', BookingViewSet)
router.register(r'places', TouristPlaceViewSet)
router.register(r'advantages', AdvantageViewSet)
router.register(r'reviews', ReviewViewSet)
router.register(r'steps', RentalStepViewSet)
router.register(r'promotions', PromotionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]