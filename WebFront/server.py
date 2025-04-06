import os
path = os.path.abspath(__file__)
safe_path = path.encode('ascii', errors='ignore').decode()
print("I AM RUNNING THIS FILE:", safe_path)

from flask import Flask, render_template, g, redirect, request
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool

app = Flask(__name__)

###############################################################################
#                           DATABASE CONFIGURATION
###############################################################################
DATABASE_USERNAME = "yy3294"
DATABASE_PASSWRD  = "969446"
DATABASE_HOST     = "34.148.223.31"
DATABASEURI       = f"postgresql://{DATABASE_USERNAME}:{DATABASE_PASSWRD}@{DATABASE_HOST}/proj1part2"

# Create the engine with NullPool to avoid storing connections
engine = create_engine(DATABASEURI, poolclass=NullPool)

###############################################################################
#             HOOKS TO MANAGE THE DB CONNECTION PER REQUEST
###############################################################################
@app.before_request
def before_request():
    """
    Set up a database connection for the current request and store it in g.conn.
    """
    try:
        g.conn = engine.connect()
    except Exception as e:
        print("Error connecting to database:", e)
        g.conn = None

@app.teardown_request
def teardown_request(exception):
    """
    Close the database connection after each request.
    """
    try:
        if g.conn is not None:
            g.conn.close()
    except Exception as e:
        pass

@app.route('/')
def index():
    return render_template("index.html")


# 1) Products page
@app.route('/products')
def products():
    print("✅ /products route HIT!")

    query = text("""
        SELECT product_id, product_name, category, image, description, price, stock_quantity
        FROM products
        ORDER BY product_id
    """)

    cursor = g.conn.execute(query)
    rows = cursor.fetchall()
    cursor.close()

    print("✅ Raw rows:", rows)

    products_list = [
        {
            "product_id": row[0],
            "product_name": row[1],
            "category": row[2],
            "image": row[3],
            "description": row[4],
            "price": row[5],
            "stock_quantity": row[6]
        }
        for row in rows
    ]

    print("✅ Converted to dicts:", products_list)

    return render_template("products.html", products=products_list)



# 2) Shopping cart page
@app.route('/cart')
def cart():
    return render_template("cart.html")

# 3) Orders page
@app.route('/orders')
def orders():
    return render_template("orders.html")

# 4) Payment page
@app.route('/payment')
def payment():
    return render_template("payment.html")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8111, debug=True, use_reloader=False)

