import io
import factory
from PIL import Image
from django.core.files.base import ContentFile
from rentcar.models import (
    Car, CarImage, CarPrice, ExtraService, Booking,
    TouristPlace, TouristPlaceImage,
    Advantage, Review, RentalStep, Promotion,
)


def _generate_test_image():
    """Создаёт лёгкий валидный PNG-файл в памяти для ImageField."""
    buf = io.BytesIO()
    Image.new("RGB", (10, 10), color="red").save(buf, format="PNG")
    return ContentFile(buf.getvalue(), name="test.png")


class CarFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Car

    name = factory.Sequence(lambda n: f"Test Car {n}")
    price_per_day = 3000
    image = factory.LazyFunction(_generate_test_image)
    is_available = True
    brand = "Toyota"
    body_type = "sedan"
    transmission = "automatic"
    drive = "front"
    year = 2022
    engine_volume = "2.0"
    power = "150 л.с."
    seats = 5
    consumption = "7.5 л/100км"
    short_description = "Короткое описание"
    full_description = "Полное описание"


class CarImageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CarImage

    car = factory.SubFactory(CarFactory)
    image = factory.LazyFunction(_generate_test_image)


class CarPriceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CarPrice

    car = factory.SubFactory(CarFactory)
    days_from = 1
    days_to = 3
    price_per_day = 3500


class ExtraServiceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ExtraService

    name = "Детское кресло"
    price = 500
    is_free = False


class BookingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Booking

    customer_name = "Иванов Иван"
    customer_phone = "+7 (700) 123-45-67"
    car = factory.SubFactory(CarFactory)
    start_date = "2026-10-01"
    end_date = "2026-10-05"
    delivery_time = "10:00"
    delivery_place = "city"
    total_price = 12000


class TouristPlaceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TouristPlace

    title = "Голубые озёра"
    image = factory.LazyFunction(_generate_test_image)
    short_description = "Короткое описание"
    duration = "2 дня"
    distance = "150 км"
    full_description = "Полное описание"


class TouristPlaceImageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TouristPlaceImage

    place = factory.SubFactory(TouristPlaceFactory)
    image = factory.LazyFunction(_generate_test_image)


class AdvantageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Advantage

    icon = "shield"
    title = "Надёжность"
    description = "Описание преимущества"
    order = 1


class ReviewFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Review

    author_name = "Айгерим"
    rating = 5
    text = "Отличный сервис!"
    platform = "google"
    is_published = True
    # date не указываем — auto_now_add сам проставит


class RentalStepFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RentalStep

    step_number = 1
    title = "Выбор авто"
    description = "Описание шага"
    icon = "car"


class PromotionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Promotion

    title = "Скидка 10%"
    description = "Описание акции"
    image = factory.LazyFunction(_generate_test_image)
    button_text = "Подробнее"
    is_active = True