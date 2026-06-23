from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv
import random

load_dotenv()

app = FastAPI()

def get_db_connection():
    # Use sslmode=require for Neon
    return psycopg2.connect(os.environ.get("DATABASE_URL"))

@app.get("/api/products")
def get_products(limit: int = 50, cursor: str = None, category: str = None):
    # Ensure limit is sensible
    limit = min(max(limit, 1), 100)
    
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # We want cursor-based pagination. Order is created_at DESC, id DESC.
            query = "SELECT * FROM products"
            params = []
            conditions = []
            
            if category and category != "All":
                conditions.append("category = %s")
                params.append(category)
                
            if cursor:
                # If there's a cursor, fetch the row first to get its created_at
                cur.execute("SELECT created_at FROM products WHERE id = %s", (cursor,))
                row = cur.fetchone()
                if row:
                    cursor_created_at = row['created_at']
                    # Rows must be strictly before the cursor in sort order
                    conditions.append("(created_at, id) < (%s, %s)")
                    params.extend([cursor_created_at, cursor])
                else:
                    # Invalid cursor, return empty
                    return {"data": [], "nextCursor": None}
                    
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
                
            query += " ORDER BY created_at DESC, id DESC LIMIT %s"
            params.append(limit)
            
            cur.execute(query, params)
            products = cur.fetchall()
            
            # Format datetime for JSON response (like Prisma does)
            for p in products:
                if 'created_at' in p and p['created_at']:
                    p['created_at'] = p['created_at'].isoformat()
                if 'updated_at' in p and p['updated_at']:
                    p['updated_at'] = p['updated_at'].isoformat()
            
            next_cursor = products[-1]['id'] if len(products) == limit else None
            
            return {"data": products, "nextCursor": next_cursor}
    except Exception as e:
        print("Error fetching products:", e)
        return JSONResponse(status_code=500, content={"error": str(e)})
    finally:
        conn.close()

@app.get("/api/categories")
def get_categories():
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT DISTINCT category FROM products ORDER BY category ASC")
            categories = [row[0] for row in cur.fetchall()]
            return {"data": categories}
    except Exception as e:
        print("Error fetching categories:", e)
        return JSONResponse(status_code=500, content={"error": str(e)})
    finally:
        conn.close()

@app.post("/api/simulate")
def simulate_new_items():
    CATEGORIES = ['Electronics', 'Clothing', 'Home & Kitchen', 'Books']
    ADJECTIVES = ['New', 'Fresh', 'Latest']
    NOUNS = ['Arrival', 'Item', 'Product']
    
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            from psycopg2.extras import execute_values
            import uuid
            from datetime import datetime
            
            now = datetime.utcnow()
            values = []
            for _ in range(50):
                _id = str(uuid.uuid4())
                name = f"{random.choice(ADJECTIVES)} {random.choice(NOUNS)} {random.randint(0, 1000)}"
                cat = random.choice(CATEGORIES)
                price = round(random.uniform(5, 100), 2)
                values.append((_id, name, cat, price, now, now))
                
            execute_values(cur, """
                INSERT INTO products (id, name, category, price, created_at, updated_at)
                VALUES %s
            """, values)
            conn.commit()
            
            return {"success": True, "message": "Inserted 50 new products"}
    except Exception as e:
        print("Error simulating items:", e)
        return JSONResponse(status_code=500, content={"error": str(e)})
    finally:
        conn.close()

# Mount the static directory to serve index.html, style.css, app.js
app.mount("/", StaticFiles(directory="public", html=True), name="public")
