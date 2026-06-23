import psycopg2
from psycopg2.extras import execute_values
import os
import random
import uuid
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    return psycopg2.connect(os.environ.get("DATABASE_URL"))

CATEGORIES = [
  'Electronics', 'Clothing', 'Home & Kitchen', 'Books', 'Sports',
  'Beauty', 'Toys', 'Automotive', 'Health', 'Garden',
  'Tools', 'Pet Supplies', 'Office Products', 'Grocery', 'Music'
]
ADJECTIVES = ['Amazing', 'Incredible', 'Awesome', 'Fantastic', 'Superb', 'Sleek', 'Durable', 'Modern', 'Vintage', 'Premium', 'Basic', 'Essential']
NOUNS = ['Widget', 'Device', 'Appliance', 'Gadget', 'Tool', 'Machine', 'Instrument', 'Accessory', 'Item', 'Product', 'Gear', 'Equipment']

def main():
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            print("Creating products table if not exists...")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id VARCHAR(36) PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    category VARCHAR(255) NOT NULL,
                    price FLOAT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP NOT NULL
                )
            """)
            
            # Create composite index for efficient cursor pagination
            print("Creating indexes...")
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_products_created_id 
                ON products (created_at DESC, id DESC)
            """)
            
            print("Clearing existing products...")
            cur.execute("TRUNCATE TABLE products")
            
            print("Starting DB Seed for 200,000 products...")
            
            TOTAL_RECORDS = 200_000
            CHUNK_SIZE = 10_000
            
            start_date = datetime(2023, 1, 1)
            end_date = datetime(2024, 1, 1)
            time_diff = end_date - start_date
            
            for i in range(0, TOTAL_RECORDS, CHUNK_SIZE):
                values = []
                for _ in range(CHUNK_SIZE):
                    _id = str(uuid.uuid4())
                    name = f"{random.choice(ADJECTIVES)} {random.choice(NOUNS)} {random.randint(0, 1000)}"
                    category = random.choice(CATEGORIES)
                    price = round(random.uniform(5, 1000), 2)
                    random_days = random.random() * time_diff.total_seconds()
                    created_at = start_date + timedelta(seconds=random_days)
                    
                    values.append((_id, name, category, price, created_at, created_at))
                
                execute_values(cur, """
                    INSERT INTO products (id, name, category, price, created_at, updated_at)
                    VALUES %s
                """, values)
                
                print(f"Inserted {i + CHUNK_SIZE} / {TOTAL_RECORDS} products")
                
            conn.commit()
            print("Seed completed successfully!")
            
    except Exception as e:
        print("An error occurred:", e)
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    main()
