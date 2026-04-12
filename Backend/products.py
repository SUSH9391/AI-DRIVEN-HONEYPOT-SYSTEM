import random

# List of product categories
CATEGORIES = [
    "Electronics",
    "Clothing",
    "Home & Kitchen",
    "Beauty & Personal Care",
    "Sports & Outdoors",
    "Toys & Games"
]

# List of product names by category
PRODUCT_NAMES = {
    "Electronics": [
        "Ultra HD Smart TV",
        "Wireless Noise-Cancelling Headphones",
        "Professional DSLR Camera",
        "Gaming Laptop",
        "Smartphone with 108MP Camera",
        "Bluetooth Soundbar",
        "Smart Home Hub",
        "Wireless Charging Pad",
        "Fitness Tracker",
        "Portable SSD Drive"
    ],
    "Clothing": [
        "Premium Cotton T-Shirt",
        "Slim-Fit Jeans",
        "Casual Button-Down Shirt",
        "Wool Blend Sweater",
        "Lightweight Jacket",
        "Athletic Running Shoes",
        "Leather Belt",
        "Formal Business Suit",
        "Comfortable Lounge Pants",
        "Designer Sunglasses"
    ],
    "Home & Kitchen": [
        "Stainless Steel Cookware Set",
        "Robot Vacuum Cleaner",
        "Air Purifier",
        "Egyptian Cotton Bed Sheets",
        "Espresso Coffee Machine",
        "Non-Stick Baking Set",
        "Smart Refrigerator",
        "Memory Foam Mattress",
        "Ceramic Dinner Set",
        "Stand Mixer"
    ],
    "Beauty & Personal Care": [
        "Anti-Aging Face Serum",
        "Professional Hair Dryer",
        "Electric Toothbrush",
        "Luxury Perfume",
        "Organic Shampoo & Conditioner",
        "Men's Grooming Kit",
        "Makeup Brush Set",
        "Facial Cleansing Device",
        "Natural Skincare Kit",
        "Beard Trimmer"
    ],
    "Sports & Outdoors": [
        "Yoga Mat",
        "Mountain Bike",
        "Tennis Racket",
        "Camping Tent",
        "Adjustable Dumbbells",
        "Golf Club Set",
        "Hiking Backpack",
        "Basketball",
        "Fishing Rod",
        "Running Shoes"
    ],
    "Toys & Games": [
        "Building Blocks Set",
        "Remote Control Car",
        "Board Game Collection",
        "Educational Science Kit",
        "Plush Teddy Bear",
        "Drone with Camera",
        "Puzzle Set",
        "Action Figure",
        "Art & Craft Kit",
        "Video Game Console"
    ]
}

# List of brands by category
BRANDS = {
    "Electronics": ["Samsung", "Sony", "Apple", "LG", "Bose", "Canon", "Dell", "HP", "Lenovo", "JBL"],
    "Clothing": ["Nike", "Adidas", "Levi's", "H&M", "Zara", "Gap", "Calvin Klein", "Ralph Lauren", "Puma", "Under Armour"],
    "Home & Kitchen": ["Cuisinart", "Dyson", "KitchenAid", "Ninja", "Calphalon", "OXO", "Breville", "Shark", "Instant Pot", "Vitamix"],
    "Beauty & Personal Care": ["L'Oreal", "Neutrogena", "Dove", "Olay", "Nivea", "Pantene", "Gillette", "Maybelline", "Garnier", "Cetaphil"],
    "Sports & Outdoors": ["Wilson", "Coleman", "The North Face", "Columbia", "Spalding", "Callaway", "Schwinn", "Speedo", "Yeti", "Patagonia"],
    "Toys & Games": ["LEGO", "Hasbro", "Mattel", "Fisher-Price", "Nintendo", "Melissa & Doug", "Nerf", "Barbie", "Hot Wheels", "Play-Doh"]
}

# Product descriptions by category
DESCRIPTIONS = {
    "Electronics": [
        "Experience cutting-edge technology with this premium device.",
        "Enhance your digital lifestyle with superior performance and reliability.",
        "State-of-the-art features designed for the modern tech enthusiast.",
        "Sleek design meets powerful functionality in this must-have gadget.",
        "The perfect balance of innovation, quality, and user-friendly features."
    ],
    "Clothing": [
        "Made with premium materials for exceptional comfort and durability.",
        "Stylish design that transitions seamlessly from casual to formal occasions.",
        "Expertly crafted with attention to detail and quality stitching.",
        "Contemporary fashion that makes a statement while ensuring comfort.",
        "Versatile addition to any wardrobe, designed for the fashion-conscious individual."
    ],
    "Home & Kitchen": [
        "Transform your living space with this elegant and functional addition.",
        "Designed to make everyday tasks easier while enhancing your home's aesthetic.",
        "Combines modern technology with timeless design for the contemporary home.",
        "Premium quality construction ensures long-lasting performance and reliability.",
        "The perfect blend of style, functionality, and durability for your home."
    ],
    "Beauty & Personal Care": [
        "Formulated with premium ingredients for exceptional results.",
        "Dermatologist-tested and approved for all skin types.",
        "Experience the luxury of professional-grade beauty products at home.",
        "Enhance your natural beauty with this gentle yet effective product.",
        "Scientifically developed to deliver visible results and lasting benefits."
    ],
    "Sports & Outdoors": [
        "Engineered for peak performance in all conditions.",
        "Professional-grade equipment designed for enthusiasts and athletes alike.",
        "Durable construction meets innovative design for superior performance.",
        "Enhance your outdoor experience with this essential gear.",
        "Tested and approved by professional athletes for reliability and performance."
    ],
    "Toys & Games": [
        "Stimulates creativity and imagination through interactive play.",
        "Educational design promotes learning while providing hours of fun.",
        "Durable construction stands up to energetic play sessions.",
        "Encourages development of fine motor skills and problem-solving abilities.",
        "Creates memorable experiences for children of all ages."
    ]
}

# Placeholder image URLs by category
PLACEHOLDER_IMAGES = {
    "Electronics": [
        "https://via.placeholder.com/300x300.png?text=Electronics+Product",
        "https://via.placeholder.com/300x300.png?text=Smart+Device",
        "https://via.placeholder.com/300x300.png?text=Tech+Gadget",
        "https://via.placeholder.com/300x300.png?text=Digital+Device",
        "https://via.placeholder.com/300x300.png?text=Modern+Electronics"
    ],
    "Clothing": [
        "https://via.placeholder.com/300x300.png?text=Fashion+Item",
        "https://via.placeholder.com/300x300.png?text=Stylish+Clothing",
        "https://via.placeholder.com/300x300.png?text=Apparel",
        "https://via.placeholder.com/300x300.png?text=Trendy+Outfit",
        "https://via.placeholder.com/300x300.png?text=Clothing+Piece"
    ],
    "Home & Kitchen": [
        "https://via.placeholder.com/300x300.png?text=Home+Product",
        "https://via.placeholder.com/300x300.png?text=Kitchen+Item",
        "https://via.placeholder.com/300x300.png?text=Household+Good",
        "https://via.placeholder.com/300x300.png?text=Home+Appliance",
        "https://via.placeholder.com/300x300.png?text=Kitchen+Tool"
    ],
    "Beauty & Personal Care": [
        "https://via.placeholder.com/300x300.png?text=Beauty+Product",
        "https://via.placeholder.com/300x300.png?text=Skincare+Item",
        "https://via.placeholder.com/300x300.png?text=Personal+Care",
        "https://via.placeholder.com/300x300.png?text=Cosmetic+Product",
        "https://via.placeholder.com/300x300.png?text=Grooming+Item"
    ],
    "Sports & Outdoors": [
        "https://via.placeholder.com/300x300.png?text=Sports+Equipment",
        "https://via.placeholder.com/300x300.png?text=Outdoor+Gear",
        "https://via.placeholder.com/300x300.png?text=Fitness+Item",
        "https://via.placeholder.com/300x300.png?text=Athletic+Equipment",
        "https://via.placeholder.com/300x300.png?text=Sports+Gear"
    ],
    "Toys & Games": [
        "https://via.placeholder.com/300x300.png?text=Toy+Item",
        "https://via.placeholder.com/300x300.png?text=Game+Product",
        "https://via.placeholder.com/300x300.png?text=Kids+Toy",
        "https://via.placeholder.com/300x300.png?text=Educational+Toy",
        "https://via.placeholder.com/300x300.png?text=Fun+Game"
    ]
}

def generate_product(product_id=None):
    """Generate a single fake product"""
    if product_id is None:
        product_id = random.randint(1, 1000)
        
    category = random.choice(CATEGORIES)
    name = random.choice(PRODUCT_NAMES[category])
    brand = random.choice(BRANDS[category])
    description = random.choice(DESCRIPTIONS[category])
    price = round(random.uniform(9.99, 999.99), 2)
    rating = round(random.uniform(3.0, 5.0), 1)
    stock = random.randint(0, 100)
    image_url = random.choice(PLACEHOLDER_IMAGES[category])
    
    return {
        "id": product_id,
        "name": name,
        "brand": brand,
        "category": category,
        "description": description,
        "price": price,
        "rating": rating,
        "stock": stock,
        "image_url": image_url
    }

def generate_products(count=10):
    """Generate multiple fake products"""
    products = []
    for i in range(1, count + 1):
        products.append(generate_product(i))
    return products

# In-memory product database
PRODUCTS = generate_products(20)

def get_product(product_id):
    """Get a product by ID"""
    for product in PRODUCTS:
        if product["id"] == product_id:
            return product
    return None

def get_products(category=None, limit=None):
    """Get all products, optionally filtered by category"""
    if category:
        filtered = [p for p in PRODUCTS if p["category"].lower() == category.lower()]
    else:
        filtered = PRODUCTS
        
    if limit:
        return filtered[:limit]
    return filtered