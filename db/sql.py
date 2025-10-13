# db/sql.py
import mysql.connector as sql
from cryptography.fernet import Fernet
from dotenv import load_dotenv
import os
import json

# -----------------------
# Load environment variables
# -----------------------
load_dotenv()
key = os.getenv("FERNET_KEY")
if not key:
    raise ValueError("❌ Missing FERNET_KEY environment variable! Please add it to your .env file.")
f = Fernet(key)

# -----------------------
# Load SQL Credentials
# -----------------------
with open("sqlDetails.json") as f_json:
    config = json.load(f_json)

db = sql.connect(
    host=config["host"],
    user=config["username"],
    password=config["password"],
    database="yippee"
)
cursor = db.cursor(buffered=True)
db.autocommit = True


# ===================================================
# USER MANAGEMENT
# ===================================================
def register(username, password, name):
    """Register a new user."""
    encrypted_password = f.encrypt(password.encode()).decode()
    cursor.execute("INSERT INTO userdata VALUES (%s, %s, %s)", (username, encrypted_password, name))
    return True


def login(username, password):
    """Authenticate user login."""
    cursor.execute("SELECT password FROM userdata WHERE username=%s", (username,))
    result = cursor.fetchone()
    if result:
        decrypted = f.decrypt(result[0].encode()).decode()
        return decrypted == password
    return False


def check_user(username):
    """Check if a user exists and return their name."""
    cursor.execute("SELECT * FROM userdata WHERE username=%s", (username,))
    result = cursor.fetchone()
    if result:
        return True, result[2]
    return False, None


def change_password(username, new_password):
    """Update user password."""
    encrypted_password = f.encrypt(new_password.encode()).decode()
    cursor.execute("UPDATE userdata SET password=%s WHERE username=%s", (encrypted_password, username))
    return True


# ===================================================
# RESTAURANTS
# ===================================================
def get_restaurants():
    """Fetch all restaurants."""
    cursor.execute("SELECT * FROM restaurants")
    return cursor.fetchall()


# ===================================================
# PAYMENT
# ===================================================
def add_payment(username, card, cvv, expiry, cardtype):
    """Encrypt and store payment details securely."""
    enc_card = f.encrypt(card.encode()).decode()
    enc_cvv = f.encrypt(cvv.encode()).decode()
    enc_expiry = f.encrypt(expiry.encode()).decode()
    enc_type = f.encrypt(cardtype.encode()).decode()

    cursor.execute("""
        INSERT INTO payment (username, card, cvv, expiry, cardtype)
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE card=%s, cvv=%s, expiry=%s, cardtype=%s
    """, (
        username, enc_card, enc_cvv, enc_expiry, enc_type,
        enc_card, enc_cvv, enc_expiry, enc_type
    ))
    return True


def retrieve_payment(username):
    """Decrypt and return saved payment details."""
    cursor.execute("SELECT card, cvv, expiry, cardtype FROM payment WHERE username=%s", (username,))
    result = cursor.fetchone()
    if result:
        try:
            return True, {
                "card": f.decrypt(result[0].encode()).decode(),
                "cvv": f.decrypt(result[1].encode()).decode(),
                "expiry": f.decrypt(result[2].encode()).decode(),
                "cardtype": f.decrypt(result[3].encode()).decode(),
            }
        except Exception:
            return False, None
    return False, None


# ===================================================
# ORDERS
# ===================================================
def place_order(username, restaurant, items, unix, total_price):
    """Insert order and associated order items."""
    cursor.execute(
        "INSERT INTO orders (username, restaurant, unix_time, total_price) VALUES (%s, %s, %s, %s)",
        (username, restaurant, unix, total_price)
    )
    order_id = cursor.lastrowid

    for dish, qty, price in items:
        cursor.execute(
            "INSERT INTO order_items (order_id, dish, quantity, price) VALUES (%s, %s, %s, %s)",
            (order_id, dish, qty, price)
        )

    return True, order_id


def view_orders(username):
    """Return all orders for a given user."""
    cursor.execute("SELECT * FROM orders WHERE username=%s ORDER BY id DESC", (username,))
    orders = cursor.fetchall()

    if not orders:
        return False, None

    data = []
    for order in orders:
        order_id, _, restaurant, unix_time, total_price = order
        cursor.execute("SELECT dish, quantity, price FROM order_items WHERE order_id=%s", (order_id,))
        items = cursor.fetchall()
        data.append({
            "order_id": order_id,
            "restaurant": restaurant,
            "items": items,
            "unix_time": unix_time,
            "total_price": total_price
        })
    return True, data


# ===================================================
# USER DATA RETRIEVAL
# ===================================================
def retrieve_user(username):
    """Fetch user details (name, email)."""
    cursor.execute("SELECT * FROM userdata WHERE username=%s", (username,))
    return cursor.fetchone()


def logout():
    """Placeholder (session handling handled in main app)."""
    return True
