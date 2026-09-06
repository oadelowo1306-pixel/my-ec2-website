import os
import mysql.connector
from flask import Flask, request

app = Flask(__name__)

@app.route("/health")
def health():
    return {"status": "ok"}, 200

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

@app.route("/")
def home():
    return "Backend is running!"

@app.route("/db")
def database_test():
    try:
        db = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT")),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )

        cursor = db.cursor()
        cursor.execute("SHOW TABLES")

        tables = cursor.fetchall()

        cursor.close()
        db.close()

        return {
            "database": os.getenv("DB_NAME"),
            "tables": [table[0] for table in tables]
        }

    except Exception as e:
        return {"error": str(e)}, 500
@app.route("/products")

def products():
    try:
        db = get_db_connection()

        cursor = db.cursor()
        cursor.execute("SELECT * FROM products")

        rows = cursor.fetchall()

        cursor.close()
        db.close()

        return {
            "products": [
                {
                    "id": row[0],
                    "name": row[1],
                    "price": float(row[2])
                }
                for row in rows
            ]
        }

    except Exception as e:
        return {"error": str(e)}, 500
    
@app.route("/products", methods=["POST"])
def add_product():
    try:
        data = request.get_json()
        if not data:
         return {"error": "Request body is required"}, 400
        if "name" not in data or "price" not in data:
         return {"error": "Name and price are required"}, 400
        name = data["name"]
        price = data["price"]

        if not isinstance(name, str) or not name.strip():
         return {"error": "Product name must be a non-empty string"}, 400
        if not isinstance(price, (int, float)) or price < 0:
         return {"error": "Price must be a non-negative number"}, 400

        db = get_db_connection()
        cursor = db.cursor()

        cursor.execute(
            "INSERT INTO products (name, price) VALUES (%s, %s)",
            (name, price)
        )

        db.commit()

        cursor.close()
        db.close()

        return {"message": "Product added successfully"}

    except Exception as e:
        return {"error": str(e)}, 500

@app.route("/products/<int:product_id>", methods=["PUT"])
def update_product(product_id):
    try:
        data = request.get_json()
        if not data:
         return {"error": "Request body is required"}, 400
        if "price" not in data:
         return {"error": "Price is required"}, 400
        price = data["price"]
        if not isinstance(price, (int, float)) or price < 0:
          return {"error": "Price must be a non-negative number"}, 400
        db = get_db_connection()
        cursor = db.cursor()

        cursor.execute(
            "UPDATE products SET price = %s WHERE id = %s",
            (price, product_id)
        )

        db.commit()

        cursor.close()
        db.close()

        return {"message": "Product updated successfully"}

    except Exception as e:
        return {"error": str(e)}, 500
@app.route("/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    try:
        db = get_db_connection()
        cursor = db.cursor()

        cursor.execute(
            "DELETE FROM products WHERE id = %s",
            (product_id,)
        )
        if cursor.rowcount == 0:
         cursor.close()
         db.close()
         return {"error": "Product not found"}, 404

        db.commit()

        cursor.close()
        db.close()

        return {"message": "Product deleted successfully"}

    except Exception as e:
        return {"error": str(e)}, 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
