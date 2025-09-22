from flask import Flask, request, jsonify
import sqlite3
import google.generativeai as genai
from google.generativeai.types import Tool, FunctionDeclaration

app = Flask(__name__)
DB_PATH = "data.db"

# --- Configure Gemini with your API key ---
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
    customer_id = data.get("customer_id", 1)
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
