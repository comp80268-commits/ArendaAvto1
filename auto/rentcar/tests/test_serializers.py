import pytest
from rentcar.serializers import (
    CarListSerializer, CarDetailSerializer,
    BookingSerializer, ReviewSerializer,
)
from rentcar.tests.factories import CarFactory, BookingFactory, ReviewFactory

pytestmark = pytest.mark.django_db


# ---------- Car ----------
def test_car_list_serializer_fields():
    car = CarFactory()
    data = CarListSerializer(car).data
    assert data["name"] == car.name
    assert data["price_per_day"] == car.price_per_day
    assert "full_description" not in data  # облегчённая версия


def test_car_detail_serializer_has_similar_cars():
    car = CarFactory(body_type="sedan")
    CarFactory(body_type="sedan")  # похожая
    CarFactory(body_type="suv")    # не похожая
    data = CarDetailSerializer(car).data
    assert "similar_cars" in data
    assert all(c["id"] != car.id for c in data["similar_cars"])


def test_car_detail_excludes_unavailable_from_similar():
    car = CarFactory(body_type="sedan")
    CarFactory(body_type="sedan", is_available=False)
    data = CarDetailSerializer(car).data
    assert len(data["similar_cars"]) == 0


# ---------- Booking: валидация ФИО ----------
@pytest.mark.parametrize("name", ["Иван", "   Пётр   ", ""])
def test_booking_invalid_customer_name(name):
    car = CarFactory()
    data = {
        "customer_name": name,
        "customer_phone": "+77001234567",
        "car": car.id,
        "start_date": "2026-10-01",
        "end_date": "2026-10-05",
    }
    serializer = BookingSerializer(data=data)
    assert not serializer.is_valid()
    assert "customer_name" in serializer.errors


def test_booking_valid_customer_name():
    car = CarFactory()
    data = {
        "customer_name": "Иванов Иван",
        "customer_phone": "+77001234567",
        "car": car.id,
        "start_date": "2026-10-01",
        "end_date": "2026-10-05",
    }
    serializer = BookingSerializer(data=data)
    assert serializer.is_valid(), serializer.errors


# ---------- Booking: валидация телефона ----------
@pytest.mark.parametrize("phone,expected", [
    ("87001234567", "+7 (700) 123-45-67"),
    ("+7 700 123 45 67", "+7 (700) 123-45-67"),
    ("77001234567", "+7 (700) 123-45-67"),
])
def test_booking_phone_normalization(phone, expected):
    car = CarFactory()
    data = {
        "customer_name": "Иванов Иван",
        "customer_phone": phone,
        "car": car.id,
        "start_date": "2026-10-01",
        "end_date": "2026-10-05",
    }
    serializer = BookingSerializer(data=data)
    assert serializer.is_valid(), serializer.errors
    assert serializer.validated_data["customer_phone"] == expected


@pytest.mark.parametrize("phone", ["12345", "abcde", "+1 202 555 0000"])
def test_booking_invalid_phone(phone):
    car = CarFactory()
    data = {
        "customer_name": "Иванов Иван",
        "customer_phone": phone,
        "car": car.id,
        "start_date": "2026-10-01",
        "end_date": "2026-10-05",
    }
    serializer = BookingSerializer(data=data)
    assert not serializer.is_valid()
    assert "customer_phone" in serializer.errors


def test_booking_serializer_readonly_fields():
    booking = BookingFactory()
    data = BookingSerializer(booking).data
    assert data["car_name"] == booking.car.name
    assert "total_price" in data
    assert "created_at" in data


# ---------- Review ----------
def test_review_serializer_platform_display():
    review = ReviewFactory(platform="google")
    data = ReviewSerializer(review).data
    assert data["platform_display"] == "Google Maps"