#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整的论文处理脚本
只支持单个日期，不再支持日期段
"""

import requests
import argparse
import xml.etree.ElementTree as ET
import json
import csv
import os
import re
import tempfile
from datetime import datetime, timedelta
from openai import OpenAI
import concurrent.futures
from tqdm import tqdm
from bs4 import BeautifulSoup
import sys

# PDF处理相关
try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("警告: PyPDF2未安装，无法处理PDF文件。请运行: pip install PyPDF2")

def already_processed(date_str, filename="arxiv_date.txt"):
    """检查 arxiv_date.txt 当前日期是否已处理过（date_str: yyyy-mm-dd）"""
    if not os.path.exists(filename):
        return False
    try:
        with open(filename, "r") as f:
            lines = f.readlines()
            yyyymmdd_list = set(line.strip() for line in lines if line.strip())
        return date_str.replace('-', '') in yyyymmdd_list
    except Exception as e:
        print(f"读取 {filename} 错误: {e}")
        return False

def append_to_processed(date_str, filename="arxiv_date.txt"):
    """处理完成后追加日期到 arxiv_date.txt（date_str: yyyy-mm-dd）"""
    try:
        with open(filename, "a") as f:
            f.write(date_str.replace('-', '') + "\n")
    except Exception as e:
        print(f"写入 {filename} 错误: {e}")

def extract_date_from_html(html_content=None, url="https://arxiv.org/list/cs/new"):
    """
    从arXiv HTML内容中提取日期
    
    Args:
        html_content (bytes or str): HTML内容，如果提供则直接使用，否则从URL下载
        url (str): arXiv HTML页面URL，仅在html_content为None时使用
        
    Returns:
        str: 日期字符串，格式为 'YYYY-MM-DD'，如果提取失败返回None
    """
    try:
        # 如果提供了HTML内容，直接使用；否则从URL下载
        if html_content is None:
            print(f"正在从 {url} 下载HTML并提取日期...")
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            html_content = response.content
        else:
            print("从提供的HTML内容中提取日期...")
        
        # 使用BeautifulSoup解析HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 查找包含"Showing new listings for"的h3标签
        h3_tags = soup.find_all('h3')
        for h3 in h3_tags:
            text = h3.get_text()
            if 'Showing new listings for' in text:
                # 提取日期部分，格式如 "Monday, 3 November 2025"
                # 匹配日期模式：Day, DD Month YYYY
                date_pattern = r'(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),\s+(\d{1,2})\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})'
                match = re.search(date_pattern, text)
                if match:
                    day = match.group(1)
                    month_name = match.group(2)
                    year = match.group(3)
                    
                    # 月份名称到数字的映射
                    month_map = {
                        'January': '01', 'February': '02', 'March': '03', 'April': '04',
                        'May': '05', 'June': '06', 'July': '07', 'August': '08',
                        'September': '09', 'October': '10', 'November': '11', 'December': '12'
                    }
                    
                    month_num = month_map.get(month_name)
                    if month_num:
                        # 格式化日期为 YYYY-MM-DD
                        date_str = f"{year}-{month_num}-{day.zfill(2)}"
                        print(f"从HTML页面提取到日期: {date_str}")
                        return date_str
        
        print("未能在HTML页面中找到日期信息")
        return None
        
    except Exception as e:
        print(f"从HTML页面提取日期时发生错误: {e}")
        return None

class CompletePaperProcessor:
    def __init__(self, docs_daily_path="docs/daily", temp_dir="temp_pdfs", enable_thumbnails=False, enable_llm=True):
        """
        初始化完整的论文处理器
        
        Args:
            docs_daily_path (str): daily文件夹路径
            temp_dir (str): 临时PDF存储目录
        """
        self.docs_daily_path = docs_daily_path
        self.temp_dir = temp_dir
        self.enable_thumbnails = enable_thumbnails
        self.enable_llm = enable_llm
        self.ensure_directories()
        
        # 初始化OpenAI客户端
        self.client = None
        if self.enable_llm:
            self.client = OpenAI(
                api_key=os.environ.get('DEEPSEEK_API_KEY'),
                base_url="https://api.deepseek.com"
            )
    
    def ensure_directories(self):
        """确保必要的目录存在"""
        for directory in [self.docs_daily_path, self.temp_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)
    
    # ==================== arXiv论文获取功能 ====================

    def fetch_arxiv_papers(self, categories=['cs.DC', 'cs.AI'], max_results=2000, target_date=None, html_content=None, include_categories=None):
        """
        从arXiv HTML内容获取指定分类的论文，并根据papers.jsonl去重与增补
        
        Args:
            categories (list): 论文分类列表（暂时忽略，从HTML获取所有cs分类）
            max_results (int): 最大获取数量
            target_date (str): 目标日期，格式为 'YYYY-MM-DD'，本函数只考虑单个日期
            html_content (bytes): HTML内容，如果提供则直接使用，否则从URL下载
            
        Returns:
            list: 论文列表（直接从HTML解析得到的论文，不再依赖papers.jsonl）
        """
        all_papers = []
        seen_papers = set()

        # 从arXiv HTML页面获取论文
        print("正在解析HTML内容获取论文信息...")
        try:
            # 如果提供了HTML内容，直接使用；否则从URL下载
            if html_content is None:
                print("正在从 https://arxiv.org/list/cs/new 下载HTML...")
                response = requests.get('https://arxiv.org/list/cs/new', timeout=30)
                response.raise_for_status()
                html_content = response.content
            
            # 使用BeautifulSoup解析HTML
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 查找所有论文条目
            paper_entries = soup.find_all('dt')
            print(f"Found {len(paper_entries)} papers in HTML")
            
            for entry in paper_entries:
                paper_info = self._extract_paper_info_from_html(entry)
                if paper_info:
                    paper_id = paper_info.get('id', '')
                    if paper_id in seen_papers:
                        print(f"跳过重复论文: {paper_info.get('title', 'N/A')}")
                        continue
                    # 跳过修订版
                    if paper_info.get('replaced', False):
                        continue
                    # 标注关键词匹配情况（用于统计展示）
                    summary_lower = (paper_info.get("summary", "") or "").lower()
                    paper_info['rl_match'] = "reinforcement learning" in summary_lower
                    paper_info['accelerat_match'] = "accelerat" in summary_lower
                    # 可选：仅保留指定类别（测试时节省成本）
                    if include_categories:
                        cats = paper_info.get('categories') or []
                        if not any(cat in include_categories for cat in cats):
                            continue
                    all_papers.append(paper_info)
                    seen_papers.add(paper_id)
            
            print(f"成功获取 {len(all_papers)} 篇论文")
            for i, paper in enumerate(all_papers):
                print(f"{i+1}. {paper.get('title', 'N/A')}")
                
        except Exception as e:
            print(f"获取论文失败: {e}")
            return []

        print(f"总共获取 {len(all_papers)} 篇论文")

        # 不再依赖papers.jsonl，直接返回解析到的论文列表
        return all_papers
    
    def _extract_paper_info_from_html(self, dt_entry):
        """从HTML dt条目中提取论文信息"""
        try:
            # 获取对应的dd条目
            dd_entry = dt_entry.find_next_sibling('dd')
            if not dd_entry:
                print("Debug: 未找到对应的dd条目")
                return None
            
            # 提取arXiv ID和链接
            arxiv_link = dt_entry.find('a', href=lambda x: x and '/abs/' in x)
            if not arxiv_link:
                print("Debug: 未找到arXiv链接")
                return None
            
            href = arxiv_link.get('href', '')
            if href.startswith('/'):
                arxiv_id = href.split('/')[-1]
                paper_id = f"http://arxiv.org/abs/{arxiv_id}"
            else:
                arxiv_id = href.split('/')[-1]
                paper_id = href if href.startswith('http') else f"http://arxiv.org/abs/{arxiv_id}"
            
            # 检查是否有(replaced)标记
            replaced = False
            dt_text = dt_entry.get_text()
            if '(replaced)' in dt_text:
                replaced = True
            
            # 提取PDF链接
            pdf_link = "N/A"
            pdf_links = dt_entry.find_all('a', href=lambda x: x and '/pdf/' in x)
            if pdf_links:
                pdf_href = pdf_links[0].get('href', 'N/A')
                if pdf_href.startswith('/'):
                    pdf_link = f"https://arxiv.org{pdf_href}"
                else:
                    pdf_link = pdf_href
            
            # 提取标题
            title_elem = dd_entry.find('div', class_='list-title')
            title = "N/A"
            if title_elem:
                # 移除"Title:"描述符
                title_text = title_elem.get_text(strip=True)
                if title_text.startswith('Title:'):
                    title = title_text[6:].strip()
                else:
                    title = title_text
            
            # 提取作者
            authors = []
            authors_elem = dd_entry.find('div', class_='list-authors')
            if authors_elem:
                author_links = authors_elem.find_all('a')
                for author_link in author_links:
                    authors.append(author_link.get_text(strip=True))
            
            # 提取分类
            categories = []
            subjects_elem = dd_entry.find('div', class_='list-subjects')
            if subjects_elem:
                # 查找所有分类链接
                category_links = subjects_elem.find_all('a')
                for cat_link in category_links:
                    href = cat_link.get('href', '')
                    if 'searchtype=subject' in href:
                        # 从链接中提取分类代码
                        match = re.search(r'query=([^&]+)', href)
                        if match:
                            categories.append(match.group(1))
                # 如果没有找到分类链接，尝试从文本中提取
                if not categories:
                    text = subjects_elem.get_text()
                    # 匹配类似 "Machine Learning (cs.LG)" 的模式
                    matches = re.findall(r'\(([^)]+)\)', text)
                    categories = [match for match in matches if match.startswith('cs.')]
            
            # 提取摘要
            summary = "N/A"
            abstract_elem = dd_entry.find('p', class_='mathjax')
            if abstract_elem:
                summary = abstract_elem.get_text(strip=True)
            
            # 提取发布时间（从arXiv ID中推断）
            published = "N/A"
            updated = "N/A"
            if arxiv_id:
                # arXiv ID格式通常是 YYMM.NNNNN
                match = re.match(r'(\d{2})(\d{2})\.(\d+)', arxiv_id)
                if match:
                    year = "20" + match.group(1)  # 假设是20xx年
                    month = match.group(2)
                    published = f"{year}-{month}-01T00:00:00Z"
                    updated = published
            
            return {
                'id': paper_id,
                'title': title,
                'authors': authors,
                'summary': summary,
                'published': published,
                'updated': updated,
                'pdf_link': pdf_link,
                'categories': categories,
                'author_count': len(authors),
                'replaced': replaced
            }
            
        except Exception as e:
            print(f"提取论文信息时发生错误: {e}")
            return None
    
    def _extract_paper_info(self, entry, ns):
        """从XML条目中提取论文信息"""
        try:
            # 提取基本信息
            title_elem = entry.find('arxiv:title', ns)
            title = title_elem.text.strip() if title_elem is not None else "N/A"
            
            # 提取作者信息
            authors = []
            for author in entry.findall('arxiv:author', ns):
                name_elem = author.find('arxiv:name', ns)
                if name_elem is not None:
                    authors.append(name_elem.text.strip())
            
            # 提取摘要
            summary_elem = entry.find('arxiv:summary', ns)
            summary = summary_elem.text.strip() if summary_elem is not None else "N/A"
            
            # 提取时间信息
            published_elem = entry.find('arxiv:published', ns)
            published = published_elem.text.strip() if published_elem is not None else "N/A"
            
            updated_elem = entry.find('arxiv:updated', ns)
            updated = updated_elem.text.strip() if updated_elem is not None else "N/A"
            
            # 提取链接
            pdf_link = "N/A"
            for link in entry.findall('arxiv:link', ns):
                if link.get('title') == 'pdf':
                    pdf_link = link.get('href', "N/A")
                    break
            
            # 提取arXiv ID
            arxiv_id = entry.find('arxiv:id', ns)
            paper_id = arxiv_id.text.strip() if arxiv_id is not None else "N/A"
            
            # 提取分类
            categories = []
            for category in entry.findall('arxiv:category', ns):
                if category.get('term'):
                    categories.append(category.get('term'))
            
            return {
                'id': paper_id,
                'title': title,
                'authors': authors,
                'summary': summary,
                'published': published,
                'updated': updated,
                'pdf_link': pdf_link,
                'categories': categories,
                'author_count': len(authors),
                'replaced': False  # XML entries don't have replaced status
            }
            
        except Exception as e:
            print(f"提取论文信息时发生错误: {e}")
            return None

    def filter_by_updated_date(self, papers, date_str):
        """根据updated日期筛选论文"""
        filtered_papers = []
        for paper in papers:
            updated_field = paper.get('updated', '')
            try:
                dt = datetime.fromisoformat(updated_field.replace('Z', ''))
                if dt.strftime('%Y-%m-%d') == date_str:
                    filtered_papers.append(paper)
            except Exception:
                pass
        return filtered_papers

    # 日期段相关功能移除，不再支持
    # def filter_by_updated_date_range(self, papers, start_date, end_date):
    #     ...

    # ==================== PDF处理和LLM分析功能 ====================
    # ...无更改，省略...

    def download_pdf(self, pdf_url, filename):
        """下载PDF文件"""
        try:
            response = requests.get(pdf_url, timeout=30)
            response.raise_for_status()
            
            filepath = os.path.join(self.temp_dir, filename)
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            return filepath
        except Exception as e:
            print(f"下载PDF失败 {pdf_url}: {e}")
            return None

    def extract_first_image(self, pdf_path):
        try:
            import fitz
            doc = fitz.open(pdf_path)
            candidates = []
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                image_list = page.get_images(full=True)
                for img in image_list:
                    w = img[2] or 0
                    h = img[3] or 0
                    if w < 256 or h < 256:
                        continue
                    area = w * h
                    ar = (w / h) if h else 0
                    if ar < 0.4 or ar > 2.5:
                        continue
                    candidates.append((area, page_num, img))
            if not candidates:
                return None, None
            candidates.sort(key=lambda x: x[0], reverse=True)
            _, page_num, best_img = candidates[0]
            page = doc.load_page(page_num)
            xref = best_img[0]
            base = doc.extract_image(xref)
            b = base.get("image")
            ext = base.get("ext", "png")
            if b:
                return b, ext
            return None, None
        except Exception as e:
            print(f"提取图片失败: {e}")
            return None, None

    def render_first_page(self, pdf_path, max_width=640):
        """将PDF第一页渲染为位图，返回(png字节, 'png')"""
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(pdf_path)
            if len(doc) == 0:
                return None, None
            page = doc.load_page(0)
            width = page.rect.width or 1.0
            zoom = max_width / width
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat, alpha=False)
            return pix.tobytes("png"), "png"
        except Exception as e:
            print(f"将PDF第一页渲染为位图 渲染页面失败: {e}")
            return None, None

    def render_best_page(self, pdf_path, max_width=640):
        try:
            import fitz
            doc = fitz.open(pdf_path)
            if len(doc) == 0:
                return None, None
            best_total = -1
            best_index = 0
            for i in range(len(doc)):
                page = doc.load_page(i)
                imgs = page.get_images(full=True)
                total = 0
                for im in imgs:
                    total += (im[2] or 0) * (im[3] or 0)
                if total > best_total:
                    best_total = total
                    best_index = i
            page = doc.load_page(best_index)
            w = page.rect.width or 1.0
            z = max_width / w
            mat = fitz.Matrix(z, z)
            pix = page.get_pixmap(matrix=mat, alpha=False)
            return pix.tobytes("png"), "png"
        except Exception as e:
            print(f"渲染页面失败: {e}")
            return None, None

    def render_largest_image_region(self, pdf_path, max_width=640):
        try:
            import fitz
            doc = fitz.open(pdf_path)
            best = None
            for i in range(len(doc)):
                page = doc.load_page(i)
                images = page.get_images(full=True)
                for im in images:
                    xref = im[0]
                    rects = page.get_image_rects(xref)
                    for r in rects:
                        w = r.width
                        h = r.height
                        if w < 256 or h < 256:
                            continue
                        ar = w / h if h else 0
                        if ar < 0.4 or ar > 2.5:
                            continue
                        area = w * h
                        if best is None or area > best[0]:
                            best = (area, i, r)
            if not best:
                return None, None
            _, page_index, rect = best
            page = doc.load_page(page_index)
            w = rect.width or 1.0
            z = max_width / w
            mat = fitz.Matrix(z, z)
            pix = page.get_pixmap(matrix=mat, alpha=False, clip=rect)
            return pix.tobytes("png"), "png"
        except Exception as e:
            print(f"渲染区域失败: {e}")
            return None, None

    def render_figure_region_by_caption(self, pdf_path, figure_no=1, max_width=640):
        try:
            import fitz, re
            doc = fitz.open(pdf_path)
            patts = [fr"figure\s*{figure_no}\b", fr"fig\.\s*{figure_no}\b"]
            for i in range(len(doc)):
                page = doc.load_page(i)
                blocks = page.get_text("blocks") or []
                captions = []
                for b in blocks:
                    if not isinstance(b, (list, tuple)) or len(b) < 5:
                        continue
                    x0, y0, x1, y1, txt = b[0], b[1], b[2], b[3], b[4] if len(b) > 4 else ""
                    t = (txt or "").lower()
                    if any(re.search(p, t) for p in patts):
                        captions.append((x0, y0, x1, y1))
                if not captions:
                    continue
                images = page.get_images(full=True)
                candidates = []
                for im in images:
                    xref = im[0]
                    rects = page.get_image_rects(xref)
                    for r in rects:
                        w = r.width
                        h = r.height
                        if w < 256 or h < 256:
                            continue
                        ar = w / h if h else 0
                        if ar < 0.4 or ar > 2.5:
                            continue
                        for (cx0, cy0, cx1, cy1) in captions:
                            overlap_x = max(0, min(r.x1, cx1) - max(r.x0, cx0))
                            base_w = min((cx1 - cx0) or 1.0, (r.x1 - r.x0) or 1.0)
                            ratio = overlap_x / base_w
                            dy = min(abs(r.y0 - cy1), abs(cy0 - r.y1))
                            score = (ratio * 1000) - dy
                            candidates.append((score, i, r))
                if candidates:
                    candidates.sort(key=lambda x: x[0], reverse=True)
                    _, page_index, rect = candidates[0]
                    page2 = doc.load_page(page_index)
                    w = rect.width or 1.0
                    z = max_width / w
                    mat = fitz.Matrix(z, z)
                    pix = page2.get_pixmap(matrix=mat, alpha=False, clip=rect)
                    return pix.tobytes("png"), "png"
            return None, None
        except Exception as e:
            print(f"按标题渲染失败: {e}")
            return None, None

    def render_figure_union_region_by_caption(self, pdf_path, figure_no=1, max_width=640, search_height=500, padding=5):
        try:
            import fitz, re
            doc = fitz.open(pdf_path)
            patt = re.compile(rf"^(figure|fig\.?)[\s]*{figure_no}[:.]", re.I)
            for i in range(len(doc)):
                page = doc.load_page(i)
                blocks = page.get_text("blocks") or []
                blocks.sort(key=lambda b: b[1] if len(b) > 1 else 0)
                caption_rect = None
                for b in blocks:
                    if not isinstance(b, (list, tuple)) or len(b) < 5:
                        continue
                    txt = (b[4] or "").strip()
                    if patt.match(txt):
                        caption_rect = fitz.Rect(b[0], b[1], b[2], b[3])
                        break
                if not caption_rect:
                    continue
                search_bottom = caption_rect.y0
                search_top = max(0, search_bottom - float(search_height))
                rects = []
                try:
                    drawings = page.get_drawings() or []
                except Exception:
                    drawings = []
                for d in drawings:
                    r = d.get("rect")
                    if not r:
                        continue
                    if r.y1 <= search_bottom + 10 and r.y0 >= search_top:
                        if r.width > 5 or r.height > 5:
                            rects.append(fitz.Rect(r.x0, r.y0, r.x1, r.y1))
                images_added = False
                try:
                    infos = page.get_image_info() or []
                    for info in infos:
                        bb = info.get("bbox")
                        if not bb:
                            continue
                        r = fitz.Rect(bb)
                        if r.y1 <= search_bottom + 10 and r.y0 >= search_top:
                            rects.append(r)
                            images_added = True
                except Exception:
                    pass
                if not images_added:
                    images = page.get_images(full=True)
                    for im in images:
                        xref = im[0]
                        rlist = page.get_image_rects(xref)
                        for r in rlist:
                            if r.y1 <= search_bottom + 10 and r.y0 >= search_top:
                                rects.append(r)
                if not rects:
                    continue
                final_rect = rects[0]
                for r in rects[1:]:
                    final_rect |= r
                final_rect.x0 -= float(padding)
                final_rect.y0 -= float(padding)
                final_rect.x1 += float(padding)
                final_rect.y1 = search_bottom + 2.0
                final_rect = final_rect & page.rect
                w = final_rect.width or 1.0
                z = max_width / w
                mat = fitz.Matrix(z, z)
                pix = page.get_pixmap(matrix=mat, alpha=False, clip=final_rect)
                return pix.tobytes("png"), "png"
            return None, None
        except Exception as e:
            print(f"按标题联合渲染失败: {e}")
            return None, None

    def upload_to_r2(self, image_bytes, ext="webp"):
        """上传字节到Cloudflare R2，返回公共URL或None"""
        try:
            import boto3
            from botocore.config import Config
            import hashlib
            import os as _os

            endpoint = _os.environ.get("R2_ENDPOINT_URL")
            access_key = _os.environ.get("R2_ACCESS_KEY_ID")
            secret_key = _os.environ.get("R2_SECRET_ACCESS_KEY")
            bucket = _os.environ.get("R2_BUCKET")
            public_url = _os.environ.get("R2_PUBLIC_URL")

            if not all([endpoint, access_key, secret_key, bucket, public_url]):
                print("R2环境变量未配置完整，跳过上传")
                return None

            s3 = boto3.client(
                "s3",
                region_name="auto",
                endpoint_url=endpoint,
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                config=Config(signature_version="s3v4"),
            )

            hash_str = hashlib.sha256(image_bytes).hexdigest()
            key = f"thumbnails/{hash_str}_w640_q70.{ext}"
            content_type = f"image/{'jpeg' if ext == 'jpg' else ext}"

            s3.put_object(
                Bucket=bucket,
                Key=key,
                Body=image_bytes,
                ContentType=content_type,
                CacheControl="public, max-age=31536000, immutable",
            )

            return f"{public_url}/{key}"
        except Exception as e:
            print(f"上传R2失败: {e}")
            return None

    def convert_to_webp(self, image_bytes, max_width=640, quality=70):
        """将任意图片字节转换为WEBP指定宽度与质量，返回bytes"""
        try:
            from PIL import Image
            import io
            buf = io.BytesIO(image_bytes)
            img = Image.open(buf)
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            w, h = img.size
            if w > max_width:
                scale = max_width / float(w)
                img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
            out = io.BytesIO()
            img.save(out, format="WEBP", quality=quality, method=6)
            return out.getvalue(), "webp"
        except Exception as e:
            print(f"WEBP转换失败: {e}")
            return None, None

    def extract_first_page_text(self, pdf_path):
        """提取PDF第一页的文本内容"""
        if not PDF_AVAILABLE:
            return "PDF处理库未安装"
        
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                if len(pdf_reader.pages) > 0:
                    first_page = pdf_reader.pages[0]
                    text = first_page.extract_text()
                    return text[:4096]  # 限制长度避免API调用过长
                else:
                    return "PDF文件为空"
        except Exception as e:
            print(f"提取PDF文本失败 {pdf_path}: {e}")
            return f"PDF处理错误: {e}"

    def call_api_for_tags_institution_interest(self, title, abstract, first_page_text):
        prompt = f"""\
Role: You are an expert Computer Science researcher and paper reviewer.

Input Data:
Title: {title}
Abstract: {abstract}
First Page Content: {first_page_text}

Task: Please analyze the provided paper content and generate a structured analysis report following the strict rules below.

### Analysis Rules:

1. **Tag Assignment**:
    - **tag1 (Broad Category)**: Choose ONE from the following expanded list based on the primary domain:
        - "mlsys": Machine Learning Systems (intersection of AI and Systems, e.g., training infra, inference optimization).
        - "ai": General Artificial Intelligence (theory, pure ML algorithms, RL).
        - "cv": Computer Vision.
        - "nlp": Natural Language Processing.
        - "sys": Traditional Systems (OS, distributed systems, storage, networking without AI focus).
        - "sec": Security & Privacy.
        - "se": Software Engineering.
        - "db": Databases.
        - "hpc": High Performance Computing.
        - "other": If none of the above fit.
    
    - **tag2 (Specific Subfield)**:
        - If tag1 is **"mlsys"**, choose ONE from this expanded list:
            "llm training", "llm inference", "rag (retrieval-augmented generation)", "agent system", "multi-modal training", "multi-modal inference", "diffusion models", "post-training (sft/rlhf)", "model compression (quantization/pruning)", "compiler & ir", "memory & caching", "cluster infrastructure", "gpu kernels", "communication & networking", "fault-tolerance", "federated learning", "on-device ai", "others".
        - If tag1 is NOT "mlsys", assign a specific, standard academic sub-field (e.g., for "cv": "object detection"; for "nlp": "machine translation").

    - **tag3 (Keywords)**: Provide a comma-separated list of 3-5 specific technical keywords used in the paper (e.g., "FlashAttention, LoRA, Ring-AllReduce").

2. **Information Extraction**:
    - **Institution**: Infer the main research institution(s) from affiliations or email domains.
    - **Code**: Extract the GitHub or project page URL if explicitly mentioned. If not found, output "None".
    - **Contributions**: Summarize the paper's 3 key contributions (innovations) as a numbered list.

3. **Summarization**:
    - **Summary**: A concise 2-3 sentence summary in English describing the core problem, the proposed method, and the main conclusion.

4. **Visualization**:
    - **Mindmap**: Generate a Mermaid.js `graph LR` diagram code block based on the Abstract to visualize the paper's logic.
        - Layout: Left-to-Right tree structure (`graph LR`).
        - Language: Use **Bilingual (Chinese + English)** for all node text.
        - Structure: Root(Paper Title) --> Nodes for Problem(核心问题/Problem), Method(主要方法/Method), Results(关键结果/Results).
        - Keep node text very short and concise.

### Output Format:
(Strictly follow this format. Do not output markdown code blocks for the text parts, only for the mermaid part.)

tag1: <tag1>
tag2: <tag2>
tag3: <tag3, tag3, ...>
institution: <institution>
code: <code>
contributions: <contribution 1, contribution 2, ...>
summary: <2-3 sentences simple summary (method+conclusion)>
mermaid:
```mermaid
graph LR
<mermaid code here using Bilingual>
```
"""
        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant. You are good at summarizing papers and extracting keywords and institutions."},
                    {"role": "user", "content": prompt}
                ],
                stream=False
            )
            result = response.choices[0].message.content.strip()
            
            # 解析结果
            # 注意：不能直接 strip 每一行，因为 mermaid 需要保留缩进
            # 但我们需要过滤掉空行，除非是在 mermaid 块中
            raw_lines = result.splitlines()
            tag1, tag2, tag3, institution, code, contributions, llm_summary, mermaid = "", "", "", "", "", "", "", ""
            
            current_field = None
            mermaid_lines = []
            reading_mermaid = False
            
            for raw_line in raw_lines:
                # 去除两端空白用于判断 tag，但保留原始行用于 mermaid
                line = raw_line.strip()
                if not line and not reading_mermaid:
                    continue

                if line.lower().startswith("tag1:"):
                    tag1 = line.split(":", 1)[1].strip()
                    current_field = "tag1"
                elif line.lower().startswith("tag2:"):
                    tag2 = line.split(":", 1)[1].strip()
                    current_field = "tag2"
                elif line.lower().startswith("tag3:"):
                    tag3 = line.split(":", 1)[1].strip()
                    current_field = "tag3"
                elif line.lower().startswith("institution:"):
                    institution = line.split(":", 1)[1].strip()
                    current_field = "institution"
                elif line.lower().startswith("code:"):
                    code = line.split(":", 1)[1].strip()
                    current_field = "code"
                elif line.lower().startswith("contributions:"):
                    contributions = line.split(":", 1)[1].strip()
                    current_field = "contributions"
                elif line.lower().startswith("summary:") or line.lower().startswith("llm_summary:"):
                    llm_summary = line.split(":", 1)[1].strip()
                    current_field = "llm_summary"
                elif line.lower().startswith("mermaid:"):
                    current_field = "mermaid"
                elif line.startswith("```mermaid"):
                    reading_mermaid = True
                    current_field = "mermaid_block"
                elif line.startswith("```") and reading_mermaid:
                    reading_mermaid = False
                    current_field = None
                else:
                    # 处理多行内容
                    if reading_mermaid:
                        # 对于 mermaid，使用原始行（保留缩进）
                        mermaid_lines.append(raw_line)
                    elif current_field == "contributions":
                        contributions += " " + line
                    elif current_field == "llm_summary":
                        llm_summary += " " + line
            
            if mermaid_lines:
                mermaid = '\n'.join(mermaid_lines)
            
            tag3_list = [t.strip() for t in tag3.split(',') if t.strip()]
            return tag1, tag2, tag3_list, institution, code, contributions, llm_summary, mermaid

        except Exception as e:
            print(f"API调用失败: {e}")
            return "", "", [], "", "", "", "", ""

    def process_single_paper(self, paper):
        categories = paper.get('categories', []) or []
        title = paper.get('title', '')

        summary = paper.get('summary', '')
        pdf_link = paper.get('pdf_link', '')
        print(f"处理论文: {title}")
        
        # 下载PDF
        if not pdf_link or pdf_link == 'N/A':
            print(f"跳过论文 {title}: 无PDF链接")
            paper['is_interested'] = True
            return paper
        
        # 生成PDF文件名
        pdf_filename = f"{paper.get('id', '').split('/')[-1]}.pdf"
        
        # 下载PDF
        pdf_path = self.download_pdf(pdf_link, pdf_filename)
        if not pdf_path:
            print(f"跳过论文 {title}: PDF下载失败")
            paper['is_interested'] = True
            return paper
        
        # 提取第一页文本
        first_page_text = self.extract_first_page_text(pdf_path)

        # 调用API获取标签、机构，并获取LLM总结（可禁用以节省token）
        if self.enable_llm:
            tag1, tag2, tag3_list, institution, code, contributions, llm_summary, mermaid = self.call_api_for_tags_institution_interest(
                title, summary, first_page_text
            )
        else:
            tag1, tag2, tag3_list, institution, code, contributions, llm_summary, mermaid = "", "", [], "TBD", "", "", title, ""
        
        # 生成缩略图（可选）
        thumbnail_url = None
        try:
            if self.enable_thumbnails and pdf_path:
                # img_bytes, ext = self.extract_first_image(pdf_path)
                # if not img_bytes:
                img_bytes, ext = self.render_figure_union_region_by_caption(pdf_path, figure_no=1)
                if not img_bytes:
                    img_bytes, ext = self.render_figure_region_by_caption(pdf_path, figure_no=1)
                if not img_bytes:
                    img_bytes, ext = self.render_largest_image_region(pdf_path)
                if not img_bytes:
                    img_bytes, ext = self.render_best_page(pdf_path)
                if img_bytes:
                    if (ext or "").lower() != "webp":
                        converted, cext = self.convert_to_webp(img_bytes)
                        if converted:
                            img_bytes, ext = converted, cext
                    thumbnail_url = self.upload_to_r2(img_bytes, ext or "webp")
        except Exception as _e:
            print(f"生成缩略图失败: {_e}")

        # 更新论文信息
        paper['tag1'] = tag1
        paper['tag2'] = tag2
        paper['tag3'] = ', '.join(tag3_list)
        paper['institution'] = institution
        paper['code'] = code
        paper['contributions'] = contributions
        # 所有 cs.DC 都输出
        paper['is_interested'] = True
        paper['llm_summary'] = llm_summary
        paper['mermaid'] = mermaid
        paper['simple_only'] = False
        if thumbnail_url:
            paper['thumbnail'] = thumbnail_url
        
        # 清理临时PDF文件
        try:
            os.remove(pdf_path)
        except:
            pass
        
        print(f"完成论文 {title}: tag1={tag1}, tag2={tag2}, institution={institution}")
        return paper
    
    # ==================== Markdown文件处理功能 ====================
    # ...实现不变，省略...
    def get_week_range(self, date_str):
        """根据日期获取该周的周一到周日的日期范围"""
        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d')
            days_since_monday = target_date.weekday()
            monday = target_date - timedelta(days=days_since_monday)
            sunday = monday + timedelta(days=6)
            
            start_str = monday.strftime('%Y%m%d')
            end_str = sunday.strftime('%Y%m%d')
            
            return f"{start_str}-{end_str}"
        except ValueError as e:
            print(f"日期格式错误: {e}")
            return None
    
    def get_arxiv_prefix(self, date_str):
        """根据日期获取类似[arXiv251027]的字符串"""
        try:
            dt = datetime.strptime(date_str, '%Y-%m-%d')
            prefix = f"[arXiv{str(dt.year)[-2:]}{dt.month:02d}{dt.day:02d}]"
            return prefix
        except Exception:
            return ""

    def clean_latex_in_title(self, title):
        """
        清理标题中的 LaTeX 语法，转换为 Markdown 格式
        彻底规避 MDX 解析错误，将所有 LaTeX 命令转换为安全的 Markdown/HTML
        
        Args:
            title (str): 原始标题
            
        Returns:
            str: 清理后的标题
        """
        if not title:
            return title
        
        # 常见的 LaTeX 命令转换
        # \textit{...} -> *...* (斜体)
        title = re.sub(r'\\textit\{([^}]+)\}', r'*\1*', title)
        # \textbf{...} -> **...** (粗体)
        title = re.sub(r'\\textbf\{([^}]+)\}', r'**\1**', title)
        # \texttt{...} -> `...` (等宽字体)
        title = re.sub(r'\\texttt\{([^}]+)\}', r'`\1`', title)
        # \emph{...} -> *...* (强调/斜体)
        title = re.sub(r'\\emph\{([^}]+)\}', r'*\1*', title)
        # \text{...} -> ... (普通文本，直接移除命令)
        title = re.sub(r'\\text\{([^}]+)\}', r'\1', title)
        # \textsc{...} -> ... (小型大写，Markdown 不支持，直接移除命令)
        title = re.sub(r'\\textsc\{([^}]+)\}', r'\1', title)
        # \underline{...} -> <u>...</u> (下划线，转换为 HTML)
        title = re.sub(r'\\underline\{([^}]+)\}', r'<u>\1</u>', title)
        # \uline{...} -> <u>...</u> (ulem 包的下划线命令，转换为 HTML)
        title = re.sub(r'\\uline\{([^}]+)\}', r'<u>\1</u>', title)
        # \uuline{...} -> <u>...</u> (ulem 包的双下划线，转换为 HTML)
        title = re.sub(r'\\uuline\{([^}]+)\}', r'<u>\1</u>', title)
        # \uwave{...} -> <u>...</u> (ulem 包的波浪下划线，转换为 HTML)
        title = re.sub(r'\\uwave\{([^}]+)\}', r'<u>\1</u>', title)
        # \sout{...} -> ~~...~~ (ulem 包的删除线，转换为 Markdown)
        title = re.sub(r'\\sout\{([^}]+)\}', r'~~\1~~', title)
        
        # 通用清理：处理所有其他 LaTeX 命令 \command{...}，移除命令保留内容
        # 这样可以避免任何未处理的 LaTeX 命令被 MDX 误解析为 JavaScript
        # 注意：这个通用清理应该在所有特定命令处理之后执行
        # 匹配模式：反斜杠 + 字母命令名 + 大括号参数
        def remove_latex_command(match):
            # group(1) 是命令名，group(2) 是内容，返回内容
            return match.group(2) if match.lastindex >= 2 else ''
        
        # 处理 \command{content} 格式的命令（移除命令，保留内容）
        # 这个正则会匹配所有剩余的 \command{...} 格式
        title = re.sub(r'\\([a-zA-Z]+)\{([^}]+)\}', remove_latex_command, title)
        
        # 处理 \command 格式的命令（无参数，直接移除）
        # 这些命令通常需要完全移除
        title = re.sub(r'\\([a-zA-Z]+)(?![a-zA-Z{])', '', title)
        
        return title

    def escape_mdx(self, text):
        """
        转义 MDX 特殊字符
        主要是 { 和 }，因为它们在 MDX 中被视为 JavaScript 表达式的开始和结束
        """
        if not text:
            return text
        # 避免重复转义：如果已经是 \{ 或 \} 则不处理
        # 这里简单处理，直接替换所有未转义的
        # 使用正则 lookbehind 可能会更准确，但简单的 replace 通常足够，
        # 除非原文真的包含 \{ 且不想被再次转义。
        # 考虑到 LaTeX 清理后应该没有 \{ 了，直接 replace 即可。
        return text.replace('{', '\\{').replace('}', '\\}')

    def format_paper_with_enhanced_info(self, paper, date_str=None):
        # 非 cs.DC 使用简化格式：- [arXivYYMMDD] title [link](https://...)
        categories = paper.get('categories', []) or []
        title = paper.get('title', 'N/A')
        # 清理标题中的 LaTeX 语法
        title = self.clean_latex_in_title(title)
        # 转义 MDX 特殊字符
        title = self.escape_mdx(title)
        
        arxiv_prefix = ""
        if date_str is not None:
            arxiv_prefix = self.get_arxiv_prefix(date_str)
        else:
            arxiv_prefix = ""
        # 使用详细格式
        authors = ', '.join(paper.get('authors', []))
        authors = self.escape_mdx(authors)
        
        pdf_link = paper.get('pdf_link', 'N/A')
        
        tags = []
        if paper.get('tag1'):
            tags.append("[" + self.escape_mdx(paper['tag1']) + "]")
        if paper.get('tag2'):
            tags.append("[" + self.escape_mdx(paper['tag2']) + "]")
        if paper.get('tag3'):
            tag3_items = [t.strip() for t in paper['tag3'].split(',') if t.strip()]
            if tag3_items:
                tags.append('[' + ', '.join([self.escape_mdx(t) for t in tag3_items]) + ']')
        tags_str = ', '.join(tags) if tags else 'TBD'
        
        institution = paper.get('institution', 'TBD')
        institution = self.escape_mdx(institution)
        
        code = paper.get('code', 'None')
        if code and code.lower() != 'none':
            code = self.escape_mdx(code)
            
        contributions = paper.get('contributions', '')
        if contributions:
            contributions = self.escape_mdx(contributions)
            
        mermaid = paper.get('mermaid', '')
        # Mermaid 不需要转义 MDX，因为它在代码块中，但我们要确保它放在 ```mermaid 块里
        # 如果 API 返回的 mermaid 已经包含了 ```mermaid，则不需要额外添加，否则添加
        # 这里的 mermaid 是纯代码，没有 ``` 包裹
        
        llm_summary = paper.get('llm_summary', '').strip()
        
        formatted_text = f"""- **{arxiv_prefix} {title}**
  - **tags:** {tags_str}
  - **authors:** {authors}
  - **institution:** {institution}
  - **link:** {pdf_link}
"""
        if code and code.lower() != 'none':
            formatted_text += f"  - **code:** {code}\n"
            
        if contributions:
            formatted_text += f"  - **contributions:** {contributions}\n"
            
        thumb = paper.get('thumbnail')
        if thumb:
            formatted_text += f"  - **thumbnail:** {thumb}\n"
        if llm_summary:
            # 转义MDX特殊字符：大括号{}会被MDX解析为JSX表达式，需要转义
            # 这里也处理 < >
            escaped_summary = llm_summary.replace('<', '&lt;').replace('>', '&gt;').replace('{', '\\{').replace('}', '\\}')
            formatted_text += f"  - **Simple LLM Summary:** {escaped_summary}\n"
            
        if mermaid:
            # 为 mermaid 增加缩进，使其属于当前 list item
            mermaid_block = "  - **Mindmap:**\n\n"
            mermaid_lines = mermaid.split('\n')
            indented_mermaid = '\n'.join(['    ' + line for line in mermaid_lines])
            mermaid_block += f"    ```mermaid\n{indented_mermaid}\n    ```\n"
            formatted_text += mermaid_block
            
        formatted_text += "\n"
        return formatted_text

    def update_markdown_file(self, filepath, papers, date_str):
        # ...实现不变...
        if not papers:
            print("没有论文需要添加")
            return

        # 不再根据兴趣过滤，全部输出
        all_papers = papers

        existing_content = ""
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                existing_content = f.read()

        # 利用正则找到所有日期section
        date_section_pattern = re.compile(
            r"(^|\n)##\s*(\d{4}-\d{2}-\d{2}).*?(?=\n##\s|\Z)", re.DOTALL
        )
        all_sections = []
        for m in date_section_pattern.finditer(existing_content):
            section_start = m.start()
            section_content = m.group(0).lstrip('\n')
            section_date = m.group(2)
            all_sections.append((section_date, section_content, section_start))
        
        # 新section内容
        papers_content = f"## {date_str}\n\n"
        if all_papers:
            # 先输出 cs.DC，再输出其他，保持各自相对顺序，并在每类开头输出总数
            csdc_papers = [p for p in all_papers if any(cat == 'cs.DC' for cat in (p.get('categories', []) or []))]
            other_papers = [p for p in all_papers if not any(cat == 'cs.DC' for cat in (p.get('categories', []) or []))]
            # 统计 cs.AI/cs.LG 两组关键词
            rl_papers = [p for p in other_papers if p.get('rl_match')]
            accelerat_papers = [p for p in other_papers if p.get('accelerat_match')]

            papers_content += f"**cs.DC total: {len(csdc_papers)}**\n\n"
            for paper in csdc_papers:
                papers_content += self.format_paper_with_enhanced_info(paper, date_str=date_str)

            papers_content += f"\n**cs.AI/cs.LG contains \"reinforcement learning\" total: {len(rl_papers)}**\n"
            for paper in rl_papers:
                papers_content += self.format_paper_with_enhanced_info(paper, date_str=date_str)

            papers_content += f"\n**cs.AI/cs.LG contains \"accelerate\" total: {len(accelerat_papers)}**\n"
            for paper in accelerat_papers:
                papers_content += self.format_paper_with_enhanced_info(paper, date_str=date_str)
        else:
            papers_content += "No papers today\n"

        replaced = False
        # 如有则替换当前日期section
        for idx, (dt, _, start_idx) in enumerate(all_sections):
            if dt == date_str:
                # 替换
                before = existing_content[:start_idx].rstrip('\n')
                after_idx = start_idx + len(_)
                after = existing_content[after_idx:]
                new_content = before
                if new_content and not new_content.endswith('\n'):
                    new_content += "\n"
                new_content += "\n" + papers_content
                if after and not after.startswith('\n'):
                    new_content += "\n"
                new_content += after.lstrip('\n')
                replaced = True
                print(f"日期 {date_str} 的内容已存在，已覆盖")
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content.strip() + '\n')
                print(f"已将 {len(all_papers)} 篇论文添加到文件: {filepath}")
                return

        # 如果没有，插入保持时间递增顺序（从小到大）
        # 找到插入点：第一个section日期大于本date_str，则插入在它前面；若找不到，追加到文件末尾
        insert_idx = None
        for idx, (dt, _, start_idx) in enumerate(all_sections):
            if dt > date_str:
                insert_idx = start_idx
                break
        if insert_idx is not None:
            # 插入到insert_idx前
            before = existing_content[:insert_idx].rstrip('\n')
            after = existing_content[insert_idx:]
            new_content = before
            if new_content and not new_content.endswith('\n'):
                new_content += "\n"
            new_content += "\n" + papers_content
            if after and not after.startswith('\n'):
                new_content += "\n"
            new_content += after.lstrip('\n')
            print(f"日期 {date_str} 的内容不存在，已按时间顺序插入")
        else:
            # 追加到最后
            new_content = existing_content.rstrip() + "\n\n" + papers_content
            print(f"日期 {date_str} 的内容不存在，已追加到最后")
        
        # 写回文件
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content.strip() + '\n')

        print(f"已将 {len(all_papers)} 篇论文添加到文件: {filepath}")

    def find_or_create_weekly_file(self, date_str):
        """根据日期找到或创建对应的周文件"""
        week_range = self.get_week_range(date_str)
        if not week_range:
            return None
        
        filename = f"{week_range}.md"
        filepath = os.path.join(self.docs_daily_path, filename)
        
        if not os.path.exists(filepath):
            self.create_weekly_file(filepath, week_range)
        
        return filepath

    def create_weekly_file(self, filepath, week_range):
        """创建新的周文件"""
        start_date_str, end_date_str = week_range.split('-')
        start_date = datetime.strptime(start_date_str, '%Y%m%d')
        end_date = datetime.strptime(end_date_str, '%Y%m%d')
        
        content = f"""# {week_range}

"""
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"创建新的周文件: {filepath}")

    def _safe_category(self, cat):
        return (cat or 'unknown').replace('.', '_').replace('/', '_').replace(' ', '_')

    def _norm_category(self, cat):
        """将类别规范化为小写且仅含字母数字（用于URL短slug）"""
        s = (cat or '').lower()
        return re.sub(r'[^a-z0-9]', '', s)

    def find_or_create_weekly_file_for_category(self, date_str, category):
        week_range = self.get_week_range(date_str)
        if not week_range:
            return None
        safe = self._safe_category(category)
        dir_path = os.path.join(self.docs_daily_path, safe)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        self.ensure_category_index_file(category)
        filepath = os.path.join(dir_path, f"{week_range}.md")
        if not os.path.exists(filepath):
            self.create_weekly_file_for_category(filepath, week_range, category)
        return filepath

    def create_weekly_file_for_category(self, filepath, week_range, category):
        norm = self._norm_category(category)
        frontmatter = f"---\nslug: /daily/{norm}/{week_range}\n---\n"
        content = f"# {week_range} ({category})\n\n"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(frontmatter + content)
        print(f"创建新的类别周文件: {filepath}")

    def ensure_category_index_file(self, category):
        safe = self._safe_category(category)
        dir_path = os.path.join(self.docs_daily_path, safe)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        meta_path = os.path.join(dir_path, "_category_.json")
        if not os.path.exists(meta_path):
            norm = self._norm_category(category)
            payload = {
                "label": category,
                "position": 1,
                "link": {"type": "generated-index", "slug": f"/daily/{norm}"}
            }
            with open(meta_path, 'w', encoding='utf-8') as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
            print(f"创建类别索引文件: {meta_path}")

    def ensure_category_indices(self):
        for entry in os.listdir(self.docs_daily_path):
            full = os.path.join(self.docs_daily_path, entry)
            if os.path.isdir(full):
                meta_path = os.path.join(full, "_category_.json")
                if not os.path.exists(meta_path):
                    label = entry.replace('_', '.')
                    norm = self._norm_category(label)
                    payload = {
                        "label": label,
                        "position": 2,
                        "collapsible": True,
                        "link": {"type": "generated-index", "slug": f"/daily/{norm}"}
                    }
                    with open(meta_path, 'w', encoding='utf-8') as f:
                        json.dump(payload, f, ensure_ascii=False, indent=2)
                    print(f"创建缺失的类别索引文件: {meta_path}")

    def update_markdown_file_for_category(self, filepath, papers, date_str, category):
        if not papers:
            return
        existing_content = ""
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                existing_content = f.read()
        date_section_pattern = re.compile(r"(^|\n)##\s*(\d{4}-\d{2}-\d{2}).*?(?=\n##\s|\Z)", re.DOTALL)
        all_sections = []
        for m in date_section_pattern.finditer(existing_content):
            section_start = m.start()
            section_content = m.group(0).lstrip('\n')
            section_date = m.group(2)
            all_sections.append((section_date, section_content, section_start))
        papers_content = f"## {date_str}\n\n"
        for paper in papers:
            papers_content += self.format_paper_with_enhanced_info(paper, date_str=date_str)
        replaced = False
        for idx, (dt, _, start_idx) in enumerate(all_sections):
            if dt == date_str:
                before = existing_content[:start_idx].rstrip('\n')
                after_idx = start_idx + len(_)
                after = existing_content[after_idx:]
                new_content = before
                if new_content and not new_content.endswith('\n'):
                    new_content += "\n"
                new_content += "\n" + papers_content
                if after and not after.startswith('\n'):
                    new_content += "\n"
                new_content += after.lstrip('\n')
                replaced = True
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content.strip() + '\n')
                return
        insert_idx = None
        for idx, (dt, _, start_idx) in enumerate(all_sections):
            if dt > date_str:
                insert_idx = start_idx
                break
        if insert_idx is not None:
            before = existing_content[:insert_idx].rstrip('\n')
            after = existing_content[insert_idx:]
            new_content = before
            if new_content and not new_content.endswith('\n'):
                new_content += "\n"
            new_content += "\n" + papers_content
            if after and not after.startswith('\n'):
                new_content += "\n"
            new_content += after.lstrip('\n')
        else:
            new_content = existing_content.rstrip() + "\n\n" + papers_content
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content.strip() + '\n')

    # ==================== 主处理流程 ====================
    
    def process_papers_by_date(self, target_date=None, categories=['cs.DC', 'cs.AI'], max_workers=2, max_papers=10, html_content=None, include_categories=None):
        """
        根据指定日期处理论文的完整流程

        Args:
            target_date (str): 目标日期，格式为 'YYYY-MM-DD'
            categories (list): 论文分类列表
            max_workers (int): 并发处理数量
            max_papers (int): 最大处理论文数量（用于测试）
            html_content (bytes): HTML内容，如果提供则直接使用
        """
        # 若未提供日期，则默认使用今天
        if not target_date:
            target_date = datetime.now().strftime('%Y-%m-%d')

        # ==== 新增: arxiv_date.txt 检查 ====
        today_ymd = target_date
        if already_processed(today_ymd):
            print(f"日期 {today_ymd} 已经处理过，自动退出。")
            return

        print(f"开始处理日期: {target_date}")

        single_date = target_date
        print(f"\n==== 处理 {single_date} ====")
        # 1. 从arXiv获取论文
        print("步骤1: 从arXiv获取论文...")
        papers = self.fetch_arxiv_papers(categories=categories, max_results=1024, target_date=single_date, html_content=html_content, include_categories=include_categories)

        if not papers:
            print(f"日期 {single_date} 没有找到论文")
            append_to_processed(single_date)
            return

        # 限制处理数量（用于测试）
        if max_papers and len(papers) > max_papers:
            papers = papers[:max_papers]
            print(f"限制处理前 {max_papers} 篇论文")

        print(f"找到 {len(papers)} 篇论文，开始处理...")

        # 2. 并发处理论文（下载PDF、调用LLM）
        print("步骤2: 处理论文（下载PDF、调用LLM）...")
        processed_papers = []

        for i, paper in enumerate(papers):
            print(f"{i+1}. {paper.get('title', 'N/A')}")

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有任务
            future_to_paper = {
                executor.submit(self.process_single_paper, paper): paper 
                for paper in papers
            }

            # 收集结果
            for future in tqdm(concurrent.futures.as_completed(future_to_paper), 
                             total=len(future_to_paper), desc="处理论文"):
                try:
                    processed_paper = future.result()
                    processed_papers.append(processed_paper)
                except Exception as e:
                    print(f"处理论文时出错: {e}")

        # 3. 统计结果
        print(f"处理完成！总共 {len(processed_papers)} 篇论文")

        # 4. 更新markdown文件
        print("步骤3: 更新markdown文件...")
        weekly_file = self.find_or_create_weekly_file(single_date)
        if weekly_file:
            self.update_markdown_file(weekly_file, processed_papers, single_date)
            print(f"处理完成！论文已添加到: {weekly_file}")
        else:
            print("无法创建或找到周文件")

        category_map = {}
        for p in processed_papers:
            for cat in (p.get('categories') or []):
                category_map.setdefault(cat, []).append(p)
        for cat, cat_papers in category_map.items():
            cat_weekly_file = self.find_or_create_weekly_file_for_category(single_date, cat)
            if cat_weekly_file:
                self.update_markdown_file_for_category(cat_weekly_file, cat_papers, single_date, cat)
                print(f"类别 {cat} 的论文已添加到: {cat_weekly_file}")
        
        # 完成后写入arxiv_date.txt
        append_to_processed(single_date)

def main():
    """
    主函数 - 使用示例
    """
    if not PDF_AVAILABLE:
        print("请先安装PyPDF2: pip install PyPDF2")
        return
    
    # 解析命令行参数（测试用途）
    parser = argparse.ArgumentParser(description="Process arXiv cs/new papers")
    parser.add_argument("--include-categories", type=str, default=None, help="仅处理指定类别，逗号分隔，例如: cs.AI,cs.LG")
    parser.add_argument("--max-papers", type=int, default=None, help="限制最大论文数量用于测试")
    parser.add_argument("--max-workers", type=int, default=10, help="并发线程数")
    parser.add_argument("--generate-thumbnails", action="store_true", help="启用PDF缩略图生成并上传到R2")
    parser.add_argument("--skip-llm", action="store_true", help="跳过LLM总结，直接使用title作为总结")
    args = parser.parse_args()

    # 检查API密钥（在启用LLM时）
    if not args.skip_llm and not os.environ.get('DEEPSEEK_API_KEY'):
        print("请设置DEEPSEEK_API_KEY环境变量，或使用 --skip-llm")
        return
    
    # 从arXiv HTML页面下载HTML内容（只下载一次）
    arxiv_url = "https://arxiv.org/list/cs/new"
    print(f"正在从 {arxiv_url} 下载HTML内容...")
    try:
        response = requests.get(arxiv_url, timeout=30)
        response.raise_for_status()
        html_content = response.content
        print("HTML内容下载成功")
    except Exception as e:
        print(f"下载HTML内容失败: {e}")
        html_content = None
    
    # 从HTML内容中提取日期
    if html_content:
        target_date = extract_date_from_html(html_content=html_content)
    else:
        target_date = None
    
    # 如果从HTML页面提取失败，使用当前日期
    if not target_date:
        print("无法从HTML页面提取日期，使用当前日期")
        target_date = datetime.now().strftime('%Y-%m-%d')
    else:
        print(f"使用从HTML页面提取的日期: {target_date}")

    # ==== 运行前检查日期是否已处理 ====
    if already_processed(target_date):
        print(f"日期 {target_date} 已经处理过，自动退出。")
        return

    include_categories = None
    if args.include_categories:
        include_categories = [s.strip() for s in args.include_categories.split(',') if s.strip()]

    max_papers = args.max_papers
    max_workers = args.max_workers

    # 创建处理器并处理论文
    processor = CompletePaperProcessor(enable_thumbnails=args.generate_thumbnails, enable_llm=(not args.skip_llm))
    processor.process_papers_by_date(
        target_date=target_date,
        max_workers=max_workers,
        max_papers=max_papers,
        html_content=html_content,
        include_categories=include_categories
    )

if __name__ == "__main__":
    main()
