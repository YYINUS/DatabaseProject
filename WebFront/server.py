import os
from flask import Flask, render_template, g, redirect, request, session
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.secret_key = '8f16f061fe02ef594d69723dece89321ae13c6a1e5345135a0658426fe9a3897'

###############################################################################
#                           DATABASE CONFIGURATION
###############################################################################
DATABASE_USERNAME = "yy3294"
DATABASE_PASSWRD  = "969446"
DATABASE_HOST     = "34.148.223.31"
DATABASEURI       = f"postgresql://{DATABASE_USERNAME}:{DATABASE_PASSWRD}@{DATABASE_HOST}/proj1part2"
engine = create_engine(DATABASEURI, poolclass=NullPool)

###############################################################################
#                          DB CONNECTION SETUP
###############################################################################
@app.before_request
def before_request():
    try:
        g.conn = engine.connect()
    except Exception as e:
        print("Error connecting to database:", e)
        g.conn = None

@app.teardown_request
def teardown_request(exception):
    try:
        if g.conn:
            g.conn.close()
    except:
        pass

###############################################################################
#                               ROUTES
###############################################################################

@app.route('/')
def index():
    return render_template("index.html")

# --------------------- LOGIN ---------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        query = text("SELECT user_id FROM users WHERE email_address = :email AND password = :password")
        result = g.conn.execute(query, {'email': email, 'password': password}).fetchone()
        if result:
            session['user_id'] = result[0]
            return redirect('/')
        else:
            return "Invalid credentials"
    return render_template("login.html")

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Collect form data
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email_address']
        phone = request.form['phone_number']
        password = request.form['password']
        zip_code = request.form.get('zip_code')
        city = request.form.get('city')
        country = request.form.get('country')

        # Optional: Enforce minimum password length
        if len(password) < 8:
            return "Password must be at least 8 characters."

        # Optional: Hash password
        # password = generate_password_hash(password)

        try:
            insert_query = text("""
                INSERT INTO users (first_name, last_name, email_address, phone_number, password, zip_code, city, country)
                VALUES (:fn, :ln, :email, :phone, :pwd, :zip, :city, :country)
            """)
            g.conn.execute(insert_query, {
                'fn': first_name,
                'ln': last_name,
                'email': email,
                'phone': phone,
                'pwd': password,
                'zip': zip_code,
                'city': city,
                'country': country
            })
            g.conn.commit()
            return redirect('/login')

        except IntegrityError as e:
            g.conn.rollback()
            return "⚠️ Email or phone number already exists."

        except Exception as e:
            g.conn.rollback()
            return f"❌ Registration failed: {str(e)}"

    return render_template('register.html')

# --------------------- PRODUCTS ---------------------
@app.route('/products')
def products():
    print("✅ /products route HIT!")

    category = request.args.get('category')
    min_price = request.args.get('min_price')
    max_price = request.args.get('max_price')

    print("🔎 Raw inputs ->", "Category:", category, "Min Price:", min_price, "Max Price:", max_price)

    query = """
        SELECT product_id, product_name, category, image, description, price, stock_quantity
        FROM products
        WHERE 1=1
    """
    params = {}

    if category:
        query += " AND category = :category"
        params['category'] = category

    try:
        if min_price and min_price.strip() != "":
            min_price = int(min_price)
            query += " AND price >= :min_price"
            params['min_price'] = min_price
    except ValueError:
        print("⚠️ Invalid min_price value ignored.")

    try:
        if max_price and max_price.strip() != "":
            max_price = int(max_price)
            query += " AND price <= :max_price"
            params['max_price'] = max_price
    except ValueError:
        print("⚠️ Invalid max_price value ignored.")

    query += " ORDER BY product_id"

    print("📝 Final SQL:", query)
    print("📦 Params:", params)

    cursor = g.conn.execute(text(query), params)
    rows = cursor.fetchall()
    cursor.close()

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

    return render_template("products.html", products=products_list)


@app.route('/product/<int:product_id>', methods=['GET', 'POST'])
def view_product(product_id):
    user_id = session.get('user_id')

    # Fetch product details
    product = g.conn.execute(text("""
        SELECT * FROM products WHERE product_id = :pid
    """), {'pid': product_id}).fetchone()

    # Handle review form submission
    if request.method == 'POST' and user_id:
        rating = request.form['rating']
        review_text = request.form['review_text']

        # Insert or update review (if user already reviewed this product)
        g.conn.execute(text("""
            INSERT INTO reviews (user_id, product_id, rating, review_text)
            VALUES (:uid, :pid, :rating, :text)
            ON CONFLICT (user_id, product_id) DO UPDATE
            SET rating = EXCLUDED.rating,
                review_text = EXCLUDED.review_text
        """), {
            'uid': user_id,
            'pid': product_id,
            'rating': rating,
            'text': review_text
        })
        g.conn.commit()
        return redirect(f'/product/{product_id}')

    # Fetch all reviews
    reviews = g.conn.execute(text("""
        SELECT r.rating, r.review_text, u.first_name, u.last_name
        FROM reviews r
        JOIN users u ON r.user_id = u.user_id
        WHERE r.product_id = :pid
    """), {'pid': product_id}).fetchall()

    return render_template('product_reviews.html', product=product, reviews=reviews, user_id=user_id)


# --------------------- ADD TO CART ---------------------
@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/login')

    product_id = request.form['product_id']
    result = g.conn.execute(text("SELECT shippingcart_id FROM shipping_carts WHERE user_id = :uid"), {'uid': user_id}).fetchone()

    if result:
        cart_id = result[0]
    else:
        result = g.conn.execute(text(
            "INSERT INTO shipping_carts (user_id) VALUES (:uid) RETURNING shippingcart_id"
        ), {'uid': user_id})
        cart_id = result.fetchone()[0]

    g.conn.execute(text("""
        INSERT INTO added_to (shippingcart_id, product_id)
        VALUES (:cid, :pid) ON CONFLICT DO NOTHING
    """), {'cid': cart_id, 'pid': product_id})
    g.conn.commit()

    return redirect('/cart')

@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/login')

    product_id = request.form.get('product_id')

    # Find the user's cart
    cart_id_result = g.conn.execute(text("""
        SELECT shippingcart_id FROM shipping_carts WHERE user_id = :uid
    """), {'uid': user_id}).fetchone()

    if cart_id_result:
        cart_id = cart_id_result[0]
        g.conn.execute(text("""
            DELETE FROM added_to
            WHERE shippingcart_id = :cid AND product_id = :pid
        """), {'cid': cart_id, 'pid': product_id})
        g.conn.commit()

    return redirect('/cart')


# --------------------- CART ---------------------
@app.route('/cart')
def cart():
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/login')

    result = g.conn.execute(text("""
        SELECT shippingcart_id FROM shipping_carts WHERE user_id = :uid
    """), {'uid': user_id}).fetchone()

    if not result:
        return render_template("cart.html", cart_items=[], total_cost=0)

    cart_id = result[0]

    # Get products in cart
    cursor = g.conn.execute(text("""
        SELECT p.product_id, p.product_name, p.price
        FROM added_to a
        JOIN products p ON a.product_id = p.product_id
        WHERE a.shippingcart_id = :cid
    """), {'cid': cart_id})

    cart_items = cursor.fetchall()
    cursor.close()

    total_cost = sum(row[2] for row in cart_items)

    return render_template("cart.html", cart_items=cart_items, total_cost=total_cost)


# --------------------- CHECKOUT ---------------------
@app.route('/checkout', methods=['POST'])
def checkout():
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/login')

    # Get the user's cart ID
    cart_result = g.conn.execute(text("""
        SELECT shippingcart_id FROM shipping_carts WHERE user_id = :uid
    """), {'uid': user_id}).fetchone()

    if not cart_result:
        return "No cart found."

    cart_id = cart_result[0]

    # Get all products in the cart
    cart_products = g.conn.execute(text("""
        SELECT product_id FROM added_to WHERE shippingcart_id = :cid
    """), {'cid': cart_id}).fetchall()

    if not cart_products:
        return "Cart is empty."

    for row in cart_products:
        product_id = row[0]

        # Insert order
        order_result = g.conn.execute(text("""
            INSERT INTO orders (user_id, product_id, order_status, order_date, delivery_date, amount)
            VALUES (:uid, :pid, 'pending', CURRENT_DATE, CURRENT_DATE + INTERVAL '3 days', 1)
            RETURNING order_id
        """), {'uid': user_id, 'pid': product_id})
        order_id = order_result.fetchone()[0]

        # Insert dummy payment
        g.conn.execute(text("""
            INSERT INTO payments (order_id, user_id, value, method, payment_status)
            VALUES (:oid, :uid, 100, 'credit card', 'pending')
        """), {'oid': order_id, 'uid': user_id})

        # Reduce stock of the product
        g.conn.execute(text("""
            UPDATE products
            SET stock_quantity = stock_quantity - 1
            WHERE product_id = :pid AND stock_quantity > 0
        """), {'pid': product_id})

    # Clear the cart
    g.conn.execute(text("""
        DELETE FROM added_to WHERE shippingcart_id = :cid
    """), {'cid': cart_id})

    g.conn.commit()
    return redirect('/payment')


# --------------------- PAYMENT ---------------------
@app.route('/payment')
def payment():
    return render_template("payment.html")

# --------------------- PROCESS PAYMENT (Update method + complete) ---------------------
@app.route('/process_payment', methods=['POST'])
def process_payment():
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/login')

    method = request.form['method']

    # Get the latest pending payment for the user
    payment_row = g.conn.execute(text("""
        SELECT payment_id FROM payments
        WHERE user_id = :uid AND payment_status = 'pending'
        ORDER BY payment_id DESC
        LIMIT 1
    """), {'uid': user_id}).fetchone()

    if not payment_row:
        return "No pending payment found."

    payment_id = payment_row[0]

    # Update the method and set status to completed
    g.conn.execute(text("""
        UPDATE payments
        SET method = :method, payment_status = 'completed'
        WHERE payment_id = :pid
    """), {'method': method, 'pid': payment_id})

    g.conn.commit()

    return render_template('payment.html')

# --------------------- ORDERS ---------------------
@app.route('/orders')
def orders():
    user_id = session.get('user_id')

    if not user_id:
        return redirect('/login')

    query = text("""
        SELECT o.order_id, p.product_name, o.order_status, o.order_date, o.delivery_date, o.amount
        FROM orders o
        JOIN products p ON o.product_id = p.product_id
        WHERE o.user_id = :uid
        ORDER BY o.order_date DESC
    """)
    cursor = g.conn.execute(query, {'uid': user_id})
    user_orders = cursor.fetchall()
    cursor.close()

    return render_template("orders.html", orders=user_orders)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8111, debug=True, use_reloader=False)


