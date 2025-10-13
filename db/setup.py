# db/setup.py
import mysql.connector as sql
import json
import sys
import subprocess

# -----------------------
# Install dependencies
# -----------------------
print("Installing required dependencies...")
subprocess.check_call([sys.executable, "-m", "pip", "install", "mysql-connector-python", "--quiet"])
subprocess.check_call([sys.executable, "-m", "pip", "install", "cryptography", "--quiet"])
subprocess.check_call([sys.executable, "-m", "pip", "install", "humanize", "--quiet"])
subprocess.check_call([sys.executable, "-m", "pip", "install", "pwinput", "--quiet"])
subprocess.check_call([sys.executable, "-m", "pip", "install", "rich", "--quiet"])
subprocess.check_call([sys.executable, "-m", "pip", "install", "python-dotenv", "--quiet"])
print("✅ Dependencies installed successfully.\n")

# -----------------------
# Get MySQL connection details
# -----------------------
host = input("Enter MySQL host (e.g. localhost): ")
username = input("Enter MySQL username: ")
password = input("Enter MySQL password: ")

with open("sqlDetails.json", "w") as f:
    json.dump({"host": host, "username": username, "password": password}, f)

# -----------------------
# Connect to MySQL
# -----------------------
print("\nConnecting to MySQL...")
db = sql.connect(host=host, user=username, password=password)
cursor = db.cursor()
db.autocommit = True

# -----------------------
# Create Database
# -----------------------
cursor.execute("DROP DATABASE IF EXISTS yippee")
cursor.execute("CREATE DATABASE yippee")
cursor.execute("USE yippee")

# -----------------------
# Create Tables
# -----------------------
cursor.execute("""
CREATE TABLE userdata (
    username VARCHAR(100) PRIMARY KEY,
    password VARCHAR(255) NOT NULL,
    name VARCHAR(100)
)
""")

cursor.execute("""
CREATE TABLE restaurants (
    name VARCHAR(100) PRIMARY KEY,
    menu TEXT,
    details TEXT
)
""")

cursor.execute("""
CREATE TABLE payment (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100),
    card VARCHAR(255),
    cvv VARCHAR(255),
    expiry VARCHAR(255),
    cardtype VARCHAR(255),
    FOREIGN KEY (username) REFERENCES userdata(username) ON DELETE CASCADE
)
""")


cursor.execute("""
CREATE TABLE orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100),
    restaurant VARCHAR(100),
    unix_time DOUBLE,
    total_price DECIMAL(10,2),
    FOREIGN KEY (username) REFERENCES userdata(username) ON DELETE CASCADE
)
""")

cursor.execute("""
CREATE TABLE order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT,
    dish VARCHAR(100),
    quantity INT,
    price DECIMAL(10,2),
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE
)
""")

# -----------------------
# Restaurant Data (Your 7 Restaurants)
# -----------------------

# 1. Grana Pizzeria
food_grana = {
    "Mineral Water": 20.00,
    "Garlic Bread": 120.00,
    "Bruschetta": 150.00,
    "Mozzarella Sticks": 180.00,
    "Margherita Pizza": 350.00,
    "Smoked Chicken Pesto Pizza": 450.00,
    "Tiramisu": 220.00
}
details_grana = {
    "Location": "Panampilly Nagar, Kochi",
    "Phone": "+91 484 1234567",
    "Website": "www.granapizzeria.com",
    "Opening Hours": "11:00 - 23:00",
    "Cuisine": "Italian / Pizza",
    "Rating": "4.6"
}

# 2. Mash Restocafe
food_mash = {
    "Mineral Water": 20.00,
    "Cold Coffee": 150.00,
    "French Fries": 120.00,
    "Fish Fingers": 220.00,
    "Soup of the Day": 150.00,
    "Burger": 280.00,
    "Pasta Alfredo": 300.00
}
details_mash = {
    "Location": "Panampilly Nagar, Kochi",
    "Phone": "+91 484 2233445",
    "Website": "www.mashrestocafe.com",
    "Opening Hours": "10:00 - 23:00",
    "Cuisine": "Café / Continental",
    "Rating": "4.5"
}

# 3. P60
food_p60 = {
    "Mineral Water": 20.00,
    "Passion Lemonade": 100.00,
    "Garlic Bread": 120.00,
    "Soup of the Day": 150.00,
    "Italian Pizza": 400.00,
    "Lasagna": 350.00,
    "Tiramisu": 200.00
}
details_p60 = {
    "Location": "Panampilly Nagar, Kochi",
    "Phone": "+91 484 3344556",
    "Website": "www.p60cafe.com",
    "Opening Hours": "12:00 - 23:00",
    "Cuisine": "Pizza / Italian / Café",
    "Rating": "4.4"
}

# 4. Happy Cup
food_happy = {
    "Mineral Water": 20.00,
    "Soft Drink": 40.00,
    "Samosa": 50.00,
    "Chaat": 100.00,
    "Kebab": 180.00,
    "Butter Chicken with Naan": 300.00,
    "Chole Bhature": 150.00
}
details_happy = {
    "Location": "Panampilly Nagar, Kochi",
    "Phone": "+91 484 4455667",
    "Website": "www.happycupcafe.com",
    "Opening Hours": "09:00 - 22:00",
    "Cuisine": "Café / Indian Street Food",
    "Rating": "4.3"
}

# 5. Gokul Oottupura
food_gokul = {
    "Mineral Water": 20.00,
    "Idli": 40.00,
    "Dosa": 60.00,
    "Vada": 50.00,
    "Meals (Veg Thali)": 120.00,
    "Uttapam": 80.00,
    "Filter Coffee": 40.00
}
details_gokul = {
    "Location": "Panampilly Nagar, Kochi",
    "Phone": "+91 484 5566778",
    "Website": "www.gokuloottupura.com",
    "Opening Hours": "07:00 - 22:00",
    "Cuisine": "South Indian (Vegetarian)",
    "Rating": "4.4"
}

# 6. 1947 Indian Restaurant
food_1947 = {
    "Mineral Water": 20.00,
    "Paneer Tikka": 220.00,
    "Chicken Tandoori": 280.00,
    "Dal Makhani": 180.00,
    "Butter Naan": 40.00,
    "Chicken Biryani": 260.00,
    "Gulab Jamun": 90.00
}
details_1947 = {
    "Location": "Panampilly Nagar, Kochi",
    "Phone": "+91 484 6677889",
    "Website": "www.1947restaurant.com",
    "Opening Hours": "12:00 - 23:00",
    "Cuisine": "North Indian",
    "Rating": "4.5"
}

# 7. Zaatar Restaurant
food_zaatar = {
    "Mineral Water": 20.00,
    "Hummus with Pita": 150.00,
    "Falafel": 180.00,
    "Shawarma Roll": 200.00,
    "Chicken Mandi": 350.00,
    "Mixed Grill Platter": 480.00,
    "Baklava": 200.00
}
details_zaatar = {
    "Location": "Panampilly Nagar, Kochi",
    "Phone": "+91 484 7788990",
    "Website": "www.zaatarcafe.com",
    "Opening Hours": "11:00 - 23:00",
    "Cuisine": "Arabic / Middle Eastern",
    "Rating": "4.6"
}

# -----------------------
# Insert Restaurant Data
# -----------------------
restaurants = [
    ("Grana Pizzeria", str(food_grana), str(details_grana)),
    ("Mash Restocafe", str(food_mash), str(details_mash)),
    ("P60", str(food_p60), str(details_p60)),
    ("Happy Cup", str(food_happy), str(details_happy)),
    ("Gokul Oottupura", str(food_gokul), str(details_gokul)),
    ("1947 Restaurant", str(food_1947), str(details_1947)),
    ("Zaatar Restaurant", str(food_zaatar), str(details_zaatar)),
]

cursor.executemany("INSERT INTO restaurants VALUES (%s, %s, %s)", restaurants)

print("✅ Database 'yippee' created successfully with 7 restaurants!")
