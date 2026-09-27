from django.db import models


# ========== УНААЛАР ==========
class Car(models.Model):
    """Автомобиль"""
    name = models.CharField(max_length=150, verbose_name="Название автомобиля")
    price_per_day = models.IntegerField(verbose_name="Стоимость суток (₽)")
    image = models.ImageField(upload_to='cars/', verbose_name="Фото автомобиля")
    is_available = models.BooleanField(default=True, verbose_name="Доступен")

    # Фильтрлер үчүн
    brand = models.CharField(max_length=50, blank=True, verbose_name="Марка")
    body_type = models.CharField(max_length=50, blank=True, verbose_name="Кузов")
    transmission = models.CharField(max_length=50, blank=True, verbose_name="Коробка")
    drive = models.CharField(max_length=50, blank=True, verbose_name="Привод")

    # Деталдуу барак үчүн
    year = models.IntegerField(null=True, blank=True, verbose_name="Год выпуска")
    engine_volume = models.CharField(max_length=50, blank=True, verbose_name="Объём двигателя")
    power = models.CharField(max_length=50, blank=True, verbose_name="Мощность двигателя")
    seats = models.IntegerField(null=True, blank=True, verbose_name="Пассажирских мест")
    consumption = models.CharField(max_length=50, blank=True, verbose_name="Расход топлива")
    short_description = models.CharField(max_length=255, blank=True, verbose_name="Краткое описание")
    full_description = models.TextField(blank=True, verbose_name="Полное описание")

    class Meta:
        verbose_name = "Автомобиль"
        verbose_name_plural = "Автомобили"
        # ============================================================
        # 🔐 PERMISSION'ДОР (моделдик укуктар)
        # Django автоматтык түрдө төмөнкүлөрдү кошот:
        #   add_car, change_car, delete_car, view_car
        # Бул жерде — КОШУМЧА жекече укуктар:
        # ============================================================
        permissions = [
            ("can_view_price",   "💰 Бааны көрүү (баа жашырылбайт)"),
            ("can_publish_car",  "🚗 Унааны жарыялоо (сайтка чыгаруу)"),
            ("can_hide_car",     "🙈 Унааны жашыруу (is_available=False)"),
        ]

    def __str__(self):
        return self.name


class CarImage(models.Model):
    """Галерея унаанын кошумча сүрөттөрү"""
    car = models.ForeignKey(
        Car, on_delete=models.CASCADE,
        related_name='images', verbose_name="Автомобиль"
    )
    image = models.ImageField(upload_to='cars/gallery/', verbose_name="Фото")

    class Meta:
        verbose_name = "Фото автомобиля"
        verbose_name_plural = "Фото автомобилей"
        # 🔐 PERMISSION: автоматтык add/change/delete/view_carimage гана
        # Кошумча укук керек эмес — галерея контентин админ башкарат

    def __str__(self):
        return f"Фото для {self.car.name}"


class CarPrice(models.Model):
    """Баанын таблицасы — ар кандай мөөнөткө"""
    car = models.ForeignKey(
        Car, on_delete=models.CASCADE,
        related_name='prices', verbose_name="Автомобиль"
    )
    days_from = models.IntegerField(verbose_name="От (дней)")
    days_to = models.IntegerField(null=True, blank=True, verbose_name="До (дней)")
    price_per_day = models.IntegerField(verbose_name="Цена за сутки (₽)")

    class Meta:
        verbose_name = "Цена автомобиля"
        verbose_name_plural = "Цены автомобилей"
        ordering = ['days_from']
        # ============================================================
        # 🔐 PERMISSION'ДОР — бааларды өзгөртүү өзүнчө укук
        # ============================================================
        permissions = [
            ("can_change_price", "💵 Бааны өзгөртүү (таблицадагы баалар)"),
        ]

    def __str__(self):
        return f"{self.car.name}: {self.days_from}–{self.days_to or '∞'} дней — {self.price_per_day} ₽"


class ExtraService(models.Model):
    """Дополнительные услуги"""
    name = models.CharField(max_length=150, verbose_name="Название услуги")
    price = models.IntegerField(default=0, verbose_name="Цена (₽). 0 = бесплатно")
    is_free = models.BooleanField(default=False, verbose_name="Бесплатно")

    class Meta:
        verbose_name = "Дополнительная услуга"
        verbose_name_plural = "Дополнительные услуги"
        # 🔐 PERMISSION: автоматтык add/change/delete/view_extraservice
        # Кошумча укук керек эмес — админ башкарат

    def __str__(self):
        return f"{self.name} — {'бесплатно' if self.is_free else str(self.price) + ' ₽'}"


class Booking(models.Model):
    """Бронирование автомобиля — Pop-up форма үчүн"""
    DELIVERY_CHOICES = [
        ('city', 'город'),
        ('airport', 'аэропорт'),
    ]

    # 👇 POP-UP ФОРМА ҮЧҮН ТАЛААЛАР 👇
    customer_name = models.CharField(max_length=150, verbose_name="ФИО клиента")
    customer_phone = models.CharField(max_length=20, verbose_name="Телефон клиента")
    # 👆 ЖАҢЫ 👆

    # Унаа жана мөөнөт
    car = models.ForeignKey(
        Car, on_delete=models.CASCADE,
        verbose_name="Выберите автомобиль"
    )
    start_date = models.DateField(verbose_name="Дата начала аренды")
    end_date = models.DateField(verbose_name="Дата окончания аренды")

    # Кошумча кызматтар
    extra_services = models.ManyToManyField(
        ExtraService, blank=True,
        verbose_name="Дополнительные услуги"
    )

    # Подача
    delivery_time = models.TimeField(null=True, blank=True, verbose_name="Время подачи")
    delivery_place = models.CharField(
        max_length=20,
        choices=DELIVERY_CHOICES,
        default='city',
        verbose_name="Место подачи"
    )

    # Итого
    total_price = models.IntegerField(default=0, verbose_name="Итого (₽)")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Бронирование"
        verbose_name_plural = "Бронирования"
        ordering = ['-created_at']
        # ============================================================
        # 🔐 PERMISSION'ДОР — брондор менен иштөө
        # ============================================================
        permissions = [
            ("can_view_all_bookings",  "📋 Баардык брондорду көрүү"),
            ("can_confirm_booking",    "✅ Броньду ырастоо"),
            ("can_cancel_booking",     "❌ Броньду жокко чыгаруу"),
            ("can_export_bookings",    "📤 Брондорду Excel'ге экспорттоо"),
        ]

    def __str__(self):
        return f"{self.customer_name} | {self.car.name} | {self.start_date} — {self.end_date}"


# ========== БУРЯТИЯ ==========
class TouristPlace(models.Model):
    """Заповедная Бурятия — жерлер"""
    title = models.CharField(max_length=150, verbose_name="Название места")
    image = models.ImageField(upload_to='places/', verbose_name="Главное фото")
    short_description = models.CharField(max_length=255, blank=True, verbose_name="Краткое описание")
    duration = models.CharField(max_length=100, blank=True, verbose_name="Продолжительность маршрута")
    distance = models.CharField(max_length=100, blank=True, verbose_name="Расстояние от Горно-Алтайска")
    full_description = models.TextField(blank=True, verbose_name="Полное описание")

    recommended_cars = models.ManyToManyField(
        Car, blank=True, related_name='places',
        verbose_name="Подходящие автомобили"
    )

    class Meta:
        verbose_name = "Достопримечательность"
        verbose_name_plural = "Достопримечательности"
        # ============================================================
        # 🔐 PERMISSION'ДОР — туристтик жерлер
        # ============================================================
        permissions = [
            ("can_publish_place", "🏔️ Жерди жарыялоо (сайтка чыгаруу)"),
            ("can_feature_place", "⭐ Жерди башкы бетке чыгаруу"),
        ]

    def __str__(self):
        return self.title


class TouristPlaceImage(models.Model):
    """Галерея жердин кошумча сүрөттөрү"""
    place = models.ForeignKey(
        TouristPlace, on_delete=models.CASCADE,
        related_name='images', verbose_name="Место"
    )
    image = models.ImageField(upload_to='places/gallery/', verbose_name="Фото")

    class Meta:
        verbose_name = "Фото места"
        verbose_name_plural = "Фото мест"
        # 🔐 PERMISSION: автоматтык add/change/delete/view гана

    def __str__(self):
        return f"Фото для {self.place.title}"


# ========== БАШКЫ БЕТ БЛОКТОРУ ==========
class Advantage(models.Model):
    """Почему нам доверяют?"""
    icon = models.CharField(max_length=50, blank=True, verbose_name="Иконка")
    title = models.CharField(max_length=150, verbose_name="Заголовок")
    description = models.TextField(verbose_name="Описание")
    order = models.IntegerField(default=0, verbose_name="Порядок вывода")

    class Meta:
        verbose_name = "Преимущество"
        verbose_name_plural = "Преимущества"
        ordering = ['order']
        # 🔐 PERMISSION: автоматтык add/change/delete/view_advantage
        # Бул — контент блогу, атайын укук керек эмес

    def __str__(self):
        return self.title


class Review(models.Model):
    """Отзывы о нашей компании"""
    PLATFORM_CHOICES = [
        ('yandex', 'Яндекс Карты'),
        ('2gis', '2ГИС'),
        ('google', 'Google Maps'),
    ]
    author_name = models.CharField(max_length=100, verbose_name="Имя автора")
    rating = models.IntegerField(default=5, verbose_name="Рейтинг (1-5)")
    text = models.TextField(verbose_name="Текст отзыва")
    platform = models.CharField(
        max_length=20, choices=PLATFORM_CHOICES,
        default='yandex', verbose_name="Платформа"
    )
    date = models.DateField(auto_now_add=True, verbose_name="Дата")
    is_published = models.BooleanField(default=True, verbose_name="Опубликован")

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ['-date']
        # ============================================================
        # 🔐 PERMISSION'ДОР — отзывдар менен иштөө
        # ============================================================
        permissions = [
            ("can_publish_review", "⭐ Отзывду жарыялоо (is_published=True)"),
            ("can_hide_review",    "🙈 Отзывду жашыруу"),
            ("can_reply_review",   "💬 Отзывга жооп жазуу"),
        ]

    def __str__(self):
        return f"{self.author_name} — {self.rating}★"


class RentalStep(models.Model):
    """Как происходит аренда автомобиля"""
    step_number = models.IntegerField(verbose_name="Номер шага")
    title = models.CharField(max_length=150, verbose_name="Заголовок")
    description = models.TextField(verbose_name="Описание")
    icon = models.CharField(max_length=50, blank=True, verbose_name="Иконка")

    class Meta:
        verbose_name = "Шаг аренды"
        verbose_name_plural = "Шаги аренды"
        ordering = ['step_number']
        # 🔐 PERMISSION: автоматтык add/change/delete/view_rentalstep
        # Контент блогы — атайын укук керек эмес

    def __str__(self):
        return f"{self.step_number}. {self.title}"


class Promotion(models.Model):
    """Предложения для клиентов — акции"""
    title = models.CharField(max_length=150, verbose_name="Заголовок")
    description = models.TextField(verbose_name="Описание")
    image = models.ImageField(upload_to='promotions/', verbose_name="Фото")
    button_text = models.CharField(max_length=50, blank=True, verbose_name="Текст кнопки")
    is_active = models.BooleanField(default=True, verbose_name="Активна")

    class Meta:
        verbose_name = "Акция"
        verbose_name_plural = "Акции"
        # ============================================================
        # 🔐 PERMISSION'ДОР — акциялар менен иштөө
        # ============================================================
        permissions = [
            ("can_activate_promotion", "🎯 Акцияны иштетүү (is_active=True)"),
            ("can_feature_promotion",  "⭐ Акцияны башкы бетке чыгаруу"),
        ]

    def __str__(self):
        return self.title