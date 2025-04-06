import os
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
    """
    Show products in a table, and allow filtering by category 
    and price range using GET query params.
    """
    # 1) Collect filter values from URL query params
    category_filter = request.args.get('category', default='', type=str)
    min_price = request.args.get('min_price', default='', type=str)
    max_price = request.args.get('max_price', default='', type=str)

    # 2) Build the SQL query dynamically based on filters
    base_query = """
        SELECT product_id, product_name, category, image, description, price, stock_quantity
        FROM products
    """
    conditions = []
    params = {}

    # If user entered a category filter
    if category_filter:
        conditions.append("category = :cat")
        params['cat'] = category_filter

    # If user entered min price
    if min_price:
        conditions.append("price >= :minp")
        params['minp'] = float(min_price)

    # If user entered max price
    if max_price:
        conditions.append("price <= :maxp")
        params['maxp'] = float(max_price)

    # If we have conditions, add WHERE
    if conditions:
        base_query += " WHERE " + " AND ".join(conditions)

    # Optional: add ORDER BY, etc.
    base_query += " ORDER BY product_id"

    # 3) Execute the query
    cursor = g.conn.execute(text(base_query), params)
    products_list = cursor.fetchall()
    cursor.close()

    # 4) Render the products template with the filter form and the results
    return render_template(
        'products.html',
        products=products_list,
        category_filter=category_filter,
        min_price=min_price,
        max_price=max_price
    )

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

