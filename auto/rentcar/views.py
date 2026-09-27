import re
from datetime import datetime
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly,
    IsAdminUser,
    AllowAny,
)
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import (
    Car, ExtraService, Booking,
    TouristPlace,
    Advantage, Review, RentalStep, Promotion
)
from .serializers import (
    CarListSerializer, CarDetailSerializer,
    ExtraServiceSerializer, BookingSerializer,
    TouristPlaceListSerializer, TouristPlaceDetailSerializer,
    AdvantageSerializer, ReviewSerializer, RentalStepSerializer, PromotionSerializer
)


# ========== УНААЛАР ==========
@extend_schema_view(
    list=extend_schema(summary="Унаалардын тизмеси", tags=["Cars"]),
    retrieve=extend_schema(summary="Унаанын деталдуу баракчасы", tags=["Cars"]),
    create=extend_schema(summary="Унаа кошуу (admin)", tags=["Cars"]),
    update=extend_schema(summary="Унааны өзгөртүү (admin)", tags=["Cars"]),
    partial_update=extend_schema(summary="Унааны жарым-жартылай өзгөртүү (admin)", tags=["Cars"]),
    destroy=extend_schema(summary="Унааны өчүрүү (admin)", tags=["Cars"]),
)
class CarViewSet(viewsets.ModelViewSet):
    """
    Унаалар:
    - GET /api/cars/ — тизме (фильтрлер менен), доступно всем
    - GET /api/cars/1/ — деталдуу барак, доступно всем
    - POST/PUT/PATCH/DELETE — только админ (is_staff=True)
    """
    queryset = Car.objects.filter(is_available=True)

    def get_permissions(self):
        """Чтение доступно всем, добавление/изменение/удаление — только админу"""
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAdminUser()]

    def get_serializer_class(self):
        """Деталдуу барак үчүн башка сериалайзер"""
        if self.action == 'retrieve':
            return CarDetailSerializer
        return CarListSerializer

    def get_queryset(self):
        """Фильтрлөө: марка, кузов, коробка, привод, сортировка"""
        queryset = Car.objects.filter(is_available=True)

        brand = self.request.query_params.get('brand')
        if brand:
            queryset = queryset.filter(brand__icontains=brand)

        body_type = self.request.query_params.get('body_type')
        if body_type:
            queryset = queryset.filter(body_type__icontains=body_type)

        transmission = self.request.query_params.get('transmission')
        if transmission:
            queryset = queryset.filter(transmission__icontains=transmission)

        drive = self.request.query_params.get('drive')
        if drive:
            queryset = queryset.filter(drive__icontains=drive)

        sort = self.request.query_params.get('sort')
        if sort == 'cheap':
            queryset = queryset.order_by('price_per_day')
        elif sort == 'expensive':
            queryset = queryset.order_by('-price_per_day')

        return queryset


# ========== КОШУМЧА КЫЗМАТТАР ==========
@extend_schema_view(
    list=extend_schema(summary="Кошумча кызматтардын тизмеси", tags=["ExtraServices"]),
    retrieve=extend_schema(summary="Кызматтын деталдары", tags=["ExtraServices"]),
    create=extend_schema(summary="Кызмат кошуу (admin)", tags=["ExtraServices"]),
    update=extend_schema(summary="Кызматты өзгөртүү (admin)", tags=["ExtraServices"]),
    partial_update=extend_schema(summary="Кызматты жарым-жартылай өзгөртүү (admin)", tags=["ExtraServices"]),
    destroy=extend_schema(summary="Кызматты өчүрүү (admin)", tags=["ExtraServices"]),
)
class ExtraServiceViewSet(viewsets.ModelViewSet):
    queryset = ExtraService.objects.all()
    serializer_class = ExtraServiceSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


# ========== БРОНДОО ==========
@extend_schema_view(
    list=extend_schema(summary="Брондордун тизмеси (admin)", tags=["Bookings"]),
    retrieve=extend_schema(summary="Броньдун деталдары (admin)", tags=["Bookings"]),
    create=extend_schema(summary="Жаңы брондоо (публичный)", tags=["Bookings"]),
    update=extend_schema(summary="Броньду өзгөртүү (admin)", tags=["Bookings"]),
    partial_update=extend_schema(summary="Броньду жарым-жартылай өзгөртүү (admin)", tags=["Bookings"]),
    destroy=extend_schema(summary="Броньду өчүрүү (admin)", tags=["Bookings"]),
)
class BookingViewSet(viewsets.ModelViewSet):
    """
    Брондоо:
    - POST /api/bookings/ — жаңы брондоо (публичный, без токена)
    - GET/PUT/DELETE — только админ (JWT)
    """
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

    def get_permissions(self):
        """Создание доступно всем, остальное — только админу"""
        if self.action == 'create':
            return [AllowAny()]
        return [IsAdminUser()]

    def create(self, request, *args, **kwargs):
        """
        Брондоо + жалпы сумманы автоматтык эсептөө.
        Формула: (күн × сутка баа) + кошумча кызматтар
        """
        data = request.data

        # 1. ФИО текшерүү
        if not data.get('customer_name'):
            return Response(
                {"error": "Введите ФИО"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 2. Телефон текшерүү жана форматтоо
        phone_raw = data.get('customer_phone', '')
        if not phone_raw:
            return Response(
                {"error": "Введите телефон"},
                status=status.HTTP_400_BAD_REQUEST
            )

        phone_digits = re.sub(r'\D', '', phone_raw)
        if len(phone_digits) == 11 and phone_digits[0] in ('7', '8'):
            formatted_phone = (
                f"+7 ({phone_digits[1:4]}) "
                f"{phone_digits[4:7]}-{phone_digits[7:9]}-{phone_digits[9:11]}"
            )
        else:
            return Response(
                {"error": "Неверный номер телефона: +7 (___) ___ __ __"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 3. Унаа
        try:
            car = Car.objects.get(id=data.get('car'))
        except Car.DoesNotExist:
            return Response(
                {"error": "Автомобиль не найден"},
                status=status.HTTP_404_NOT_FOUND
            )

        # 4. Даталар
        try:
            start = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
            end = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
        except (KeyError, ValueError):
            return Response(
                {"error": "Неверный формат даты (ГГГГ-ММ-ДД)"},
                status=status.HTTP_400_BAD_REQUEST
            )

        days = (end - start).days
        if days <= 0:
            return Response(
                {"error": "Дата окончания должна быть позже даты начала"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 5. Негизги баа
        total = days * car.price_per_day

        # 6. Кошумча кызматтар
        # .get() на QueryDict (multipart/form-data запросы) возвращает только
        # последнее значение из нескольких одноимённых полей, из-за чего
        # список услуг обрезался. .getlist() достаёт все.
        if hasattr(data, 'getlist'):
            service_ids = data.getlist('extra_services')
        else:
            service_ids = data.get('extra_services', [])

        services = ExtraService.objects.filter(id__in=service_ids)
        for s in services:
            if not s.is_free:
                total += s.price

        # 7. Сактоо
        booking = Booking.objects.create(
            customer_name=data.get('customer_name'),
            customer_phone=formatted_phone,
            car=car,
            start_date=start,
            end_date=end,
            delivery_time=data.get('delivery_time') or None,
            delivery_place=data.get('delivery_place', 'city'),
            total_price=total
        )
        booking.extra_services.set(services)

        serializer = self.get_serializer(booking)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# ========== БУРЯТИЯ ==========
@extend_schema_view(
    list=extend_schema(summary="Туристтик жерлердин каталогу", tags=["TouristPlaces"]),
    retrieve=extend_schema(summary="Жердин деталдуу баракчасы", tags=["TouristPlaces"]),
    create=extend_schema(summary="Жер кошуу (admin)", tags=["TouristPlaces"]),
    update=extend_schema(summary="Жерди өзгөртүү (admin)", tags=["TouristPlaces"]),
    partial_update=extend_schema(summary="Жерди жарым-жартылай өзгөртүү (admin)", tags=["TouristPlaces"]),
    destroy=extend_schema(summary="Жерди өчүрүү (admin)", tags=["TouristPlaces"]),
)
class TouristPlaceViewSet(viewsets.ModelViewSet):
    """
    Заповедная Бурятия:
    - GET /api/places/ — каталог (жеңил версия)
    - GET /api/places/1/ — деталдуу барак (галерея + унаалар)
    - POST/PUT/DELETE — только админ (JWT)
    """
    queryset = TouristPlace.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        """Деталдуу барак үчүн башка сериалайзер"""
        if self.action == 'retrieve':
            return TouristPlaceDetailSerializer
        return TouristPlaceListSerializer


# ========== БАШКЫ БЕТ БЛОКТОРУ ==========
@extend_schema_view(
    list=extend_schema(summary="Артыкчылыктардын тизмеси", tags=["Advantages"]),
    retrieve=extend_schema(summary="Артыкчылыктын деталдары", tags=["Advantages"]),
    create=extend_schema(summary="Артыкчылык кошуу (admin)", tags=["Advantages"]),
    update=extend_schema(summary="Артыкчылыкты өзгөртүү (admin)", tags=["Advantages"]),
    partial_update=extend_schema(summary="Артыкчылыкты жарым-жартылай өзгөртүү (admin)", tags=["Advantages"]),
    destroy=extend_schema(summary="Артыкчылыкты өчүрүү (admin)", tags=["Advantages"]),
)
class AdvantageViewSet(viewsets.ModelViewSet):
    """Почему нам доверяют?"""
    queryset = Advantage.objects.all()
    serializer_class = AdvantageSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


@extend_schema_view(
    list=extend_schema(summary="Отзывдардын тизмеси", tags=["Reviews"]),
    retrieve=extend_schema(summary="Отзывдун деталдары", tags=["Reviews"]),
    create=extend_schema(summary="Отзыв кошуу (admin)", tags=["Reviews"]),
    update=extend_schema(summary="Отзывду өзгөртүү (admin)", tags=["Reviews"]),
    partial_update=extend_schema(summary="Отзывду жарым-жартылай өзгөртүү (admin)", tags=["Reviews"]),
    destroy=extend_schema(summary="Отзывду өчүрүү (admin)", tags=["Reviews"]),
)
class ReviewViewSet(viewsets.ModelViewSet):
    """Отзывы о нашей компании"""
    queryset = Review.objects.filter(is_published=True)
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


@extend_schema_view(
    list=extend_schema(summary="Аренда этаптары", tags=["RentalSteps"]),
    retrieve=extend_schema(summary="Этаптын деталдары", tags=["RentalSteps"]),
    create=extend_schema(summary="Этап кошуу (admin)", tags=["RentalSteps"]),
    update=extend_schema(summary="Этапты өзгөртүү (admin)", tags=["RentalSteps"]),
    partial_update=extend_schema(summary="Этапты жарым-жартылай өзгөртүү (admin)", tags=["RentalSteps"]),
    destroy=extend_schema(summary="Этапты өчүрүү (admin)", tags=["RentalSteps"]),
)
class RentalStepViewSet(viewsets.ModelViewSet):
    """Как происходит аренда автомобиля"""
    queryset = RentalStep.objects.all()
    serializer_class = RentalStepSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


@extend_schema_view(
    list=extend_schema(summary="Акциялардын тизмеси", tags=["Promotions"]),
    retrieve=extend_schema(summary="Акциянын деталдары", tags=["Promotions"]),
    create=extend_schema(summary="Акция кошуу (admin)", tags=["Promotions"]),
    update=extend_schema(summary="Акцияны өзгөртүү (admin)", tags=["Promotions"]),
    partial_update=extend_schema(summary="Акцияны жарым-жартылай өзгөртүү (admin)", tags=["Promotions"]),
    destroy=extend_schema(summary="Акцияны өчүрүү (admin)", tags=["Promotions"]),
)
class PromotionViewSet(viewsets.ModelViewSet):
    """Предложения для клиентов — акции"""
    queryset = Promotion.objects.filter(is_active=True)
    serializer_class = PromotionSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]