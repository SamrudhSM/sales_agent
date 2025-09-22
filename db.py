import sqlite3

# Connect to the database
conn = sqlite3.connect("data.db")
cursor = conn.cursor()

# ------------------------
# Insert mock products
# ------------------------
products = [
    ("Nike Air Zoom", "Shoes", "Lightweight running shoes", 4500, 20, "https://example.com/nike.jpg"),
    ("Adidas RunFalcon", "Shoes", "Comfortable daily running shoes", 4000, 15, "https://example.com/adidas.jpg"),
    ("Puma Velocity", "Shoes", "High-performance sneakers", 4200, 10, "https://example.com/puma.jpg"),
    ("MacBook Air M2", "Electronics", "Laptop for designers and students", 114900, 5, "https://example.com/macbook.jpg"),
    ("Apple iPhone 15", "Electronics", "Latest iPhone with A17 chip", 79900, 8, "https://example.com/iphone.jpg"),
    ("Zara Black Dress", "Fashion", "Elegant black dress for evening parties", 2499, 12, "https://example.com/zara_dress.jpg"),
    ("Zara Floral Maxi", "Fashion", "Floral black maxi dress", 2899, 10, "https://example.com/zara_maxi.jpg"),
]

cursor.executemany("""
INSERT INTO products (name, category, description, price, stock, image_url)
VALUES (?, ?, ?, ?, ?, ?);
""", products)

# ------------------------
# Insert mock customers
# ------------------------
customers = [
    ("Rahul", "rahul@example.com", "student,sports"),
    ("Ananya", "ananya@example.com", "designer,apple_fan"),
    ("Sneha", "sneha@example.com", "fashion,shopping"),
    ("Vikram", "vikram@example.com", "electronics,gaming"),
    ("Priya", "priya@example.com", "student,fashion"),
]

cursor.executemany("""
INSERT INTO customers (name, email, tags)
VALUES (?, ?, ?);
""", customers)

# ------------------------
# Insert mock purchases
# ------------------------
purchases = [
    (1, 1, 1),  # Rahul bought Nike Air Zoom
    (1, 4, 1),  # Rahul bought MacBook Air
    (2, 5, 1),  # Ananya bought iPhone 15
    (3, 6, 1),  # Sneha bought Zara Black Dress
    (5, 7, 1),  # Priya bought Zara Floral Maxi
]

cursor.executemany("""
INSERT INTO purchases (customer_id, product_id, quantity)
VALUES (?, ?, ?);
""", purchases)

# ------------------------
# Insert mock cart items
# ------------------------
cart_items = [
    (1, 2, 1),  # Rahul has Adidas RunFalcon in cart
    (3, 7, 1),  # Sneha has Zara Floral Maxi in cart
]

cursor.executemany("""
INSERT INTO cart (customer_id, product_id, quantity)
VALUES (?, ?, ?);
""", cart_items)

# Commit changes and close connection
conn.commit()
conn.close()

print("Mock data inserted successfully!")
