
"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver
To run locally:
    python server.py
Go to http://localhost:8111 in your browser.
A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""
import os
  # accessible as a variable in index.html:	
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)


#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@34.148.223.31/proj1part2
#
# For example, if you had username zy2431 and password 123123, then the following line would be:
#
#     DATABASEURI = "postgresql://zy2431:123123@34.148.223.31/proj1part2"
#
# Modify these with your own credentials you received from TA!
DATABASE_USERNAME = "yy3294"
DATABASE_PASSWRD = "969446"
DATABASE_HOST = "34.148.223.31"
DATABASEURI = f"postgresql://{DATABASE_USERNAME}:{DATABASE_PASSWRD}@{DATABASE_HOST}/proj1part2"

@app.before_request
def before_request():
    try:
        g.conn = engine.connect()
    except:
        print("uh oh, problem connecting to database")
        import traceback; traceback.print_exc()
        g.conn = None

@app.teardown_request
def teardown_request(exception):
    try:
        g.conn.close()
    except Exception as e:
        pass

# ------------------ ROUTES ------------------

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/users')
def show_users():
    query = "SELECT * FROM users"
    cursor = g.conn.execute(text(query))
    users = [dict(
        user_id=row[0],
        first_name=row[1],
        last_name=row[2],
        email=row[3],
        phone=row[4]
    ) for row in cursor]
    cursor.close()
    return render_template("users.html", users=users)

@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        insert_query = """
            INSERT INTO users (first_name, last_name, email_address, phone_number, password, zip_code, city, country)
            VALUES (:fn, :ln, :email, :phone, :pwd, :zip, :city, :country)
        """
        g.conn.execute(text(insert_query), {
            "fn": request.form['first_name'],
            "ln": request.form['last_name'],
            "email": request.form['email_address'],
            "phone": request.form['phone_number'],
            "pwd": request.form['password'],
            "zip": request.form['zip_code'],
            "city": request.form['city'],
            "country": request.form['country']
        })
        g.conn.commit()
        return redirect('/users')
    return render_template("add_user.html")

# ------------------ RUN SERVER ------------------

if __name__ == "__main__":
    import click

    @click.command()
    @click.option('--debug', is_flag=True)
    @click.option('--threaded', is_flag=True)
    @click.argument('HOST', default='0.0.0.0')
    @click.argument('PORT', default=8111, type=int)
    def run(debug, threaded, host, port):
        print("running on %s:%d" % (host, port))
        app.run(host=host, port=port, debug=debug, threaded=threaded)

    run()

# View all products
@app.route('/products')
def show_products():
    query = "SELECT * FROM products"
    cursor = g.conn.execute(text(query))
    products = [dict(
        product_id=row[0],
        name=row[1],
        category=row[2],
        image=row[3],
        description=row[4],
        price=row[5],
        stock=row[6]
    ) for row in cursor]
    cursor.close()
    return render_template("products.html", products=products)

# Add a new product
@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        insert_query = """
            INSERT INTO products (product_name, category, image, description, price, stock_quantity)
            VALUES (:name, :category, :image, :desc, :price, :stock)
        """
        g.conn.execute(text(insert_query), {
            "name": request.form['product_name'],
            "category": request.form['category'],
            "image": request.form['image'],
            "desc": request.form['description'],
            "price": request.form['price'],
            "stock": request.form['stock_quantity']
        })
        g.conn.commit()
        return redirect('/products')
    return render_template("add_product.html")

# View all orders
@app.route('/orders')
def show_orders():
    query = """
    SELECT orders.order_id, users.first_name, users.last_name, orders.product_id,
           orders.order_status, orders.order_date, orders.delivery_date, orders.amount
    FROM orders
    JOIN users ON orders.user_id = users.user_id
    """
    cursor = g.conn.execute(text(query))
    orders = [dict(
        order_id=row[0],
        customer_name=f"{row[1]} {row[2]}",
        product_id=row[3],
        status=row[4],
        order_date=row[5],
        delivery_date=row[6],
        amount=row[7]
    ) for row in cursor]
    cursor.close()
    return render_template("orders.html", orders=orders)

# Add a new order
@app.route('/add_order', methods=['GET', 'POST'])
def add_order():
    if request.method == 'POST':
        insert_query = """
            INSERT INTO orders (user_id, product_id, order_status, order_date, delivery_date, amount)
            VALUES (:uid, :pid, :status, :odate, :ddate, :amt)
        """
        g.conn.execute(text(insert_query), {
            "uid": request.form['user_id'],
            "pid": request.form['product_id'],
            "status": request.form['order_status'],
            "odate": request.form['order_date'],
            "ddate": request.form['delivery_date'],
            "amt": request.form['amount']
        })
        g.conn.commit()
        return redirect('/orders')
    return render_template("add_order.html")
