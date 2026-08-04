import os
import django
from django.core.files import File

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "scentido.settings")
django.setup()

from app.models import Category, Product

# Standard categories
CATEGORIES_MAP = {
    "Attar": ["attar", "oil", "subaya", "jannath"],
    "Bahoor": ["bahoor", "bukhoor", "incense"],
    "Burner": ["burner", "censer", "bakhoor burner"],
    "Perfumes": ["perfume", "spray", "marj", "oudh", "noora", "musk", "one million", "blanc", "noir", "oud royale"],
}

DEFAULT_NOTE_MAP = {
    "MARJ": ("Bergamot • Pink Pepper", "Damask Rose • Oud", "Ambergris • Leather"),
    "SUBAYA": ("Mandarin • White Floral", "Jasmine Sambac • Iris", "Bourbon Vanilla • White Musk"),
    "OUDH KUWAITY": ("Smoked Incense • Cardamom", "Kuwaiti Oud • Patchouli", "Dark Amber • Vetiver"),
    "JANNATH AL FIRDOUS": ("Green Apple • Wild Mint", "Lotus • Lily of the Valley", "Golden Honey • Oakmoss"),
    "NOORA": ("Orange • Honey", "Tuberose • Orange Blossom", "Patchouli • Vanilla"),
    "MUSK RIZAL": ("Powdery Iris • Aldehydes", "Royal White Musk", "Tonka Bean • Sandalwood"),
    "ONE MILLION": ("Blood Mandarin • Mint", "Absolute Rose • Cinnamon", "Blond Leather • Amber"),
    "BLANC": ("White Tea • Bergamot", "Neroli • Orange Blossom", "White Amber • Soft Musk"),
    "NOIR": ("Black Pepper • Bergamot", "Smoked Vetiver • Tobacco", "Dark Ebony Wood • Leather"),
    "OUD ROYALE": ("Taif Rose • Saffron", "Royal Cambodian Oud", "Golden Amber • Musk"),
}

def clean_name_from_filename(filename):
    name_without_ext = os.path.splitext(filename)[0]
    clean = name_without_ext.replace("-", " ").replace("_", " ").title()
    return clean

def auto_assign_category(name):
    name_lower = name.lower()
    for cat_name, keywords in CATEGORIES_MAP.items():
        if any(kw in name_lower for kw in keywords):
            cat_obj, _ = Category.objects.get_or_create(name=cat_name)
            return cat_obj
    cat_obj, _ = Category.objects.get_or_create(name="Perfumes")
    return cat_obj

def run_import():
    base_dir = django.conf.settings.BASE_DIR
    search_dirs = [
        os.path.join(base_dir, "static", "images", "products"),
        os.path.join(base_dir, "static", "images", "perfumes"),
        os.path.join(base_dir, "media", "products"),
    ]

    print("Scanning folders for product images...")

    processed_files = set()
    added_count = 0

    for d in search_dirs:
        if not os.path.exists(d):
            continue

        for fname in os.listdir(d):
            if not fname.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                continue

            if fname in processed_files or fname.startswith("test"):
                continue

            processed_files.add(fname)
            filepath = os.path.join(d, fname)
            product_name = clean_name_from_filename(fname)
            category = auto_assign_category(product_name)

            notes = DEFAULT_NOTE_MAP.get(
                product_name.upper(),
                ("Citrus • Fresh Spices", "Floral Accord • Cedarwood", "Amber • White Musk")
            )

            product, created = Product.objects.get_or_create(
                name=product_name,
                defaults={
                    "category": category,
                    "price": 3999.00,
                    "subtitle": f"{product_name} • Eau De Parfum",
                    "description": f"An exquisite fragrance embodying luxury and sophistication. Crafted with premium ingredients for an unforgettable signature trail.",
                    "story": f"Inspired by royal Heritage, {product_name} delivers an enchanting olfactory journey.",
                    "volume": "100 ml",
                    "concentration": "Eau De Parfum",
                    "longevity": "10 - 12 Hours",
                    "top_notes": notes[0],
                    "heart_notes": notes[1],
                    "base_notes": notes[2],
                    "featured": True,
                    "stock": 25,
                    "is_active": True,
                }
            )

            if created or not product.image:
                with open(filepath, "rb") as f:
                    product.image.save(fname, File(f), save=True)
                print(f"  [+] Saved image & created: {product_name} ({category.name})")
                added_count += 1
            else:
                print(f"  [=] Product exists: {product_name}")

    print(f"\n[OK] Import complete! Total products in database: {Product.objects.count()}")

if __name__ == "__main__":
    run_import()
