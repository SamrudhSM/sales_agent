import sqlite3

# Path to your database file
DB_PATH = "data.db"

# Connect to the database (it will create the file if it doesn't exist)
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Drop the table if it already exists (optional, for fresh creation)
cursor.execute("DROP TABLE IF EXISTS customers;")

# Create the customers table
cursor.execute("""
CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

# Commit changes and close connection
conn.commit()
conn.close()

print("Table 'customers' created successfully!")
