import datetime

from flask import Flask, jsonify, request, flash
import json
import sqlite3

app = Flask(__name__)


def db_connection():
    conn = None
    try:
        conn = sqlite3.connect("product_management.db")
    except sqlite3.error as e:
        print(e)
    print("connection", conn)
    return conn


def validate_data(status_code, message, payload):
    return jsonify({
        "status": status_code,
        "message": message,
        "payload": payload
    })


def data_validations(data):
    if not data[0] or len(data[0]) <= 1:
        return validate_data(status_code=422, message="sorry product_name not entered correctly")
    elif not data[1] or not data[1].isnumeric():
        return validate_data(status_code=422, message="sorry price not entered correctly")
    elif not data[2] or not data[2].isnumeric():
        return validate_data(status_code=422, message="sorry quantity not entered correctly")
    else:
        conn = db_connection()
        cursor = conn.cursor()
        sql = """INSERT INTO products(product_name, price, quantity) VALUES(?,?,?) """
        cursor.execute(sql, (data[0], data[1], data[2]))
        conn.commit()
        return validate_data(status_code=201, message="product_item created successfully",
                             payload={"product_name": data[0], "price": data[1], "quantity": data[2]})


@app.route("/products", methods=["GET"])
def get_products():
    try:
        conn = db_connection()
        cursor = conn.execute("SELECT * FROM products")
        product_dic = {row[0]: {"product_name": row[1], "price": row[2], "quantity": row[3]}
                       for row in cursor.fetchall()}
        if product_dic:
            return jsonify(product_dic)
        else:
            return validate_data(status_code=422, message="no products available ")

    except Exception as e:
        print("Error", e)
        return validate_data(status_code=500, message="something went wrong")


@app.route("/products/<int:id>", methods=["GET"])
def get_product_details(id):
    try:
        conn = db_connection()
        cursor = conn.execute(f"SELECT * FROM products WHERE id=?", (id,))
        product_dic = {row[0]: {"product_name": row[1], "price": row[2], "quantity": row[3]}
                       for row in cursor.fetchall()}
        if product_dic:
            return jsonify(product_dic)
        else:
            return validate_data(status_code=422, message="product is not available")

    except Exception as e:
        print("Error", e)
        return validate_data(status_code=500, message="something went wrong")


@app.route("/products_price_greater_then_hundred/<int:price1>-<int:price2>", methods=["GET"])
def products_greater(price1, price2):
    try:
        conn = db_connection()
        cursor = conn.execute(f"SELECT * FROM products WHERE price BETWEEN {price1} AND {price2}")
        product_dic = {row[0]: {"product_name": row[1], "price": row[2], "quantity": row[3]}
                       for row in cursor.fetchall()}
        if product_dic:
            return jsonify(product_dic)
        else:
            return validate_data(status_code=422, message="no products available in this range")

    except Exception as e:
        print("Error", e)
        return validate_data(status_code=500, message="something went wrong")


@app.route("/products", methods=["POST"])
def create_product_item():
    try:
        request_data = request.get_json()
        print(request_data)
        if not request_data:
            return validate_data(status_code=422, message="sorry request data is not available")
        product_name = request_data.get('product_name')
        print(request_data.get('product_name'))
        price = request_data.get('price')
        quantity = request_data.get('quantity')

        print(product_name, price, quantity)
        data = [product_name, price, quantity]
        return data_validations(data=data)
    except Exception as e:
        import traceback
        traceback.print_exc()
        print("Error", e)
        return validate_data(status_code=500, message="something went wrong")


@app.route("/products/<int:id>", methods=["PUT"])
def updated_product_details(id):
    try:
        request_data = request.json
        if not request_data:
            return validate_data(status_code=422, message="request is not appropriate")
        product_name = request_data.get('product_name')
        price = request_data.get('price')
        quantity = request_data.get('quantity')
        conn = db_connection()
        cursor = conn.cursor()
        sql = "UPDATE products SET product_name=?, quantity=?, price=? WHERE id=? "
        updated_table = {
            "id": id,
            "price": price,
            "product_name": product_name,
            "quantity": quantity
        }
        cursor.execute(sql, (product_name, quantity, price, id))
        conn.commit()
        return jsonify(updated_table)
    except Exception as e:
        print("Error", e)
        return validate_data(status_code=500, message="something went wrong")


@app.route("/products/<int:id>", methods=["DELETE"])
def deleted_values(id):
    try:
        conn = db_connection()
        sql = f"SELECT * FROM products WHERE id={id}"
        cursor = conn.execute(sql)

        if cursor.fetchall():
            sql = """ DELETE FROM products WHERE id=? """
            conn.execute(sql, (id,))
            conn.commit()

            return validate_data(status_code=422, message="The product with id: {} has been deleted")
        else:
            return validate_data(status_code=404, message="no product present")

    except Exception as e:

        print("Error", e)
        return validate_data(status_code=500, message="something went wrong")


if __name__ == "__main__":
    app.run(debug=True, port=8900)
