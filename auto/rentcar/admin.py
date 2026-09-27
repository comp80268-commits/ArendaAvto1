from django.contrib import admin
from .models import (
    # Унаалар
    Car, CarImage, CarPrice,
    ExtraService,
    Booking,
    # Бурятия
    TouristPlace, TouristPlaceImage,
    # Башкы бет блоктору
    Advantage, Review, RentalStep, Promotion,
)


# ============================================================
# ========== INLINE'ДАР (галереялар үчүн) ===================
# ============================================================
class CarImageInline(admin.TabularInline):
    """Унаанын галереясын түздөн-түз Car баракчасында кошуу"""
    model = CarImage
    extra = 1


class CarPriceInline(admin.TabularInline):
    """Унаанын баа таблицасын түздөн-түз Car баракчасында кошуу"""
    model = CarPrice
    extra = 1


class TouristPlaceImageInline(admin.TabularInline):
    """Жердин галереясын түздөн-түз TouristPlace баракчасында кошуу"""
    model = TouristPlaceImage
    extra = 1


# ============================================================
# ========== УНААЛАР =========================================
# ============================================================
@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price_per_day', 'brand', 'body_type', 'is_available')
    list_editable = ('price_per_day', 'is_available')
    list_filter = ('brand', 'body_type', 'transmission', 'drive', 'is_available')
    search_fields = ('name', 'brand', 'short_description')
    inlines = [CarImageInline, CarPriceInline]   # 👈 галерея + баалар
    list_per_page = 20

    # 🔐 PERMISSION: admin панелде колдонуучуга төмөнкү укуктарды бере аласың:
    #   - add_car / change_car / delete_car / view_car
    #   - can_view_price, can_publish_car, can_hide_car


@admin.register(CarImage)
class CarImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'car', 'image')
    search_fields = ('car__name',)
    # 🔐 PERMISSION: add_carimage / change_carimage / delete_carimage / view_carimage


@admin.register(CarPrice)
class CarPriceAdmin(admin.ModelAdmin):
    list_display = ('id', 'car', 'days_from', 'days_to', 'price_per_day')
    list_filter = ('car',)
    search_fields = ('car__name',)
    # 🔐 PERMISSION: add_carprice / change_carprice / delete_carprice / view_carprice
    #   + can_change_price


# ============================================================
# ========== КОШУМЧА КЫЗМАТТАР ==============================
# ============================================================
@admin.register(ExtraService)
class ExtraServiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'is_free')
    list_editable = ('price', 'is_free')
    list_filter = ('is_free',)
    search_fields = ('name',)
    # 🔐 PERMISSION: add/change/delete/view_extraservice


# ============================================================
# ========== БРОНДОО =========================================
# ============================================================
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'customer_name', 'customer_phone',
        'car', 'start_date', 'end_date',
        'total_price', 'created_at'
    )
    list_filter = ('delivery_place', 'start_date', 'created_at')
    search_fields = ('customer_name', 'customer_phone', 'car__name')
    readonly_fields = ('total_price', 'created_at')
    filter_horizontal = ('extra_services',)
    date_hierarchy = 'created_at'
    list_per_page = 30
    # 🔐 PERMISSION: add/change/delete/view_booking
    #   + can_view_all_bookings, can_confirm_booking,
    #     can_cancel_booking, can_export_bookings


# ============================================================
# ========== БУРЯТИЯ =========================================
# ============================================================
@admin.register(TouristPlace)
class TouristPlaceAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'duration', 'distance')
    search_fields = ('title', 'short_description')
    filter_horizontal = ('recommended_cars',)
    inlines = [TouristPlaceImageInline]   # 👈 галерея
    # 🔐 PERMISSION: add/change/delete/view_touristplace
    #   + can_publish_place, can_feature_place


@admin.register(TouristPlaceImage)
class TouristPlaceImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'place', 'image')
    search_fields = ('place__title',)
    # 🔐 PERMISSION: add/change/delete/view_touristplaceimage


# ============================================================
# ========== БАШКЫ БЕТ БЛОКТОРУ =============================
# ============================================================
@admin.register(Advantage)
class AdvantageAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'title', 'icon')
    list_editable = ('order',)
    search_fields = ('title',)
    ordering = ('order',)
    # 🔐 PERMISSION: add/change/delete/view_advantage


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'author_name', 'rating', 'platform', 'date', 'is_published')
    list_editable = ('is_published',)
    list_filter = ('platform', 'rating', 'is_published')
    search_fields = ('author_name', 'text')
    date_hierarchy = 'date'
    # 🔐 PERMISSION: add/change/delete/view_review
    #   + can_publish_review, can_hide_review, can_reply_review


@admin.register(RentalStep)
class RentalStepAdmin(admin.ModelAdmin):
    list_display = ('id', 'step_number', 'title', 'icon')
    list_editable = ('step_number',)
    search_fields = ('title',)
    ordering = ('step_number',)
    # 🔐 PERMISSION: add/change/delete/view_rentalstep


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'button_text', 'is_active')
    list_editable = ('is_active',)
    list_filter = ('is_active',)
    search_fields = ('title',)
    # 🔐 PERMISSION: add/change/delete/view_promotion
    #   + can_activate_promotion, can_feature_promotion