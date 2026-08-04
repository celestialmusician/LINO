import os
import django
from django.core.files import File

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "scentido.settings")
django.setup()

from app.models import Category, Product

# User defined categories: Attar, Bahoor, Burner, Perfumes
CATEGORIES = [
    {"name": "Attar", "slug": "attar"},
    {"name": "Bahoor", "slug": "bahoor"},
    {"name": "Burner", "slug": "burner"},
    {"name": "Perfumes", "slug": "perfume-spray"},
]

def sync_categories():
    print("Syncing Categories...")
    cat_objs = {}
    for cat_data in CATEGORIES:
        category, created = Category.objects.get_or_create(
            name=cat_data["name"],
            defaults={"slug": cat_data["slug"], "is_active": True}
        )
        if not category.slug:
            category.slug = cat_data["slug"]
            category.save()
        cat_objs[cat_data["name"]] = category
        print(f"  Category: {category.name} (slug: {category.slug})")

    # Map existing products to these 4 categories if needed
    perfumes_cat = cat_objs["Perfumes"]
    attar_cat = cat_objs["Attar"]

    updated_count = 0
    for product in Product.objects.all():
        if product.category.name not in cat_objs:
            # Reassign to closest matching category
            if "attar" in product.name.lower() or "oil" in product.subtitle.lower():
                product.category = attar_cat
            else:
                product.category = perfumes_cat
            product.save()
            updated_count += 1

    print(f"Re-assigned {updated_count} products to match standard categories.")
    print("[OK] Category sync completed successfully!")

if __name__ == "__main__":
    sync_categories()
