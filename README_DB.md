# Database Migration Guide

This guide explains how to migrate your Arxiv Daily data from static Markdown/JSON files to a Supabase (PostgreSQL) database. This approach solves the issue of the repository size growing indefinitely.

## Prerequisites

1.  **Supabase Account**: Create a free account at [supabase.com](https://supabase.com).
2.  **Project**: Create a new project (e.g., named "ai-toutiao").

## Step 1: Get Your Keys

1.  Log in to your [Supabase Dashboard](https://supabase.com/dashboard).
2.  Click on your project.
3.  In the left sidebar, click the **Settings** icon (gear icon) ⚙️ at the bottom.
4.  Click on **API**.
5.  You will see the **Project URL** and **Project API keys**.

   *   **Project URL**: This is your `SUPABASE_URL`.
   *   **anon public**: This is your `SUPABASE_ANON_KEY` (Safe for frontend).
   *   **service_role secret**: This is your `SUPABASE_SERVICE_ROLE_KEY` (Keep secret! For Python script only).

## Step 2: Database Setup

1.  Go to the **SQL Editor** in your Supabase dashboard (icon looking like `>_` on the left).
2.  Click **New Query**.
3.  Copy the content of `scripts/db_schema.sql` from this repository.
4.  Paste it into the SQL Editor and click **Run** (bottom right).
   *   *Result*: This creates the `papers` table and indexes.

## Step 3: Environment Configuration

You need to set up environment variables for both the migration script (Python) and the frontend (React).

### For Migration (Python Script)

These keys allow the script to write data to your database. Run these commands in your terminal:

```bash
# Replace with your actual URL and SERVICE_ROLE key
export SUPABASE_URL="https://your-project-id.supabase.co"
export SUPABASE_SERVICE_ROLE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." 
```

### For Frontend (Vercel / Local)

These keys allow the website to read data.

**Option A: Local Development**
Create a `.env` file in the project root:

```env
SUPABASE_URL="https://your-project-id.supabase.co"
SUPABASE_ANON_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Option B: Vercel Deployment**
1. Go to your Vercel Project Dashboard.
2. Click **Settings** > **Environment Variables**.
3. Add the following variables:
   *   `SUPABASE_URL`: (Your Project URL)
   *   `SUPABASE_ANON_KEY`: (Your `anon` key)

> **Important**: Never use the `service_role` key in your frontend or Vercel environment variables! It bypasses security rules.

## Step 4: Migrate Data

Run the migration script to parse all existing Markdown files and upload them to the database.

```bash
# Install dependencies
pip install supabase

# Run migration
python scripts/migrate_to_supabase.py
```

This script supports "upsert", so you can run it multiple times without creating duplicates.

## Step 5: Verify Frontend

The frontend code in `src/pages/arxiv-daily.tsx` has been updated to automatically check for Supabase configuration.

1.  Start your development server: `npm start`.
2.  If the environment variables are set correctly, the page will fetch data from Supabase.
3.  If not, it will gracefully fallback to the local JSON files.

## Step 6: Update Workflow (How to save space)

To stop the repository from growing:

1.  Add `docs/daily/**/*.md` and `static/data/*.json` to your `.gitignore` file.
2.  In your daily update workflow:
    *   Run `python get_daily_arxiv_paper.py` (generates MD files locally).
    *   Run `python scripts/migrate_to_supabase.py` (pushes to DB).
    *   Do **not** commit the generated MD/JSON files.

This way, your data lives in the database, and your git repository remains lightweight.
