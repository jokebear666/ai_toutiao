#!/usr/bin/env python3
import os
import re
import json
import argparse
from datetime import datetime, timedelta

def norm_category(cat):
    return re.sub(r'[^a-z0-9]', '', (cat or '').lower())

def _parse_week_range(name):
    m = re.match(r'^(\d{8})-(\d{8})\.md$', name)
    if not m:
        return None, None
    try:
        start = datetime.strptime(m.group(1), '%Y%m%d')
        end = datetime.strptime(m.group(2), '%Y%m%d')
        return start, end
    except Exception:
        return None, None

def recent_week_files(dir_path, months=3):
    if not os.path.isdir(dir_path):
        return []
    cutoff = datetime.today() - timedelta(days=months * 30)
    candidates = []
    for n in os.listdir(dir_path):
        if re.match(r'^\d{8}-\d{8}\.md$', n):
            _, end = _parse_week_range(n)
            if end is None:
                continue
            if end >= cutoff:
                candidates.append((end, n))
    candidates.sort(key=lambda x: x[0])
    return [os.path.join(dir_path, n) for _, n in candidates]

def parse_week_md(file_path):
    if not file_path or not os.path.exists(file_path):
        return {"week": "", "items": []}
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    week = ""
    m = re.search(r'^#\s*([0-9\-]+)', content, re.M)
    if m:
        week = m.group(1).strip()
    items = []
    headers = list(re.finditer(r'(^|\n)##\s*(\d{4}-\d{2}-\d{2})', content))
    for i, hm in enumerate(headers):
        day = hm.group(2)
        start = hm.end()
        end = headers[i+1].start() if i+1 < len(headers) else len(content)
        section = content[start:end]
        tms = list(re.finditer(r'^-\s+\*\*\[[^\]]+\]\s*(.*?)\*\*', section, re.M))
        for j, tm in enumerate(tms):
            title = tm.group(1).strip()
            entry_start = tm.end()
            entry_end = tms[j+1].start() if j+1 < len(tms) else len(section)
            entry = section[entry_start:entry_end]
            am = re.search(r'^\s+-\s+\*\*authors:\*\*\s*(.+)$', entry, re.M)
            lm = re.search(r'^\s+-\s+\*\*link:\*\*\s*(\S+)', entry, re.M)
            tmn = re.search(r'^\s+-\s+\*\*thumbnail:\*\*\s*(\S+)', entry, re.M)
            authors = am.group(1).strip() if am else ""
            link = lm.group(1).strip() if lm else None
            thumbnail = tmn.group(1).strip() if tmn else None
            items.append({"title": title, "authors": authors, "link": link, "day": day, "thumbnail": thumbnail})
    return {"week": week, "items": items}

def build(docs_dir, output_path, max_items_per_cat, months=3):
    categories = []
    base = docs_dir
    for entry in sorted(os.listdir(base)):
        full = os.path.join(base, entry)
        if not os.path.isdir(full):
            continue
        label = entry.replace('_', '.')
        slug = norm_category(label)
        files = recent_week_files(full, months=months)
        all_items = []
        weeks = []
        for fp in files:
            parsed = parse_week_md(fp)
            if parsed.get('week'):
                weeks.append(parsed['week'])
            all_items.extend(parsed.get('items', []))
        # 去重（优先使用 link，其次使用 title+day）
        seen = set()
        deduped = []
        for it in all_items:
            key = it.get('link') or (it.get('title'), it.get('day'))
            if key in seen:
                continue
            seen.add(key)
            deduped.append(it)
        # 按日期降序
        def _parse_day(s):
            try:
                return datetime.strptime(s or '', '%Y-%m-%d')
            except Exception:
                return datetime.min
        deduped.sort(key=lambda it: _parse_day(it.get('day')), reverse=True)
        cats_items = deduped[:max_items_per_cat]
        latest_week = weeks[-1] if weeks else ""
        categories.append({"label": label, "slug": slug, "week": latest_week, "items": cats_items})
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({"categories": categories}, f, ensure_ascii=False, indent=2)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--docs-dir", default="docs/daily")
    ap.add_argument("--output", default="static/data/arxiv_daily.json")
    ap.add_argument("--max-items-per-cat", type=int, default=24)
    ap.add_argument("--months", type=int, default=3)
    args = ap.parse_args()
    build(args.docs_dir, args.output, args.max_items_per_cat, months=args.months)
    print(f"写入静态数据: {args.output}")

if __name__ == "__main__":
    main()
