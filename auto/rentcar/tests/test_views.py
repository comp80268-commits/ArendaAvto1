import pytest
from django.urls import reverse
from rentcar.tests.factories import (
    CarFactory, ExtraServiceFactory, BookingFactory,
    TouristPlaceFactory, AdvantageFactory, ReviewFactory,
    RentalStepFactory, PromotionFactory,
)

pytestmark = pytest.mark.django_db


# ========== CARS ==========
def test_car_list_public_only_available():
    CarFactory.create_batch(2, is_available=True)
    CarFactory(is_available=False)
    from rest_framework.test import APIClient
    client = APIClient()
    response = client.get(reverse("car-list"))
    assert response.status_code == 200
    assert len(response.data) == 2


def test_car_list_filter_by_brand(api_client):
    CarFactory(brand="Toyota")
    CarFactory(brand="Kia")
    response = api_client.get(reverse("car-list"), {"brand": "Toyota"})
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["brand"] == "Toyota"


def test_car_list_filter_by_body_type(api_client):
    CarFactory(body_type="sedan")
    CarFactory(body_type="suv")
    response = api_client.get(reverse("car-list"), {"body_type": "suv"})
    assert len(response.data) == 1


def test_car_list_sort_cheap(api_client):
    CarFactory(price_per_day=5000)
    CarFactory(price_per_day=2000)
    response = api_client.get(reverse("car-list"), {"sort": "cheap"})
    prices = [c["price_per_day"] for c in response.data]
    assert prices == sorted(prices)


def test_car_list_sort_expensive(api_client):
    CarFactory(price_per_day=5000)
    CarFactory(price_per_day=2000)
    response = api_client.get(reverse("car-list"), {"sort": "expensive"})
    prices = [c["price_per_day"] for c in response.data]
    assert prices == sorted(prices, reverse=True)


def test_car_retrieve_uses_detail_serializer(api_client):
    car = CarFactory()
    response = api_client.get(reverse("car-detail", args=[car.id]))
    assert response.status_code == 200
    assert "similar_cars" in response.data
    assert "images" in response.data


def test_car_create_requires_authentication(api_client):
    """Неавторизованный пользователь не может создавать авто"""
    response = api_client.post(reverse("car-list"), {"name": "New Car"})
    assert response.status_code in (401, 403)


def test_car_create_forbidden_for_regular_user(auth_client):
    """Обычный авторизованный пользователь (не админ) НЕ может создавать авто"""
    response = auth_client.post(reverse("car-list"), {
        "name": "New Car",
        "price_per_day": 3000,
    })
    assert response.status_code == 403


def test_car_create_allowed_for_admin(admin_client):
    """Админ может обращаться к созданию (упадёт по image, но не по правам)"""
    response = admin_client.post(reverse("car-list"), {
        "name": "New Car",
        "price_per_day": 3000,
    })
    # ожидаем ошибку валидации из-за отсутствия обязательного image, не 401/403
    assert response.status_code != 401
    assert response.status_code != 403


def test_car_update_forbidden_for_regular_user(auth_client):
    """Обычный пользователь не может редактировать авто"""
    car = CarFactory()
    response = auth_client.patch(reverse("car-detail", args=[car.id]), {
        "name": "Updated Name",
    })
    assert response.status_code == 403


def test_car_delete_forbidden_for_regular_user(auth_client):
    """Обычный пользователь не может удалять авто"""
    car = CarFactory()
    response = auth_client.delete(reverse("car-detail", args=[car.id]))
    assert response.status_code == 403


def test_car_delete_allowed_for_admin(admin_client):
    """Админ может удалять авто"""
    car = CarFactory()
    response = admin_client.delete(reverse("car-detail", args=[car.id]))
    assert response.status_code == 204


# ========== EXTRA SERVICES ==========
def test_extra_service_list_public(api_client):
    ExtraServiceFactory.create_batch(2)
    response = api_client.get(reverse("extraservice-list"))
    assert response.status_code == 200
    assert len(response.data) == 2


# ========== BOOKINGS ==========
def test_booking_create_success(api_client):
    car = CarFactory(price_per_day=1000)
    payload = {
        "customer_name": "Иванов Иван",
        "customer_phone": "87001234567",
        "car": car.id,
        "start_date": "2026-10-01",
        "end_date": "2026-10-04",
        "delivery_place": "city",
    }
    response = api_client.post(reverse("booking-list"), payload)
    assert response.status_code == 201
    assert response.data["customer_phone"] == "+7 (700) 123-45-67"
    assert response.data["total_price"] == 3000  # 3 дня * 1000


def test_booking_create_with_extra_services_total():
    from rest_framework.test import APIClient
    client = APIClient()
    car = CarFactory(price_per_day=1000)
    paid_service = ExtraServiceFactory(price=500, is_free=False)
    free_service = ExtraServiceFactory(price=0, is_free=True)
    payload = {
        "customer_name": "Иванов Иван",
        "customer_phone": "87001234567",
        "car": car.id,
        "start_date": "2026-10-01",
        "end_date": "2026-10-03",
        "extra_services": [paid_service.id, free_service.id],
    }
    response = client.post(reverse("booking-list"), payload)
    assert response.status_code == 201
    # 2 дня * 1000 + 500 (платная услуга, бесплатная не добавляется)
    assert response.data["total_price"] == 2500


def test_booking_create_missing_name(api_client):
    car = CarFactory()
    response = api_client.post(reverse("booking-list"), {
        "customer_phone": "87001234567",
        "car": car.id,
        "start_date": "2026-10-01",
        "end_date": "2026-10-03",
    })
    assert response.status_code == 400
    assert "error" in response.data


def test_booking_create_missing_phone(api_client):
    car = CarFactory()
    response = api_client.post(reverse("booking-list"), {
        "customer_name": "Иванов Иван",
        "car": car.id,
        "start_date": "2026-10-01",
        "end_date": "2026-10-03",
    })
    assert response.status_code == 400


def test_booking_create_invalid_phone(api_client):
    car = CarFactory()
    response = api_client.post(reverse("booking-list"), {
        "customer_name": "Иванов Иван",
        "customer_phone": "12345",
        "car": car.id,
        "start_date": "2026-10-01",
        "end_date": "2026-10-03",
    })
    assert response.status_code == 400


def test_booking_create_car_not_found(api_client):
    response = api_client.post(reverse("booking-list"), {
        "customer_name": "Иванов Иван",
        "customer_phone": "87001234567",
        "car": 9999,
        "start_date": "2026-10-01",
        "end_date": "2026-10-03",
    })
    assert response.status_code == 404


def test_booking_create_invalid_date_format(api_client):
    car = CarFactory()
    response = api_client.post(reverse("booking-list"), {
        "customer_name": "Иванов Иван",
        "customer_phone": "87001234567",
        "car": car.id,
        "start_date": "01-10-2026",
        "end_date": "2026-10-03",
    })
    assert response.status_code == 400


def test_booking_create_end_date_before_start(api_client):
    car = CarFactory()
    response = api_client.post(reverse("booking-list"), {
        "customer_name": "Иванов Иван",
        "customer_phone": "87001234567",
        "car": car.id,
        "start_date": "2026-10-05",
        "end_date": "2026-10-01",
    })
    assert response.status_code == 400


def test_booking_list_requires_admin(auth_client):
    """Обычный авторизованный, но не админ — должен получить 403"""
    BookingFactory()
    response = auth_client.get(reverse("booking-list"))
    assert response.status_code == 403


def test_booking_list_unauthenticated_forbidden(api_client):
    BookingFactory()
    response = api_client.get(reverse("booking-list"))
    assert response.status_code in (401, 403)


def test_booking_list_admin_allowed(admin_client):
    BookingFactory.create_batch(2)
    response = admin_client.get(reverse("booking-list"))
    assert response.status_code == 200
    assert len(response.data) == 2


# ========== TOURIST PLACES ==========
def test_place_list_public(api_client):
    TouristPlaceFactory.create_batch(2)
    response = api_client.get(reverse("touristplace-list"))
    assert response.status_code == 200
    assert len(response.data) == 2


def test_place_retrieve_uses_detail_serializer(api_client):
    place = TouristPlaceFactory()
    response = api_client.get(reverse("touristplace-detail", args=[place.id]))
    assert "recommended_cars" in response.data
    assert "images" in response.data


# ========== ADVANTAGES / REVIEWS / STEPS / PROMOTIONS ==========
def test_advantage_list_public(api_client):
    AdvantageFactory.create_batch(2)
    response = api_client.get(reverse("advantage-list"))
    assert response.status_code == 200
    assert len(response.data) == 2


def test_review_list_only_published(api_client):
    ReviewFactory(is_published=True)
    ReviewFactory(is_published=False)
    response = api_client.get(reverse("review-list"))
    assert response.status_code == 200
    assert len(response.data) == 1


def test_rental_step_list_public(api_client):
    RentalStepFactory.create_batch(3)
    response = api_client.get(reverse("rentalstep-list"))
    assert response.status_code == 200
    assert len(response.data) == 3


def test_promotion_list_only_active(api_client):
    PromotionFactory(is_active=True)
    PromotionFactory(is_active=False)
    response = api_client.get(reverse("promotion-list"))
    assert response.status_code == 200
    assert len(response.data) == 1