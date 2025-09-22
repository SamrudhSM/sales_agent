import sqlite3
from flask import Flask, render_template, request, jsonify, session, redirect, url_for

app = Flask(__name__)
app.secret_key = 'supersecretkey' 

DB_PATH = "data.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def index():
    return redirect(url_for("login"))

@app.route("/home")
def home():
    if "customer_id" not in session:
        return redirect(url_for("login"))  # protect route
    name = session.get("customer_name")
    return render_template("index.html", name=name)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    conn = get_db_connection()
    user = conn.execute(
        "SELECT * FROM customers WHERE email = ? AND password = ?",
        (email, password)
    ).fetchone()
    conn.close()

    if user:
        session["customer_id"] = user["customer_id"]
        session["customer_name"] = user["name"]
        return jsonify({"message": "Login successful", "redirect": "/home"}), 200
    else:
        return jsonify({"error": "Invalid email or password"}), 401


@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if not name or not email or not password:
        return jsonify({"error": "Missing required fields"}), 400

    try:
        conn = get_db_connection()
        conn.execute(
            "INSERT INTO customers (name, email, password) VALUES (?, ?, ?)",
            (name, email, password)
        )
        conn.commit()
        user = conn.execute("SELECT * FROM customers WHERE email = ?", (email,)).fetchone()
        conn.close()

        # Auto-login
        session["customer_id"] = user["customer_id"]
        session["customer_name"] = user["name"]
        return jsonify({"message": "Signup successful", "redirect": "/home"}), 201

    except sqlite3.IntegrityError:
        return jsonify({"error": "Email already exists"}), 409

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/product/<int:product_id>")
def product_page(product_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT product_id, name, description, price, category FROM products WHERE product_id = ?", (product_id,))
    product = cursor.fetchone()
    conn.close()

    if product:
        product_data = {
            "id": product[0],
            "name": product[1],
            "description": product[2],
            "price": product[3],
            "category": product[4]
        }
    else:
        product_data = None  # If product not found
    
    return render_template("product.html", product=product_data)

@app.route("/cart")
def cart():
    if "customer_id" not in session:
        return redirect(url_for("login"))

    customer_id = session["customer_id"]

    conn = get_db_connection()
    cart_items = conn.execute("""
        SELECT c.cart_id, c.quantity, c.added_at,
               p.product_id, p.name, p.price, p.category
        FROM cart c
        JOIN products p ON c.product_id = p.product_id
        WHERE c.customer_id = ?
    """, (customer_id,)).fetchall()
    conn.close()

    return render_template("cart.html", name=session.get("customer_name"), cart_items=cart_items)


@app.route("/add_to_cart/<int:product_id>", methods=["POST"])
def add_to_cart(product_id):
    if "customer_id" not in session:
        return redirect(url_for("login"))

    customer_id = session["customer_id"]

    conn = get_db_connection()
    try:
        # Check if the item is already in the cart
        cart_item = conn.execute(
            "SELECT quantity FROM cart WHERE customer_id = ? AND product_id = ?",
            (customer_id, product_id)
        ).fetchone()

        if cart_item:
            # If item exists, update the quantity
            new_quantity = cart_item["quantity"] + 1
            conn.execute(
                "UPDATE cart SET quantity = ? WHERE customer_id = ? AND product_id = ?",
                (new_quantity, customer_id, product_id)
            )
        else:
            # If item is new, add it to the cart
            conn.execute(
                "INSERT INTO cart (customer_id, product_id, quantity) VALUES (?, ?, 1)",
                (customer_id, product_id)
            )
        conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        print(f"Database error: {e}")
        return "Failed to add item to cart.", 500
    finally:
        conn.close()

    return redirect(url_for("cart"))


def get_products():
    conn = sqlite3.connect("data.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

@app.route("/getproducts")
def getproducts():
    return jsonify(get_products())


@app.route("/checkout", methods=["POST"])
def checkout():
    if "customer_id" not in session:
        return redirect(url_for("login"))

    customer_id = session["customer_id"]

    conn = get_db_connection()
    try:
        conn.execute("DELETE FROM cart WHERE customer_id = ?", (customer_id,))
        conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        print(f"Database error during checkout: {e}")
    finally:
        conn.close()

    return redirect(url_for("home"))

 
if __name__ == "__main__":
    app.run(debug=True)


