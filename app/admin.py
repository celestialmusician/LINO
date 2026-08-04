from django.contrib import admin
from .models import Category, Product, ProductImage, Order, OrderItem, Review

# Admin Panel Custom Branding
admin.site.site_header = "LINO PARFUMS • ADMIN"
admin.site.site_title = "LINO PARFUMS Admin Portal"
admin.site.index_title = "Welcome to LINO Luxury Fragrance Management"


# ==================================================
# PRODUCT GALLERY INLINE
# ==================================================

class ProductImageInline(admin.TabularInline):

    model = ProductImage

    extra = 5

    fields = (
        "image",
        "alt_text",
        "ordering",
    )

    ordering = (
        "ordering",
    )


# ==================================================
# CATEGORY ADMIN
# ==================================================

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "slug",
        "is_active",
    )

    list_display_links = (
        "name",
    )

    list_filter = (
        "is_active",
    )

    search_fields = (
        "name",
        "description",
    )

    prepopulated_fields = {
        "slug": ("name",)
    }

    ordering = (
        "name",
    )


# ==================================================
# PRODUCT ADMIN
# ==================================================

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    inlines = [
        ProductImageInline,
    ]

    list_display = (
        "name",
        "category",
        "price",
        "stock",
        "featured",
        "is_active",
        "created_at",
    )

    list_display_links = (
        "name",
    )

    list_editable = (
        "price",
        "stock",
        "featured",
        "is_active",
    )

    list_filter = (
        "category",
        "featured",
        "is_active",
    )

    search_fields = (
        "name",
        "subtitle",
        "description",
        "story",
    )

    prepopulated_fields = {
        "slug": ("name",)
    }

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    ordering = (
        "-created_at",
    )

    fieldsets = (

        (
            "Basic Information",
            {
                "fields": (
                    "category",
                    "name",
                    "slug",
                    "subtitle",
                    "image",
                )
            }
        ),

        (
            "Pricing & Stock",
            {
                "fields": (
                    "price",
                    "stock",
                    "sku",
                )
            }
        ),

        (
            "Fragrance Details",
            {
                "fields": (
                    "volume",
                    "concentration",
                    "longevity",
                    "top_notes",
                    "heart_notes",
                    "base_notes",
                )
            }
        ),

        (
            "Content",
            {
                "fields": (
                    "description",
                    "story",
                )
            }
        ),

        (
            "Status",
            {
                "fields": (
                    "featured",
                    "is_active",
                )
            }
        ),

        (
            "Dates",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            }
        ),

    )


# ==================================================
# ORDER ITEM INLINE
# ==================================================

class OrderItemInline(admin.TabularInline):

    model = OrderItem

    extra = 0

    readonly_fields = ("product", "quantity", "price_at_order")

    fields = ("product", "quantity", "price_at_order")


# ==================================================
# ORDER ADMIN
# ==================================================

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    inlines = [OrderItemInline]

    list_display = (
        "order_id",
        "first_name",
        "last_name",
        "email",
        "phone",
        "payment_method",
        "total",
        "status",
        "created_at",
    )

    list_display_links = ("order_id",)

    list_editable = ("status",)

    list_filter = ("status", "payment_method", "created_at")

    search_fields = (
        "order_id",
        "first_name",
        "last_name",
        "email",
        "phone",
        "tracking_number",
    )

    readonly_fields = ("order_id", "created_at")

    ordering = ("-created_at",)


# ==================================================
# REVIEW ADMIN
# ==================================================

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):

    list_display = (
        "product",
        "reviewer_name",
        "rating",
        "headline",
        "verified_purchase",
        "is_approved",
        "created_at",
    )

    list_editable = ("is_approved",)

    list_filter = ("rating", "is_approved", "verified_purchase", "created_at")

    search_fields = ("product__name", "reviewer_name", "reviewer_email", "headline", "comment")

    actions = ["approve_reviews", "disapprove_reviews"]

    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)
        self.message_user(request, "Selected reviews approved.")
    approve_reviews.short_description = "Approve selected reviews"

    def disapprove_reviews(self, request, queryset):
        queryset.update(is_approved=False)
        self.message_user(request, "Selected reviews hidden.")
    disapprove_reviews.short_description = "Hide selected reviews"