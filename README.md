**Team Members Information**
- Yasemin Yuksel (yy3294)
- Yeyuxi Yi (yy3561)

**PostgreSQL Database Information** --> psql -U yy3294 -h 34.148.223.31 -d proj1part2
- database account (UNI): yy3294
- host: 34.148.223.31
- database name: proj1part2

**Live Web Application URL:**
- http://34.73.133.143:8111

**Implemented Features from Part 1 Proposal:**
- We successfully implemented the customer-facing side of the e-commerce application with
the following features:
  * view all products
  * filter products by category and price range
  * view individual product details
  * add products to a shopping cart
  * remove products from shopping cart
  * view orders
  * add reviews for products
- All the data is dynamically fetched from our PostgreSQL datavase via SQLAlchemy

Following the feedback we received from our TA after our Part 1 submission, we decided to place our focus on the customer side. 

**Bonus Enhancements:**
- pages styles with basic HTML and form filters
- cart summary showing items
- validations for product filtering

**Interesting Pages with Database Logic:**

*- /products --> Product Filtering with SQL Query*

   * This page allows users to filter products based on optional input criteria such    as category, minimum price, and maximum price. These inputs are captured from a      front-end HTML form and used to dynamically build a SQL query with appropriate       WHERE clauses.

      SELECT product_id, product_name, category, image, description, price, stock_quantity
    
      FROM products
    
      WHERE category = :cat AND price BETWEEN :min_price AND :max_price
    
      ORDER BY product_id;
    
   
  * This page is interesting because it showcases the construction of dynamic queries using     user-defined filters, while safely parameterizing SQL inputs to avoid injection      attacks. It also illustrates how the web interface connects directly to backend      logic by translating user interactions into meaningful database operations.

*- /cart --> Retrieving Session-Based Shopping Cart Contents*

  * This page displays the products currently in the user’s cart. The cart is stored   in a session variable as a list of product_ids, and the backend retrieves full       product information by querying the database using a PostgreSQL ANY clause.
    
      product_ids = session.get("cart", [])
    
      query = text("SELECT * FROM products WHERE product_id = ANY(:ids)")
    
      products = g.conn.execute(query, {"ids": product_ids}).fetchall()
    
    
  * This page is interesting because it integrates client-side session management      with server-side SQL querying, demonstrating how user activity on the front-end      directly affects query execution on the backend. It also highlights the use of       array-safe querying in PostgreSQL, which efficiently handles variable-length lists   of IDs.

