import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "scentido.settings")
django.setup()

from app.models import Product

def cleanup():
    seen_slugs = set()
    to_delete = []

    for product in Product.objects.all().order_by("id"):
        # Normalize slug base
        clean_slug = product.slug.split("-cat")[0].split("-3q")[0].split("-y8")[0].split("-v")[0].split("-b")[0].split("-c")[0].split("-at")[0]
        
        # Keep clean title-cased names
        product.name = product.name.split(" Cat")[0].split(" Cat")[0].split(" 3")[0].split(" Y")[0].split(" V")[0].split(" B")[0].split(" C")[0].split(" At")[0].upper()
        product.save()

        if product.name in seen_slugs:
            to_delete.append(product)
        else:
            seen_slugs.add(product.name)

    for p in to_delete:
        p.delete()

    print(f"[OK] Cleaned up duplicates. Remaining unique products: {Product.objects.count()}")
    for p in Product.objects.all():
        print(f"  - {p.name} | Category: {p.category.name} | Image: {p.image.url if p.image else 'No image'}")

if __name__ == "__main__":
    cleanup()
