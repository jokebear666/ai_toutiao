import os
import json
from supabase import create_client, Client
from datetime import datetime

# Initialize Supabase client
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY") or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not url or not key:
    print("Error: SUPABASE_URL and SUPABASE_KEY (or SUPABASE_SERVICE_ROLE_KEY) environment variables are required.")
    exit(1)

supabase: Client = create_client(url, key)

# Configuration
CATEGORIES_MAP = {
    "ai": ["cs_AI"],
    "cv": ["cs_CV"],
    "ml": ["cs_LG", "stat_ML"],
    "other": ["cs_CL", "cs_RO", "cs_CR", "cs_SE"]
}

COLORS = ["#60a5fa", "#34d399", "#818cf8", "#f472b6", "#fbbf24"]

def fetch_papers(categories, limit=3):
    try:
        # Fetch papers that match any of the specified category slugs
        response = supabase.table("papers") \
            .select("id, title, published_date, authors, category_slug, tags, thumbnail_url") \
            .in_("category_slug", categories) \
            .order("published_date", desc=True) \
            .limit(limit) \
            .execute()
        
        return response.data
    except Exception as e:
        print(f"Error fetching papers for {categories}: {e}")
        return []

def format_paper(paper, index):
    # Extract first author
    authors = paper.get("authors", [])
    if isinstance(authors, list) and authors:
        author = authors[0]
    elif isinstance(authors, str):
        author = authors.split(',')[0]
    else:
        author = "Unknown"
        
    # Categories/Tags for label
    # Prefer first tag, fallback to category_slug
    tags = paper.get("tags", [])
    if tags and isinstance(tags, list) and len(tags) > 0:
        tag_label = tags[0]
    else:
        tag_label = paper.get("category_slug", "Paper").replace("_", ".")
    
    # Color
    color = COLORS[index % len(COLORS)]
    
    return {
        "id": paper.get("id"),
        "title": paper.get("title"),
        "date": str(paper.get("published_date")),
        "author": author,
        "tags": [{"label": tag_label, "color": color}],
        "hasCode": False,  # Default to False
        "imgUrl": paper.get("thumbnail_url")
    }

def main():
    dashboard_data = {}
    
    for key, cats in CATEGORIES_MAP.items():
        print(f"Fetching {key} papers...")
        papers = fetch_papers(cats)
        formatted = [format_paper(p, i) for i, p in enumerate(papers)]
        dashboard_data[key] = formatted
        
    # Output path - relative to this script
    output_path = os.path.join(os.path.dirname(__file__), "../src/data/dashboard.json")
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, "w") as f:
        json.dump(dashboard_data, f, indent=2)
        
    print(f"Successfully updated dashboard data at {output_path}")

if __name__ == "__main__":
    main()
