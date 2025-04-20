' COMS W4111 – Project Part 4: PostgreSQL Schema Expansion
' Team 73 Submission

' Teammates:
' - Yasemin Yuksel (UNI: yy3294)
' - Yeyuxi Yi (UNI: yy3561)

' PostgreSQL Database for Grading:
' - UNI: yy3294
' - Host: 34.148.223.31
' - Database: proj1part2

' =============================
' OVERVIEW
' =============================
' In this project, we expanded our schema from Project Part 3 by implementing three advanced features:
' 1. Full-text search on review text using tsvector.
' 2. An array attribute for product tags.
' 3. A trigger to automatically update a user’s last_order_date.
' These features were not present in Part 3, and are meaningfully integrated into our ecommerce database schema.

' =============================
' FEATURE 1 – Full-Text Search on Reviews
' =============================
' Description:
' We added a tsvector column review_vector to the reviews table to enable full-text search on review_text.
' We also created a trigger to automatically update this vector upon insert or update, and indexed it using GIN.

' Implementation:
ALTER TABLE reviews ADD COLUMN review_vector tsvector;
UPDATE reviews SET review_vector = to_tsvector('english', review_text);
CREATE INDEX idx_review_vector ON reviews USING GIN(review_vector);

CREATE OR REPLACE FUNCTION update_review_vector() RETURNS trigger AS $$
BEGIN
  NEW.review_vector := to_tsvector('english', NEW.review_text);
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_review_vector_update
BEFORE INSERT OR UPDATE ON reviews
FOR EACH ROW
EXECUTE FUNCTION update_review_vector();

' Query Example:
SELECT * FROM reviews
WHERE review_vector @@ to_tsquery('english', 'great & quality');

' Explanation:
' This query returns reviews that include both "great" and "quality".

' =============================
' FEATURE 2 – Array Attribute for Product Tags
' =============================
' Description:
' We added a tags TEXT[] array to the products table to support multi-tag categorization like "wireless", "gaming", etc.

' Implementation:
ALTER TABLE products ADD COLUMN tags TEXT[];

UPDATE products SET tags = ARRAY['wireless', 'gaming', 'high-precision'] WHERE product_id = 7;
UPDATE products SET tags = ARRAY['kitchen', 'appliance'] WHERE product_id = 9;
UPDATE products SET tags = ARRAY['ergonomic', 'furniture'] WHERE product_id = 8;
UPDATE products SET tags = ARRAY['noise-canceling', 'audio'] WHERE product_id = 3;

' Query Example:
SELECT product_name, tags
FROM products
WHERE 'wireless' = ANY(tags);

' Explanation:
' Returns products tagged with the keyword 'wireless'.

' =============================
' FEATURE 3 – Trigger to Track Last Order Date
' =============================
' Description:
' We added last_order_date to users and created a trigger to automatically update it upon order insertion.

' Implementation:
ALTER TABLE users ADD COLUMN last_order_date DATE;

CREATE OR REPLACE FUNCTION update_last_order_date() RETURNS trigger AS $$
BEGIN
  UPDATE users
  SET last_order_date = NEW.order_date
  WHERE user_id = NEW.user_id;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_last_order
AFTER INSERT ON orders
FOR EACH ROW
EXECUTE FUNCTION update_last_order_date();

' Example Trigger Event:
INSERT INTO orders (user_id, product_id, order_status, order_date, delivery_date, amount)
VALUES (3, 1, 'pending', '2025-04-20', '2025-04-24', 1);

' Result:
' Automatically updates users.last_order_date for user_id = 3 to '2025-04-20'

SELECT user_id, last_order_date FROM users WHERE user_id = 3;

' =============================
' REQUIRED QUERIES
' =============================

' Query 1: Full-text search on reviews
SELECT * FROM reviews
WHERE review_vector @@ to_tsquery('english', 'great & quality');

' Query 2: Array query on product tags
SELECT product_name, tags
FROM products
WHERE 'wireless' = ANY(tags);

' Query 3: Trigger result for last_order_date
INSERT INTO orders (user_id, product_id, order_status, order_date, delivery_date, amount)
VALUES (3, 1, 'pending', CURRENT_DATE, CURRENT_DATE + INTERVAL '3 days', 1);

SELECT user_id, last_order_date FROM users WHERE user_id = 3;

' =============================
' NOTES
' =============================
' - All three features were newly implemented and not present in Part 3.
' - Features were selected to match realistic ecommerce use cases.
' - The database has been populated with appropriate test data.
' - Queries are tested and return correct results on the submitted PostgreSQL instance.
' - No frontend changes were made; this submission focuses solely on the backend schema.





