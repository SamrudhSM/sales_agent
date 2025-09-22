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
        return jsonify({"message": "Login successful"}), 200
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
        return jsonify({"message": "Signup successful"}), 201

    except sqlite3.IntegrityError:
        return jsonify({"error": "Email already exists"}), 409

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
