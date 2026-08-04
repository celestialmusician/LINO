import os
import django
from django.core.files import File

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "scentido.settings")
django.setup()

from app.models import Category, Product

PRODUCTS_DATA = [
    {
        "name": "MARJ",
        "category": "Signature Collection",
        "price": 4999.00,
        "subtitle": "Eau De Parfum • 100ml",
        "description": "An opulent fusion of rare spices, rich leather, and velvety amber. Crafted for those who command respect and leave an indelible impression of timeless grandeur.",
        "story": "Inspired by the vast golden dunes at sunset, MARJ encapsulates the spirit of regal mystery and eternal warmth.",
        "image_filename": "MARJ.png",
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
        "category": "Attar",
        "price": 3499.00,
        "subtitle": "Concentrated Perfume Oil • 50ml",
        "description": "A delicate, hauntingly beautiful harmony of blooming jasmine, sweet vanilla, and warm white musk. Elegance captured in a single drop.",
        "story": "Subaya evokes early morning strolls through royal Andalusian gardens where morning dew meets rare blossoms.",
        "image_filename": "SUBAYA.png",
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
        "category": "Oudh",
        "price": 5999.00,
        "subtitle": "Pure Oud Wood Extract • 100ml",
        "description": "Intense, deep, and unapologetically royal. Sourced from aged Agarwood trees and blended with smoked incense and exotic resins.",
        "story": "A tribute to ancient Arabian perfumery traditions handed down through generations of master artisans.",
        "image_filename": "OUDH-KUWAITY.png",
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
        "category": "Musk",
        "price": 2999.00,
        "subtitle": "Heavenly Botanical Nectar • 100ml",
        "description": "A garden of paradise in a bottle. Fresh green notes mingled with wild mint, lotus petals, and pure golden honey notes.",
        "story": "Literal translation 'Gardens of Paradise', crafted to evoke peace, purity, and spiritual elevation.",
        "image_filename": "JANNATH-AL-FIRDOUS.png",
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
        "category": "Floral",
        "price": 3899.00,
        "subtitle": "Radiant Amber Floral • 100ml",
        "description": "Luminous citrus top notes giving way to a heart of orange blossom and honeyed plums, resting on a base of warm patchouli.",
        "story": "Noora means 'Divine Light' — created to shine with brilliance and captivating grace in any room.",
        "image_filename": "NOORA.png",
        "volume": "100 ml",
        "concentration": "Eau De Parfum",
        "longevity": "10 - 12 Hours",
        "top_notes": "Orange • Tangerine • Honey",
        "heart_notes": "Tuberose • Orange Blossom • Plum",
        "base_notes": "Patchouli • Dark Chocolate • Vanilla",
        "featured": False,
        "stock": 30,
    },
    {
        "name": "MUSK RIZAL",
        "category": "Musk",
        "price": 4299.00,
        "subtitle": "Velvet Royal Musk • 100ml",
        "description": "Silky, sensual, and intoxicatingly smooth white musk paired with powdery iris and warm Tonka bean.",
        "story": "Designed as an intimate second-skin fragrance that lingers long after you leave.",
        "image_filename": "MUSK-RIZAL.png",
        "volume": "100 ml",
        "concentration": "Extrait De Parfum",
        "longevity": "12 - 14 Hours",
        "top_notes": "Powdery Iris • Violet Leaf • Aldehydes",
        "heart_notes": "Royal White Musk • Heliotrope",
        "base_notes": "Tonka Bean • Sandalwood • Cashmere",
        "featured": False,
        "stock": 20,
    },
    {
        "name": "ONE MILLION",
        "category": "Perfume Spray",
        "price": 3999.00,
        "subtitle": "Spiced Gold Accord • 100ml",
        "description": "Bold blood mandarin, spicy cinnamon, and seductive leather in a gold-standard luxury composition.",
        "story": "For the ambitious visionary who settles for nothing less than perfection.",
        "image_filename": "ONE MILLION.png",
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

def seed():
    source_dir = os.path.join(django.conf.settings.BASE_DIR, "static", "images", "products")
    
    print("Seeding Categories and Products...")
    for data in PRODUCTS_DATA:
        cat_name = data.pop("category")
        category, _ = Category.objects.get_or_create(name=cat_name)
        
        img_name = data.pop("image_filename")
        img_path = os.path.join(source_dir, img_name)
        
        product, created = Product.objects.get_or_create(
            name=data["name"],
            defaults={
                "category": category,
                "price": data["price"],
                "subtitle": data["subtitle"],
                "description": data["description"],
                "story": data["story"],
                "volume": data["volume"],
                "concentration": data["concentration"],
                "longevity": data["longevity"],
                "top_notes": data["top_notes"],
                "heart_notes": data["heart_notes"],
                "base_notes": data["base_notes"],
                "featured": data["featured"],
                "stock": data["stock"],
                "is_active": True,
            }
        )
        
        if os.path.exists(img_path) and (created or not product.image):
            with open(img_path, "rb") as f:
                product.image.save(img_name, File(f), save=True)
            print(f"  [+] Saved image for {product.name}")

        print(f"  {'Created' if created else 'Already exists'}: {product.name} (Rs. {product.price})")

    print("\n[OK] Database seeding complete! Total Products:", Product.objects.count())

if __name__ == "__main__":
    seed()
