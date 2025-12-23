#!/usr/bin/env python3
import argparse
import os
import io
import json
import tempfile
import requests
import hashlib

def download_pdf(url):
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    fd, path = tempfile.mkstemp(suffix=".pdf")
    os.close(fd)
    with open(path, "wb") as f:
        f.write(r.content)
    return path

def save_bytes(b, path):
    with open(path, "wb") as f:
        f.write(b)

def image_size_from_bytes(b):
    try:
        from PIL import Image
        im = Image.open(io.BytesIO(b))
        return im.size
    except Exception:
        return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf-url", default=None)
    ap.add_argument("--pdf-path", default=None)
    ap.add_argument("--out-dir", default="tmp_extract")
    ap.add_argument("--figure", type=int, default=1)
    ap.add_argument("--save", default=None)
    ap.add_argument("--upload", action="store_true")
    args = ap.parse_args()

    pdf_path = args.pdf_path
    if not pdf_path and args.pdf_url:
        pdf_path = download_pdf(args.pdf_url)
    if not pdf_path:
        print(json.dumps({"error": "missing pdf"}, ensure_ascii=False))
        return

    os.makedirs(args.out_dir, exist_ok=True)

    from get_daily_arxiv_paper import CompletePaperProcessor
    proc = CompletePaperProcessor(enable_thumbnails=True)

    img_bytes = None
    ext = None
    img_bytes, ext = proc.render_figure_union_region_by_caption(pdf_path, figure_no=args.figure)
    if not img_bytes:
        print("联合渲染失败，尝试按标题渲染")
        img_bytes, ext = proc.render_figure_region_by_caption(pdf_path, figure_no=args.figure)
    if not img_bytes:
        print("按标题渲染失败，尝试按区域渲染")
        img_bytes, ext = proc.render_largest_image_region(pdf_path)
    if not img_bytes:
        print("按区域渲染失败，尝试按页面渲染")
        img_bytes, ext = proc.render_best_page(pdf_path)
    if not img_bytes:
        print("按页面渲染失败，无法提取图片")
        print(json.dumps({"error": "no image"}, ensure_ascii=False))
        return
    if (ext or "").lower() != "webp":
        converted, cext = proc.convert_to_webp(img_bytes)
        if converted:
            img_bytes, ext = converted, cext
    saved = None
    if args.save:
        save_bytes(img_bytes, args.save)
        saved = args.save
    else:
        default_path = os.path.join(args.out_dir, f"thumbnail.{ext or 'webp'}")
        save_bytes(img_bytes, default_path)
        saved = default_path
    url = None
    if args.upload:
        url = proc.upload_to_r2(img_bytes, ext or "webp")
    h = hashlib.sha256(img_bytes).hexdigest()
    size_px = image_size_from_bytes(img_bytes)
    print(json.dumps({"ext": ext, "size": len(img_bytes), "sha256": h, "saved": saved, "url": url, "img_size": size_px}, ensure_ascii=False))

if __name__ == "__main__":
    main()
