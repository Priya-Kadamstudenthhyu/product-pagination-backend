# CodeVector Internship - 200k Products Backend (Python)

This is the completed take-home task for the CodeVector Internship. The backend has been completely written in Python using FastAPI to ensure simplicity, speed, and ease of demonstration during live interviews.

## Technology Choices
- **Backend Framework**: Python with FastAPI. FastAPI is incredibly fast, modern, and requires very little boilerplate. 
- **Database**: PostgreSQL (Neon/Supabase) via `psycopg2`. Using raw SQL queries demonstrates a direct understanding of how cursor pagination works under the hood without relying on black-box ORMs.
- **Frontend**: Vanilla HTML/JS with a custom CSS design system. It avoids build step complexities while delivering a sleek, modern UI with infinite scroll.

## The Pagination Problem
The key requirement was to: *"Show the correct data while data is changing. If 50 new products are added/updated while someone is browsing, they must not see the same product twice or miss one."*

### Solution: Cursor-Based Pagination
Offset-based pagination (`OFFSET X LIMIT Y`) fails in concurrent environments. If you are on page 2 (Offset 50) and 50 new items are inserted at the top, the items that were previously on page 1 get pushed to page 2. When you query page 2, you see them again!

**How this solution fixes it:**
We use the `id` and `created_at` fields to form a stable cursor.
- Products are indexed and sorted by `(created_at DESC, id DESC)` to ensure deterministic ordering.
- When requesting the next batch, the client passes the `id` of the last product it saw.
- The database queries strictly for rows where `(created_at, id) < (cursor_created_at, cursor_id)`.
- If new rows are inserted, they appear at the top of the list and never push existing rows down in relation to the cursor.

## Quick Start (Local Development)

1. **Install dependencies**:
   Make sure you have Python installed, then run:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Database**:
   Copy `.env.example` to `.env`, then set your Neon connection string:
   ```env
   DATABASE_URL="postgresql://[user]:[password]@[neon-hostname]/[dbname]?sslmode=require"
   ```
   Keep `.env` private. It contains secrets and should not be committed to GitHub.

3. **Initialize Database & Seed Data**:
   This script will automatically create the `products` table, set up the composite index, and perform bulk inserts of 200,000 products very quickly.
   ```bash
   python seed.py
   ```

4. **Start the Server**:
   ```bash
   uvicorn main:app --reload --port 3000
   ```
   The backend API and Frontend UI will be served at `http://localhost:3000`.

## Deployment to Render

1. Create a free PostgreSQL database on [Neon.tech](https://neon.tech/).
2. Deploy this repository to Render as a "Web Service".
3. Set the Build Command: `pip install -r requirements.txt`
4. Set the Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add your `DATABASE_URL` in the Render environment variables.

## AI Usage Note
AI was used to:
- Quickly scaffold the FastAPI server and raw SQL queries using `psycopg2`.
- Write the `seed.py` script utilizing `execute_values` for maximum bulk-insert performance.
- Style the frontend UI using standard Vanilla CSS to meet the "rich aesthetics" requirement without relying on external libraries.
- The core logic around composite indices and cursor pagination was carefully crafted to guarantee mathematical correctness against race conditions.
