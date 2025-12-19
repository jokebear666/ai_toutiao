#!/usr/bin/env python3
import argparse
import hashlib
import io
import os
import tempfile
import requests

def download_pdf(url):
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    fd, path = tempfile.mkstemp(suffix=".pdf")
    os.close(fd)
    with open(path, "wb") as f:
        f.write(r.content)
    return path

def extract_first_image(pdf_path):
    import fitz
    doc = fitz.open(pdf_path)
    for page_index in range(min(2, len(doc))):
        page = doc.load_page(page_index)
        imgs = page.get_images(full=True)
        if imgs:
            imgs.sort(key=lambda m: (m[2] or 0) * (m[3] or 0), reverse=True)
            xref = imgs[0][0]
            base = doc.extract_image(xref)
            b = base.get("image")
            ext = base.get("ext", "png")
            if b:
                return b, ext
    return None, None

def render_first_page(pdf_path, max_width=640):
    import fitz
    doc = fitz.open(pdf_path)
    if len(doc) == 0:
        return None, None
    page = doc.load_page(0)
    w = page.rect.width or 1.0
    z = max_width / w
    mat = fitz.Matrix(z, z)
    pix = page.get_pixmap(matrix=mat, alpha=False)
    return pix.tobytes("webp"), "webp"

def convert_to_webp(image_bytes, max_width=640, quality=70):
    from PIL import Image
    buf = io.BytesIO(image_bytes)
    img = Image.open(buf)
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    w, h = img.size
    if w > max_width:
        s = max_width / float(w)
        img = img.resize((int(w * s), int(h * s)))
    out = io.BytesIO()
    img.save(out, format="WEBP", quality=quality, method=6)
    return out.getvalue(), "webp"

def upload_to_r2(image_bytes, ext="webp"):
    import boto3
    from botocore.config import Config
    endpoint = os.environ.get("R2_ENDPOINT_URL")
    access_key = os.environ.get("R2_ACCESS_KEY_ID")
    secret_key = os.environ.get("R2_SECRET_ACCESS_KEY")
    bucket = os.environ.get("R2_BUCKET")
    public = os.environ.get("R2_PUBLIC_URL")
    if not all([endpoint, access_key, secret_key, bucket, public]):
        return None
    s3 = boto3.client(
        "s3",
        region_name="auto",
        endpoint_url=endpoint,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        config=Config(signature_version="s3v4"),
    )
    h = hashlib.sha256(image_bytes).hexdigest()
    key = f"thumbnails/{h}_w640_q70.{ext}"
    ct = f"image/{'jpeg' if ext == 'jpg' else ext}"
    # try:
    #     s3.put_object(Bucket=bucket, Key=key, Body=image_bytes, ContentType=ct, CacheControl="public, max-age=31536000, immutable")
    # except Exception as e:
    #     print(json_dump({"error": "upload_failed", "detail": str(e)}))
    #     return None
    s3.put_object(Bucket=bucket, Key=key, Body=image_bytes, ContentType=ct, CacheControl="public, max-age=31536000, immutable")

    return f"{public}/{key}"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf-url", default=None)
    ap.add_argument("--pdf-path", default=None)
    ap.add_argument("--save", default=None)
    ap.add_argument("--upload", action="store_true")
    args = ap.parse_args()
    pdf_path = args.pdf_path
    if not pdf_path and args.pdf_url:
        pdf_path = download_pdf(args.pdf_url)
    if not pdf_path:
        print("{""error"": ""missing pdf""}")
        return
    b, ext = extract_first_image(pdf_path)
    if not b:
        b, ext = render_first_page(pdf_path)
    if not b:
        print("{""error"": ""no image""}")
        return
    if (ext or "").lower() != "webp":
        wb, wext = convert_to_webp(b)
        if wb:
            b, ext = wb, wext
    saved = None
    if args.save:
        with open(args.save, "wb") as f:
            f.write(b)
        saved = args.save
    url = None
    if args.upload:
        url = upload_to_r2(b, ext or "webp")
    h = hashlib.sha256(b).hexdigest()
    print(json_dump({"ext": ext, "size": len(b), "sha256": h, "saved": saved, "url": url}))

def json_dump(obj):
    import json
    return json.dumps(obj, ensure_ascii=False)

if __name__ == "__main__":
    main()
