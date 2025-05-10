import sqlite3
import random


def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def create_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cubes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            color TEXT,
            name TEXT,
            description TEXT,
            image TEXT,
            price REAL,
            stock INTEGER
        )
    ''')
    conn.commit()
    conn.close()

def generate_cube_description():
  adjectives = [
      "colorful", "fun", "interactive", "soft", "safe", "stackable", "durable",
      "bright", "lightweight", "educational", "engaging", "creative"
  ]
  features = [
      "perfect for tiny hands", "great for early learning", "helps build motor skills",
      "teaches colors and shapes", "designed for safe play", "fun to stack and sort",
      "ideal for playtime", "inspires imagination", "built to last"
  ]
  toys = [
      "cube", "block", "toy block", "learning cube", "building block", "stacking cube"
  ]

  adjective = random.choice(adjectives)
  toy = random.choice(toys)
  feature = random.choice(features)

  return f"A {adjective} {toy} that's {feature}."

def add_cube(color):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if cube with the color already exists
    cursor.execute("SELECT * FROM cubes WHERE color = ?", (color,))
    existing_cube = cursor.fetchone()

    if existing_cube:
        # Update stock if cube already exists
        cursor.execute("UPDATE cubes SET stock = stock + 1 WHERE color = ?", (color,))
    else:
        # Insert new cube with default values
        cursor.execute(
            '''INSERT INTO cubes (color, name, description, image, price, stock)
               VALUES (?, ?, ?, ?, ?, ?)''',
            (color, f"{color.capitalize()} CUB", generate_cube_description(), f"{color}.jpg", 10.0, 1)
        )

    conn.commit()
    conn.close()