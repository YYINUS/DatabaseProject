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

**Bonus Enhancements:**
- pages styles with basic HTML and form filters
- cart summary showing items
- validations for product filtering

**Interesting Pages with Database Logic:**

*- /products --> Product Filtering with SQL Query*

  * This page uses user inputs from a filter form (category, min price, max price) to dynamically construct a SELECT query with WHERE conditions:

      SELECT product_id, product_name, category, image, description, price, stock_quantity
    
      FROM products
    
      WHERE category = :cat AND price BETWEEN :min_price AND :max_price
    
      ORDER BY product_id;
    
   
  * This is interesting because it demonstrates dynamic query building based on optional user inputs
  and safely parameterizes SQL to avoid injection.

*- /cart --> Display Shopping Cart Contents*

  * This page retrieves product data for items stored in the session-based shopping cart:
    
      product_ids = session.get("cart", [])
    
      query = text("SELECT * FROM products WHERE product_id = ANY(:ids)")
    
      products = g.conn.execute(query, {"ids": product_ids}).fetchall()
    
    
  * This is interesting because it shows the integration of front-end session storage
  with backend SQL logic and uses array-safe queries (ANY) in PostgreSQL.

