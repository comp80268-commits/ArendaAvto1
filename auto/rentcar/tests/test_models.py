import pytest
from rentcar.tests.factories import (
    CarFactory, CarImageFactory, CarPriceFactory, ExtraServiceFactory,
    BookingFactory, TouristPlaceFactory, TouristPlaceImageFactory,
    ReviewFactory, RentalStepFactory, PromotionFactory,
)

pytestmark = pytest.mark.django_db


def test_car_str():
    car = CarFactory(name="Renault Duster")
    assert str(car) == "Renault Duster"


def test_car_image_str():
    car = CarFactory(name="Kia Rio")
    img = CarImageFactory(car=car)
    assert str(img) == "Фото для Kia Rio"


def test_car_price_str_with_open_end():
    car = CarFactory(name="BMW X5")
    price = CarPriceFactory(car=car, days_from=10, days_to=None, price_per_day=2000)
    assert "∞" in str(price)


def test_car_price_ordering():
    car = CarFactory()
    CarPriceFactory(car=car, days_from=10)
    CarPriceFactory(car=car, days_from=1)
    prices = list(car.prices.all())
    assert prices[0].days_from == 1


def test_extra_service_str_free():
    service = ExtraServiceFactory(name="GPS", is_free=True, price=0)
    assert "бесплатно" in str(service)


def test_extra_service_str_paid():
    service = ExtraServiceFactory(name="Кресло", is_free=False, price=500)
    assert "500" in str(service)


def test_booking_str():
    booking = BookingFactory(customer_name="Петров Петр")
    assert "Петров Петр" in str(booking)
    assert booking.car.name in str(booking)


def test_booking_default_delivery_place():
    booking = BookingFactory()
    assert booking.delivery_place in ("city", "airport")


def test_tourist_place_str():
    place = TouristPlaceFactory(title="Чолпон-Ата")
    assert str(place) == "Чолпон-Ата"


def test_tourist_place_image_str():
    place = TouristPlaceFactory(title="Ысык-Куль")
    img = TouristPlaceImageFactory(place=place)
    assert str(img) == "Фото для Ысык-Куль"


def test_tourist_place_recommended_cars_m2m():
    place = TouristPlaceFactory()
    car = CarFactory()
    place.recommended_cars.add(car)
    assert car in place.recommended_cars.all()


def test_review_str():
    review = ReviewFactory(author_name="Данияр", rating=4)
    assert str(review) == "Данияр — 4★"


def test_review_date_auto_set():
    review = ReviewFactory()
    assert review.date is not None


def test_rental_step_str():
    step = RentalStepFactory(step_number=2, title="Оплата")
    assert str(step) == "2. Оплата"


def test_promotion_str():
    promo = PromotionFactory(title="Скидка на выходные")
    assert str(promo) == "Скидка на выходные"