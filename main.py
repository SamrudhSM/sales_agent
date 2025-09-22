import sqlite3
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import google.generativeai as genai
from google.generativeai.types import Tool, FunctionDeclaration

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
        # Fetch items in cart
        cart_items = conn.execute(
            "SELECT product_id, quantity FROM cart WHERE customer_id = ?",
            (customer_id,)
        ).fetchall()

        # Insert them into purchases
        for item in cart_items:
            conn.execute(
                "INSERT INTO purchases (customer_id, product_id, quantity) VALUES (?, ?, ?)",
                (customer_id, item["product_id"], item["quantity"])
            )

        # Clear cart for this customer
        conn.execute("DELETE FROM cart WHERE customer_id = ?", (customer_id,))

        conn.commit()

    except sqlite3.Error as e:
        conn.rollback()
        print(f"Database error during checkout: {e}")
        return "Checkout failed.", 500
    finally:
        conn.close()

    return redirect(url_for("home"))


genai.configure(api_key="AIzaSyDrBtlrAJ77izPgPplgesAEUXYy2k_wgY8")

# --- DB helper ---
def get_db_data(customer_id=1):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Customer info
    cursor.execute("SELECT name FROM customers WHERE customer_id = ?", (customer_id,))
    row = cursor.fetchone()
    customer_name = row[0] if row else f"Customer {customer_id}"

    # Products
    cursor.execute("SELECT product_id, name, category, description, price, stock FROM products")
    products = [
        {"id": r[0], "name": r[1], "category": r[2], "description": r[3], "price": r[4], "stock": r[5]}
        for r in cursor.fetchall()
    ]

    # Purchases
    cursor.execute("SELECT purchase_id, product_id, quantity, purchase_date FROM purchases WHERE customer_id = ?", (customer_id,))
    purchases = [
        {"id": r[0], "product_id": r[1], "quantity": r[2], "date": r[3]}
        for r in cursor.fetchall()
    ]

    # Cart
    cursor.execute("SELECT cart_id, product_id, quantity, added_at FROM cart WHERE customer_id = ?", (customer_id,))
    cart = [
        {"id": r[0], "product_id": r[1], "quantity": r[2], "added_at": r[3]}
        for r in cursor.fetchall()
    ]

    conn.close()
    return {
        "customer_name": customer_name,
        "products": products,
        "purchases": purchases,
        "cart": cart
    }

# --- Tool function ---
def add_to_cart(customer_id: int, product_name: str, quantity: int = 1):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT product_id FROM products WHERE name LIKE ?", (f"%{product_name}%",))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return {"status": "error", "message": f"Product '{product_name}' not found."}
    product_id = row[0]
    cursor.execute("INSERT INTO cart (customer_id, product_id, quantity) VALUES (?, ?, ?)", (customer_id, product_id, quantity))
    conn.commit()
    conn.close()
    return {"status": "success", "message": f"Added {quantity} of '{product_name}' (id={product_id}) to cart."}

# --- Tool definition ---
tools = [
    Tool(
        function_declarations=[
            FunctionDeclaration(
                name="add_to_cart",
                description="Add a product to the cart by name",
                parameters={
                    "type": "object",
                    "properties": {
                        "customer_id": {"type": "integer"},
                        "product_name": {"type": "string"},
                        "quantity": {"type": "integer"}
                    },
                    "required": ["customer_id", "product_name"]
                }
            )
        ]
    )
]

# --- AI route ---
@app.route("/ask_ai", methods=["POST"])
def ai_route():
    data = request.json
    query = data.get("query")
    customer_id = session.get("customer_id", 1)
    if not query:
        return jsonify({"error": "No query provided"}), 400

    db_data = get_db_data(customer_id)

    # Create model with tools
    model = genai.GenerativeModel(model_name="gemini-1.5-flash", tools=tools)

    # Inject DB context into prompt
    prompt = f"""
    Customer: {db_data['customer_name']} (ID: {customer_id})

    Products: {db_data['products']}

    Purchases: {db_data['purchases']}

    Cart: {db_data['cart']}

    Now answer the user's query:
    {query}
    """

    response = model.generate_content(prompt)

    # If Gemini calls the tool
    if response.candidates[0].content.parts[0].function_call:
        fn_call = response.candidates[0].content.parts[0].function_call
        fn_name = fn_call.name
        fn_args = dict(fn_call.args)
        print("DEBUG: Tool call ->", fn_name, fn_args)

        if fn_name == "add_to_cart":
            return jsonify(add_to_cart(fn_args.get("customer_id", customer_id), fn_args["product_name"], fn_args.get("quantity", 1)))

    # Otherwise return Gemini text
    return jsonify({"reply": response.text})



 
if __name__ == "__main__":
    app.run(debug=True)


