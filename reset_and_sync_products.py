import os
import django
import shutil
from django.core.files import File

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "scentido.settings")
django.setup()

from app.models import Category, Product, ProductImage

PRODUCTS_CONFIG = [
    {
        "name": "MARJ",
        "category_name": "Perfumes",
        "price": 4999.00,
        "subtitle": "Eau De Parfum • 100ml",
        "description": "An opulent fusion of rare spices, rich leather, and velvety amber. Crafted for those who command respect and leave an indelible impression of timeless grandeur.",
        "story": "Inspired by the vast golden dunes at sunset, MARJ encapsulates the spirit of regal mystery and eternal warmth.",
        "filename": "MARJ.png",
        "volume": "100 ml",
        "concentration": "Eau De Parfum",
        "longevity": "10 - 12 Hours",
        "top_notes": "Bergamot • Pink Pepper • Saffron",
        "heart_notes": "Damask Rose • Cedarwood • Oud",
        "base_notes": "Ambergris • Leather • Sandalwood",
        "featured": True,
        "stock": 25,
    },
    {
        "name": "SUBAYA",
        "category_name": "Attar",
        "price": 3499.00,
        "subtitle": "Concentrated Perfume Oil • 50ml",
        "description": "A delicate, hauntingly beautiful harmony of blooming jasmine, sweet vanilla, and warm white musk. Elegance captured in a single drop.",
        "story": "Subaya evokes early morning strolls through royal Andalusian gardens where morning dew meets rare blossoms.",
        "filename": "SUBAYA.png",
        "volume": "50 ml",
        "concentration": "Concentrated Perfume Oil",
        "longevity": "12 - 14 Hours",
        "top_notes": "Mandarin • White Floral • Peach",
        "heart_notes": "Jasmine Sambac • Ylang Ylang • Iris",
        "base_notes": "Bourbon Vanilla • White Musk • Cedar",
        "featured": True,
        "stock": 40,
    },
    {
        "name": "OUDH KUWAITY",
        "category_name": "Perfumes",
        "price": 5999.00,
        "subtitle": "Pure Oud Wood Extract • 100ml",
        "description": "Intense, deep, and unapologetically royal. Sourced from aged Agarwood trees and blended with smoked incense and exotic resins.",
        "story": "A tribute to ancient Arabian perfumery traditions handed down through generations of master artisans.",
        "filename": "OUDH-KUWAITY.png",
        "volume": "100 ml",
        "concentration": "Extrait De Parfum",
        "longevity": "14 - 16 Hours",
        "top_notes": "Smoked Incense • Cardamom • Nutmeg",
        "heart_notes": "Kuwaiti Oud • Patchouli • Guaiac Wood",
        "base_notes": "Dark Amber • Vetiver • Labdanum",
        "featured": True,
        "stock": 15,
    },
    {
        "name": "JANNATH AL FIRDOUS",
        "category_name": "Attar",
        "price": 2999.00,
        "subtitle": "Heavenly Botanical Nectar • 100ml",
        "description": "A garden of paradise in a bottle. Fresh green notes mingled with wild mint, lotus petals, and pure golden honey notes.",
        "story": "Literal translation 'Gardens of Paradise', crafted to evoke peace, purity, and spiritual elevation.",
        "filename": "JANNATH-AL-FIRDOUS.png",
        "volume": "100 ml",
        "concentration": "Eau De Parfum",
        "longevity": "8 - 10 Hours",
        "top_notes": "Green Apple • Wild Mint • Basil",
        "heart_notes": "Lotus • Lily of the Valley • Cinnamon",
        "base_notes": "Golden Honey • Oakmoss • Musk",
        "featured": True,
        "stock": 50,
    },
    {
        "name": "NOORA",
        "category_name": "Attar",
        "price": 3899.00,
        "subtitle": "Radiant Amber Floral • 100ml",
        "description": "Luminous citrus top notes giving way to a heart of orange blossom and honeyed plums, resting on a base of warm patchouli.",
        "story": "Noora means 'Divine Light' — created to shine with brilliance and captivating grace in any room.",
        "filename": "NOORA.png",
        "volume": "100 ml",
        "concentration": "Eau De Parfum",
        "longevity": "10 - 12 Hours",
        "top_notes": "Orange • Tangerine • Honey",
        "heart_notes": "Tuberose • Orange Blossom • Plum",
        "base_notes": "Patchouli • Dark Chocolate • Vanilla",
        "featured": True,
        "stock": 30,
    },
    {
        "name": "MUSK RIZAL",
        "category_name": "Attar",
        "price": 4299.00,
        "subtitle": "Velvet Royal Musk • 100ml",
        "description": "Silky, sensual, and intoxicatingly smooth white musk paired with powdery iris and warm Tonka bean.",
        "story": "Designed as an intimate second-skin fragrance that lingers long after you leave.",
        "filename": "MUSK-RIZAL.png",
        "volume": "100 ml",
        "concentration": "Extrait De Parfum",
        "longevity": "12 - 14 Hours",
        "top_notes": "Powdery Iris • Violet Leaf • Aldehydes",
        "heart_notes": "Royal White Musk • Heliotrope",
        "base_notes": "Tonka Bean • Sandalwood • Cashmere",
        "featured": True,
        "stock": 20,
    },
    {
        "name": "ONE MILLION",
        "category_name": "Perfumes",
        "price": 3999.00,
        "subtitle": "Spiced Gold Accord • 100ml",
        "description": "Bold blood mandarin, spicy cinnamon, and seductive leather in a gold-standard luxury composition.",
        "story": "For the ambitious visionary who settles for nothing less than perfection.",
        "filename": "ONE MILLION.png",
        "volume": "100 ml",
        "concentration": "Eau De Parfum",
        "longevity": "10 - 12 Hours",
        "top_notes": "Blood Mandarin • Grapefruit • Peppermint",
        "heart_notes": "Absolute Rose • Cinnamon • Spices",
        "base_notes": "Blond Leather • Tonka Bean • Amber",
        "featured": True,
        "stock": 35,
    },
]

def reset_products():
    base_dir = django.conf.settings.BASE_DIR
    static_images_dir = os.path.join(base_dir, "static", "images", "products")
    media_dir = os.path.join(base_dir, "media", "products")
    os.makedirs(media_dir, exist_ok=True)

    # Ensure 4 standard categories exist
    categories = {}
    for cat_name in ["Attar", "Bahoor", "Burner", "Perfumes"]:
        cat, _ = Category.objects.get_or_create(name=cat_name)
        categories[cat_name] = cat

    for item in PRODUCTS_CONFIG:
        cat_obj = categories.get(item["category_name"], categories["Perfumes"])
        src_path = os.path.join(static_images_dir, item["filename"])
        
        # Avoid wiping DB on every deploy if products already exist
        if not Product.objects.filter(name__iexact=item["name"]).exists():
            product = Product(
                name=item["name"],
                category=cat_obj,
                price=item["price"],
                subtitle=item["subtitle"],
                description=item["description"],
                story=item["story"],
                volume=item["volume"],
                concentration=item["concentration"],
                longevity=item["longevity"],
                top_notes=item["top_notes"],
                heart_notes=item["heart_notes"],
                base_notes=item["base_notes"],
                featured=item["featured"],
                stock=item["stock"],
                is_active=True,
            )

            if os.path.exists(src_path):
                with open(src_path, "rb") as f:
                    clean_filename = item["filename"].replace(" ", "_")
                    product.image.save(clean_filename, File(f), save=False)
            
            product.save()
            print(f"  [+] Synced missing product: {product.name}")
        else:
            print(f"  [=] Product exists: {item['name']}")

    print("\n[OK] Product sync complete! Total Products:", Product.objects.count())

if __name__ == "__main__":
    reset_products()
