from django.db import models
from django.utils.text import slugify


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

            self.slug = slugify(self.name)

        if not self.sku:

            self.sku = f"LINO-{slugify(self.name).upper()}"

        super().save(*args, **kwargs)

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