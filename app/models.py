from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.db.models import Avg, Count


# ==================================================
# CATEGORY
# ==================================================

class Category(models.Model):

    name = models.CharField(
        max_length=100,
        unique=True
    )

    slug = models.SlugField(
        unique=True,
        blank=True
    )

    description = models.TextField(
        blank=True
    )

    image = models.ImageField(
        upload_to="categories/",
        blank=True,
        null=True
    )

    is_active = models.BooleanField(
        default=True
    )

    class Meta:

        ordering = ["name"]

        verbose_name_plural = "Categories"

    def save(self, *args, **kwargs):

        if not self.slug:

            self.slug = slugify(self.name)

        super().save(*args, **kwargs)

    def __str__(self):

        return self.name


# ==================================================
# PRODUCT
# ==================================================

class Product(models.Model):

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="products"
    )

    name = models.CharField(
        max_length=150
    )

    slug = models.SlugField(
        unique=True,
        blank=True
    )

    subtitle = models.CharField(
        max_length=200,
        blank=True
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    description = models.TextField()

    story = models.TextField(
        blank=True
    )

    image = models.ImageField(
        upload_to="products/"
    )

    volume = models.CharField(
        max_length=50,
        default="100 ml"
    )

    concentration = models.CharField(
        max_length=100,
        default="Eau De Parfum"
    )

    longevity = models.CharField(
        max_length=100,
        default="8 - 10 Hours"
    )

    # ----------------------------------------
    # FRAGRANCE NOTES
    # ----------------------------------------

    top_notes = models.CharField(
        max_length=255,
        blank=True,
        help_text="e.g. Bergamot • Pink Pepper • Cardamom"
    )

    heart_notes = models.CharField(
        max_length=255,
        blank=True,
        help_text="e.g. Cedarwood • Iris • Patchouli"
    )

    base_notes = models.CharField(
        max_length=255,
        blank=True,
        help_text="e.g. Amber • Sandalwood • Musk"
    )

    stock = models.PositiveIntegerField(
        default=0
    )

    sku = models.CharField(
        max_length=50,
        unique=True,
        blank=True
    )

    featured = models.BooleanField(
        default=False
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:

        ordering = ["-created_at"]

    def save(self, *args, **kwargs):

        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            count = 1
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{count}"
                count += 1
            self.slug = slug

        if not self.sku:
            base_sku = f"LINO-{slugify(self.name).upper()}"
            sku = base_sku
            count = 1
            while Product.objects.filter(sku=sku).exclude(pk=self.pk).exists():
                sku = f"{base_sku}-{count}"
                count += 1
            self.sku = sku

        super().save(*args, **kwargs)

    def get_average_rating(self):
        avg = self.reviews.filter(is_approved=True).aggregate(Avg('rating'))['rating__avg']
        return round(avg, 1) if avg else 5.0

    def get_review_count(self):
        return self.reviews.filter(is_approved=True).count()

    @property
    def get_image_url(self):
        if self.image and hasattr(self.image, 'url'):
            try:
                return self.image.url
            except Exception:
                pass
        clean_name = self.name.replace(" ", "-").upper()
        return f"/static/images/products/{clean_name}.png"

    def __str__(self):

        return self.name


# ==================================================
# PRODUCT GALLERY
# ==================================================

class ProductImage(models.Model):

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="gallery"
    )

    image = models.ImageField(
        upload_to="products/gallery/"
    )

    alt_text = models.CharField(
        max_length=150,
        blank=True
    )

    ordering = models.PositiveIntegerField(
        default=0
    )

    class Meta:

        ordering = ["ordering"]

        verbose_name = "Product Image"

        verbose_name_plural = "Product Gallery"

    def __str__(self):

        return f"{self.product.name} - Gallery Image"


# ==================================================
# ORDER
# ==================================================

class Order(models.Model):

    STATUS_CHOICES = [
        ("pending",   "Pending"),
        ("confirmed", "Confirmed"),
        ("shipped",   "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]

    PAYMENT_CHOICES = [
        ("cod", "Cash on Delivery"),
        ("upi", "UPI / GPay / PhonePe"),
        ("card", "Credit / Debit Card"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders"
    )

    order_id = models.CharField(
        max_length=20,
        unique=True,
        blank=True
    )

    # ---- Customer Details ----

    first_name = models.CharField(max_length=100)
    last_name  = models.CharField(max_length=100)
    email      = models.EmailField()
    phone      = models.CharField(max_length=20)
    address    = models.TextField()
    city       = models.CharField(max_length=100)
    state      = models.CharField(max_length=100)
    pincode    = models.CharField(max_length=10)

    # ---- Financials & Payment ----

    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_CHOICES,
        default="cod"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    tracking_number = models.CharField(
        max_length=50,
        blank=True
    )

    notes = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:

        ordering = ["-created_at"]

    def save(self, *args, **kwargs):

        if not self.order_id:

            import random
            self.order_id = f"SCN{random.randint(100000, 999999)}"

        super().save(*args, **kwargs)

    def __str__(self):

        return f"Order {self.order_id} – {self.first_name} {self.last_name}"


# ==================================================
# ORDER ITEM
# ==================================================

class OrderItem(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        related_name="order_items"
    )

    quantity = models.PositiveIntegerField(default=1)

    price_at_order = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    def get_subtotal(self):
        return self.quantity * self.price_at_order

    def __str__(self):
        product_name = self.product.name if self.product else "Deleted Product"
        return f"{self.order.order_id} – {product_name} x{self.quantity}"


# ==================================================
# REVIEW & RATING
# ==================================================

class Review(models.Model):

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="reviews"
    )

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviews"
    )

    reviewer_name = models.CharField(
        max_length=100
    )

    reviewer_email = models.EmailField()

    rating = models.PositiveSmallIntegerField(
        default=5,
        help_text="Rating from 1 to 5"
    )

    headline = models.CharField(
        max_length=150,
        blank=True
    )

    comment = models.TextField()

    verified_purchase = models.BooleanField(
        default=False
    )

    is_approved = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.product.name} - {self.rating}★ by {self.reviewer_name}"