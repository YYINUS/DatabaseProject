import sys
from sqlalchemy import create_engine, text

# Replace these credentials with your own
DATABASE_USERNAME = "yy3294"
DATABASE_PASSWORD = "969446"
DATABASE_HOST = "34.148.223.31"
DATABASE_URI = f"postgresql://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_HOST}/proj1part2"

def main():
    # Create the engine
    engine = create_engine(DATABASE_URI)

    try:
        with engine.connect() as conn:
            # Same query as in your Flask code
            query = text("""
                SELECT product_id, product_name, category, image, description, price, stock_quantity
                FROM products
                ORDER BY product_id
            """)
            result = conn.execute(query)

            # Fetch all rows
            rows = result.fetchall()

            # Print how many rows we got
            print(f"Number of products returned: {len(rows)}")

            # Print each row
            for row in rows:
                print(row)

    except Exception as e:
        print("Error during query:", e)

if __name__ == "__main__":
    main()
