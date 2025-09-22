import sqlite3

# Connect to SQLite database
conn = sqlite3.connect("data.db")
cursor = conn.cursor()

# ------------------------
# Create tables
# ------------------------

# Products table
cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT,
    description TEXT,
    price REAL NOT NULL,
    stock INTEGER DEFAULT 0
);
""")

# Customers table
cursor.execute("""
CREATE TABLE IF NOT EXISTS customers (
    customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    tags TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

# Purchases table
cursor.execute("""
CREATE TABLE IF NOT EXISTS purchases (
    purchase_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    quantity INTEGER DEFAULT 1,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);
""")

# Cart table
cursor.execute("""
CREATE TABLE IF NOT EXISTS cart (
    cart_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    quantity INTEGER DEFAULT 1,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);
""")

# ------------------------
# Insert Products
# ------------------------
products = [
    ("Nike Air Zoom", "Shoes", "Lightweight running shoes", 4500, 20),
    ("Adidas RunFalcon", "Shoes", "Comfortable daily running shoes", 4000, 15),
    ("Puma Velocity", "Shoes", "High-performance sneakers", 4200, 10),
    ("MacBook Air M2", "Electronics", "Laptop for designers and students", 114900, 5),
    ("Apple iPhone 15", "Electronics", "Latest iPhone with A17 chip", 79900, 8),
    ("Zara Black Dress", "Fashion", "Elegant black dress for evening parties", 2499, 12),
    ("Zara Floral Maxi", "Fashion", "Floral black maxi dress", 2899, 10),
    ("Samsung Galaxy S23", "Electronics", "Latest Samsung smartphone", 69900, 10),
    ("Dell XPS 13", "Electronics", "Compact laptop for work and study", 99900, 7),
    ("HP Spectre x360", "Electronics", "Convertible laptop for designers", 109900, 5),
    ("Sony WH-1000XM5", "Electronics", "Noise-cancelling headphones", 24900, 15),
    ("Bose QuietComfort 45", "Electronics", "Premium noise-cancelling headphones", 22900, 12),
    ("Adidas Ultraboost", "Shoes", "High-performance running shoes", 8000, 10),
    ("Nike Revolution 6", "Shoes", "Everyday comfortable running shoes", 4000, 20),
    ("Puma RS-X", "Shoes", "Trendy sneakers for casual wear", 4500, 18),
    ("Zara Summer Shirt", "Fashion", "Light cotton shirt for summer", 1200, 25),
    ("Zara Denim Jeans", "Fashion", "Slim-fit denim jeans", 1999, 20),
    ("Levi's 501 Jeans", "Fashion", "Classic straight-fit jeans", 2999, 15),
    ("H&M Hoodie", "Fashion", "Comfortable cotton hoodie", 1499, 18),
    ("Uniqlo T-Shirt", "Fashion", "Basic crew neck t-shirt", 899, 30),
    ("Apple Watch Series 9", "Electronics", "Smartwatch for fitness and notifications", 39900, 10),
    ("Fitbit Charge 6", "Electronics", "Fitness tracking smartwatch", 12900, 15),
    ("Canon EOS R10", "Electronics", "Mirrorless camera for beginners", 79900, 5),
    ("Nikon Z30", "Electronics", "Compact mirrorless camera", 69900, 6),
    ("Sony Alpha 7C", "Electronics", "Full-frame mirrorless camera", 159900, 3),
    ("Reebok Classic Leather", "Shoes", "Casual everyday sneakers", 4500, 12),
    ("Fila Disruptor", "Shoes", "Chunky sneakers trend", 5000, 10),
    ("H&M Summer Dress", "Fashion", "Floral summer dress", 1799, 20),
    ("Zara Leather Jacket", "Fashion", "Stylish leather jacket", 4999, 8),
    ("Nike Sports Shorts", "Fashion", "Comfortable gym shorts", 1299, 15),
    ("Adidas Sports T-Shirt", "Fashion", "Breathable workout t-shirt", 1399, 20),
    ("Puma Hoodie", "Fashion", "Casual cotton hoodie", 1599, 18),
    ("Apple iPad Air", "Electronics", "Tablet for work and study", 59900, 8)
]

cursor.executemany("""
INSERT INTO products (name, category, description, price, stock)
VALUES (?, ?, ?, ?, ?);
""", products)

# ------------------------
# Insert Customers
# ------------------------
customers = [
    ("Rahul", "rahul@example.com", "student,sports"),
    ("Ananya", "ananya@example.com", "designer,apple_fan"),
    ("Sneha", "sneha@example.com", "fashion,shopping"),
    ("Vikram", "vikram@example.com", "electronics,gaming"),
    ("Priya", "priya@example.com", "student,fashion"),
    ("Rohan", "rohan@example.com", "student,gaming"),
    ("Meera", "meera@example.com", "designer,fashion"),
    ("Karan", "karan@example.com", "electronics,gamer"),
    ("Sana", "sana@example.com", "student,shopping"),
    ("Amit", "amit@example.com", "fitness,sports"),
    ("Neha", "neha@example.com", "fashion,shopping"),
    ("Vivek", "vivek@example.com", "electronics,designer"),
    ("Isha", "isha@example.com", "fashion,student"),
    ("Aditya", "aditya@example.com", "sports,student"),
    ("Anika", "anika@example.com", "electronics,apple_fan")
]

cursor.executemany("""
INSERT INTO customers (name, email, tags)
VALUES (?, ?, ?);
""", customers)

# ------------------------
# Insert some purchase history
# ------------------------
purchases = [
    (1, 1, 1),  # Rahul bought Nike Air Zoom
    (1, 4, 1),  # Rahul bought MacBook Air M2
    (2, 5, 1),  # Ananya bought iPhone 15
    (3, 6, 1),  # Sneha bought Zara Black Dress
    (5, 7, 1),  # Priya bought Zara Floral Maxi
    (6, 8, 1),  # Rohan bought Puma RS-X
    (7, 4, 1),  # Meera bought MacBook Air M2
    (8, 1, 1),  # Karan bought Nike Air Zoom
    (9, 6, 1),  # Sana bought Adidas Ultraboost
    (10, 12, 1), # Amit bought H&M Hoodie
    (11, 14, 1), # Neha bought Apple Watch Series 9
    (12, 9, 1),  # Vivek bought Zara Summer Shirt
    (13, 15, 1), # Isha bought Fitbit Charge 6
    (14, 16, 1), # Aditya bought Canon EOS R10
    (15, 17, 1)  # Anika bought Nikon Z30
]

cursor.executemany("""
INSERT INTO purchases (customer_id, product_id, quantity)
VALUES (?, ?, ?);
""", purchases)

# Commit changes and close
conn.commit()
conn.close()

print("Database created and mock data inserted successfully!")
