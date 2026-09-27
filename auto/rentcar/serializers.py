import re
from rest_framework import serializers
from .models import (
    Car, CarImage, CarPrice, ExtraService, Booking,
    TouristPlace, TouristPlaceImage,
    Advantage, Review, RentalStep, Promotion
)


# ========== УНААЛАР ==========
class CarImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarImage
        fields = ['id', 'image']


class CarPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarPrice
        fields = ['id', 'days_from', 'days_to', 'price_per_day']


class CarListSerializer(serializers.ModelSerializer):
    """Тизме үчүн — жеңил версия (каталог, башкы бет)"""
    class Meta:
        model = Car
        fields = [
            'id', 'name', 'price_per_day', 'image', 'is_available',
            'brand', 'body_type', 'transmission', 'drive',
            'short_description'
        ]


class CarDetailSerializer(serializers.ModelSerializer):
    """
    Деталдуу барак үчүн (renault duster сыяктуу):
    - Галерея (images)
    - Баалар (prices)
    - Окшош унаалар (similar_cars)
    """
    images = CarImageSerializer(many=True, read_only=True)
    prices = CarPriceSerializer(many=True, read_only=True)
    similar_cars = serializers.SerializerMethodField()

    class Meta:
        model = Car
        fields = [
            'id', 'name', 'price_per_day', 'image', 'is_available',
            'brand', 'body_type', 'transmission', 'drive',
            'year', 'engine_volume', 'power', 'seats', 'consumption',
            'short_description', 'full_description',
            'images', 'prices', 'similar_cars'
        ]

    def get_similar_cars(self, obj):
        """Окшош унаалар — ошол эле кузов боюнча, өзүнөн башка"""
        similar = Car.objects.filter(
            body_type=obj.body_type,
            is_available=True
        ).exclude(id=obj.id)[:3]
        return CarListSerializer(similar, many=True).data


# ========== КОШУМЧА КЫЗМАТТАР ==========
class ExtraServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExtraService
        fields = ['id', 'name', 'price', 'is_free']


# ========== БРОНДОО ==========
class BookingSerializer(serializers.ModelSerializer):
    car_name = serializers.CharField(source='car.name', read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id',
            'customer_name', 'customer_phone',
            'car', 'car_name',
            'start_date', 'end_date',
            'extra_services',
            'delivery_time', 'delivery_place',
            'total_price', 'created_at'
        ]
        read_only_fields = ['total_price', 'created_at']

    def validate_customer_name(self, value):
        """ФИО текшерүү — жок дегенде 2 сөз (аты + фамилиясы)"""
        if len(value.strip().split()) < 2:
            raise serializers.ValidationError(
                "Введите полное ФИО (фамилия и имя)"
            )
        return value

    def validate_customer_phone(self, value):
        """Телефон номерин текшерүү — +7 (___) ___ __ __"""
        digits = re.sub(r'\D', '', value)

        if len(digits) == 11 and digits[0] in ('7', '8'):
            # Форматтоо: +7 (XXX) XXX-XX-XX
            return f"+7 ({digits[1:4]}) {digits[4:7]}-{digits[7:9]}-{digits[9:11]}"

        raise serializers.ValidationError(
            "Введите корректный номер: +7 (___) ___ __ __"
        )


# ========== БУРЯТИЯ ==========
class TouristPlaceImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TouristPlaceImage
        fields = ['id', 'image']


class TouristPlaceListSerializer(serializers.ModelSerializer):
    """Каталог үчүн — жеңил версия"""
    class Meta:
        model = TouristPlace
        fields = ['id', 'title', 'image', 'short_description']


class TouristPlaceDetailSerializer(serializers.ModelSerializer):
    """
    Деталдуу барак (Голубые озёра сыяктуу):
    - Галерея (images)
    - Подходящие автомобили (recommended_cars)
    """
    images = TouristPlaceImageSerializer(many=True, read_only=True)
    recommended_cars = CarListSerializer(many=True, read_only=True)

    class Meta:
        model = TouristPlace
        fields = [
            'id', 'title', 'image',
            'short_description', 'duration', 'distance', 'full_description',
            'images', 'recommended_cars'
        ]


# ========== БАШКЫ БЕТ БЛОКТОРУ ==========
class AdvantageSerializer(serializers.ModelSerializer):
    """Почему нам доверяют?"""
    class Meta:
        model = Advantage
        fields = ['id', 'icon', 'title', 'description', 'order']


class ReviewSerializer(serializers.ModelSerializer):
    """Отзывы о нашей компании"""
    platform_display = serializers.CharField(
        source='get_platform_display',
        read_only=True
    )

    class Meta:
        model = Review
        fields = [
            'id', 'author_name', 'rating', 'text',
            'platform', 'platform_display', 'date'
        ]


class RentalStepSerializer(serializers.ModelSerializer):
    """Как происходит аренда автомобиля"""
    class Meta:
        model = RentalStep
        fields = ['id', 'step_number', 'title', 'description', 'icon']


class PromotionSerializer(serializers.ModelSerializer):
    """Предложения для клиентов — акции"""
    class Meta:
        model = Promotion
        fields = ['id', 'title', 'description', 'image', 'button_text']