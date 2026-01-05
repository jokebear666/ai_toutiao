import os
import re
import json
from datetime import datetime
import time

# Try to import supabase, but don't fail immediately if not installed
try:
    from supabase import create_client, Client
except ImportError:
    print("Error: 'supabase' package not found. Please run: pip install supabase")
    exit(1)

# Configuration
# Users should set these environment variables
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") # Use Service Role Key for writing

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: Please set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY environment variables.")
    print("Usage: export SUPABASE_URL='...' && export SUPABASE_SERVICE_ROLE_KEY='...' && python migrate_to_supabase.py")
    exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS_DIR = os.path.join(ROOT_DIR, 'docs', 'daily')

def escape_mdx_content(text):
    if not text:
        return text
    return re.sub(r'<(\d)', r'&lt;\1', text)

def parse_md_file(file_path, category_slug):
    if not os.path.exists(file_path):
        return []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    items_data = []
    
    # Extract entries by date headers
    # Matches ## YYYY-MM-DD
    headers = list(re.finditer(r'(^|\n)##\s*(\d{4}-\d{2}-\d{2})', content))
    
    for i, hm in enumerate(headers):
        day_str = hm.group(2)
        start = hm.end()
        end = headers[i+1].start() if i+1 < len(headers) else len(content)
        section = content[start:end]
        
        # Parse individual papers in this day section
        # Matches - **[Title]**
        tms = list(re.finditer(r'^-\s+\*\*\[[^\]]+\]\s*(.*?)\*\*', section, re.M))
        
        for j, tm in enumerate(tms):
            title = tm.group(1).strip()
            entry_start = tm.end()
            entry_end = tms[j+1].start() if j+1 < len(tms) else len(section)
            entry = section[entry_start:entry_end]
            
            # Extract fields
            am = re.search(r'^\s+-\s+\*\*authors:\*\*\s*(.+)$', entry, re.M)
            lm = re.search(r'^\s+-\s+\*\*link:\*\*\s*(\S+)', entry, re.M)
            tmn = re.search(r'^\s+-\s+\*\*thumbnail:\*\*\s*(\S+)', entry, re.M)
            cd = re.search(r'^\s+-\s+\*\*code:\*\*\s*(\S+)', entry, re.M)
            im = re.search(r'^\s+-\s+\*\*institution:\*\*\s*(.+)$', entry, re.M)
            tg = re.search(r'^\s+-\s+\*\*tags:\*\*\s*(.+)$', entry, re.M)
            cm = re.search(r'^\s+-\s+\*\*contributions:\*\*\s*(.+)$', entry, re.M)
            sm = re.search(r'^\s+-\s+\*\*Simple LLM Summary:\*\*\s*(.+)$', entry, re.M)
            mm = re.search(r'^\s+-\s+\*\*Mindmap:\*\*\s*\n\s*```mermaid\n([\s\S]+?)\n\s*```', entry, re.M)
            
            # Process fields
            authors = am.group(1).strip() if am else ""
            link = lm.group(1).strip() if lm else None
            thumbnail = tmn.group(1).strip() if tmn else None
            code = cd.group(1).strip() if cd else None
            institution = im.group(1).strip() if im else ""
            tags_raw = tg.group(1).strip() if tg else ""
            contributions = cm.group(1).strip() if cm else ""
            summary = sm.group(1).strip() if sm else ""
            mindmap = mm.group(1).strip() if mm else ""

            # Clean fields
            contributions = escape_mdx_content(contributions)
            summary = escape_mdx_content(summary)
            if mindmap:
                mindmap = mindmap.replace('"', '”')
            
            # Parse tags
            tag_list = []
            if tags_raw:
                cleaned = tags_raw.replace('[', '').replace(']', '')
                parts = cleaned.split(',')
                tag_list = [t.strip() for t in parts if t.strip()]

            if not link:
                continue # Skip if no link (key)

            items_data.append({
                "category_slug": category_slug,
                "title": title,
                "published_date": day_str,
                "authors": authors,
                "institution": institution,
                "link": link,
                "code_url": code,
                "thumbnail_url": thumbnail,
                "summary": summary,
                "contributions": contributions,
                "mindmap": mindmap,
                "tags": tag_list
            })
            
    return items_data

def migrate():
    print(f"Scanning directory: {DOCS_DIR}")
    
    # Traverse directory
    total_papers = 0
    
    for root, dirs, files in os.walk(DOCS_DIR):
        # Infer category from directory name
        # Structure: docs/daily/cs_CV/20230101-20230107.md
        rel_path = os.path.relpath(root, DOCS_DIR)
        if rel_path == '.':
            continue
            
        category_slug = os.path.basename(root) # e.g. cs_CV
        
        for file in files:
            if not file.endswith('.md'):
                continue
            
            file_path = os.path.join(root, file)
            print(f"Processing {category_slug} / {file} ...")
            
            papers = parse_md_file(file_path, category_slug)
            
            if not papers:
                continue
                
            # Batch insert/upsert
            # Supabase Python client supports upsert
            try:
                # We do it in batches of 100 to avoid request size limits
                batch_size = 50
                for i in range(0, len(papers), batch_size):
                    batch = papers[i:i+batch_size]
                    response = supabase.table('papers').upsert(batch, on_conflict='link').execute()
                    # print(f"  Inserted {len(batch)} papers.")
                
                total_papers += len(papers)
            except Exception as e:
                print(f"  Error inserting batch: {e}")
                
    print(f"Migration completed. Total papers processed: {total_papers}")

if __name__ == "__main__":
    migrate()
