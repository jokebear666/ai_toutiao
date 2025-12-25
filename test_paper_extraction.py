import unittest
from unittest.mock import MagicMock, patch
import os
import sys
import argparse
import requests
import xml.etree.ElementTree as ET

# 添加当前目录到 path 以便导入模块
sys.path.append(os.getcwd())

# 尝试导入
try:
    from get_daily_arxiv_paper import CompletePaperProcessor
except ImportError as e:
    print(f"Import failed: {e}")
    sys.modules['PyPDF2'] = MagicMock()
    from get_daily_arxiv_paper import CompletePaperProcessor

def get_paper_info_from_arxiv(arxiv_id):
    """
    使用 arXiv API 获取论文元数据
    """
    url = f"http://export.arxiv.org/api/query?id_list={arxiv_id}"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch metadata from arXiv: {response.status_code}")
        return None
    
    root = ET.fromstring(response.content)
    # namespace
    ns = {'atom': 'http://www.w3.org/2005/Atom', 'arxiv': 'http://arxiv.org/schemas/atom'}
    
    entry = root.find('atom:entry', ns)
    if entry is None:
        print("No entry found for this arXiv ID.")
        return None
        
    title = entry.find('atom:title', ns).text.strip()
    summary = entry.find('atom:summary', ns).text.strip()
    
    # 获取 PDF 链接
    pdf_link = ""
    for link in entry.findall('atom:link', ns):
        if link.get('title') == 'pdf':
            pdf_link = link.get('href')
            
    # 如果没有显式的 pdf link，尝试构造
    if not pdf_link:
        pdf_link = f"http://arxiv.org/pdf/{arxiv_id}.pdf"
        
    return {
        'id': f"http://arxiv.org/abs/{arxiv_id}",
        'title': title,
        'summary': summary,
        'pdf_link': pdf_link,
        'authors': [a.find('atom:name', ns).text for a in entry.findall('atom:author', ns)],
        'categories': [] # 简化处理
    }

def run_real_extraction(arxiv_id):
    """
    运行真实的论文提取流程
    """
    print(f"Fetching metadata for arXiv ID: {arxiv_id}...")
    paper_info = get_paper_info_from_arxiv(arxiv_id)
    if not paper_info:
        return
        
    print(f"Title: {paper_info['title']}")
    print(f"PDF Link: {paper_info['pdf_link']}")
    
    # 实例化 Processor
    # 注意：需要环境变量 DEEPSEEK_API_KEY
    if not os.environ.get("DEEPSEEK_API_KEY"):
        print("Error: DEEPSEEK_API_KEY environment variable is not set.")
        return

    processor = CompletePaperProcessor(docs_daily_path="temp_docs", temp_dir="temp_pdfs", enable_thumbnails=False, enable_llm=True)
    
    # 复用 process_single_paper 的逻辑，但这里我们想直接看 call_api 的结果
    # 或者直接调用 process_single_paper 并打印结果
    
    # 下载 PDF
    pdf_filename = f"{arxiv_id}.pdf"
    print(f"Downloading PDF to {os.path.join(processor.temp_dir, pdf_filename)}...")
    pdf_path = processor.download_pdf(paper_info['pdf_link'], pdf_filename)
    
    if not pdf_path:
        print("Failed to download PDF.")
        return
        
    print("Extracting text from first page...")
    first_page_text = processor.extract_first_page_text(pdf_path)
    # print(f"First page text preview: {first_page_text[:200]}...")
    
    print("Calling LLM API for extraction...")
    result = processor.call_api_for_tags_institution_interest(
        paper_info['title'],
        paper_info['summary'],
        first_page_text
    )
    
    tag1, tag2, tag3_list, institution, code, contributions, llm_summary, mermaid = result
    
    print("\n" + "="*50)
    print("EXTRACTION RESULTS")
    print("="*50)
    print(f"Tag1: {tag1}")
    print(f"Tag2: {tag2}")
    print(f"Tag3: {', '.join(tag3_list)}")
    print(f"Institution: {institution}")
    print(f"Code: {code}")
    print(f"Contributions: {contributions}")
    print(f"LLM Summary: {llm_summary}")
    print("-" * 20)
    print("Mermaid Code:")
    print(mermaid)
    print("="*50)
    
    # 清理 PDF
    try:
        os.remove(pdf_path)
        print("Cleaned up PDF file.")
    except:
        pass

class TestPaperExtraction(unittest.TestCase):
    def setUp(self):
        # 实例化处理器，禁用 thumbnails，启用 LLM
        # 使用 patch.dict 确保环境变量设置
        with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "fake_key"}):
            # 这里可能会因为文件系统操作（创建目录）而产生副作用，但 CompletePaperProcessor 构造函数里有 ensure_directories
            # 我们可以 mock os.makedirs 来避免副作用，或者允许它创建临时目录
            with patch('os.makedirs'): 
                self.processor = CompletePaperProcessor(docs_daily_path="test_docs", temp_dir="test_temp", enable_thumbnails=False, enable_llm=True)
            
        # Mock OpenAI client
        self.processor.client = MagicMock()

    def test_call_api_for_tags_institution_interest(self):
        print("\nTesting full extraction...")
        # 准备模拟的 LLM 返回内容
        mock_response_content = """
tag1: mlsys
tag2: llm training
tag3: LoRA, quantization, distributed training
institution: UC Berkeley
code: https://github.com/example/project
contributions: 1. Proposed Method A. 2. Achieved SOTA. 3. Open sourced code.
summary: This paper proposes Method A for efficient LLM training. It achieves SOTA results.
mermaid:
```mermaid
graph LR
  A((标题/Title)) --> B(问题/Problem)
  B --> B1(训练慢/Slow training)
  A --> C(方法/Method)
  C --> C1(方法A/Method A)
  A --> D(结果/Results)
  D --> D1(SOTA)
```
"""
        # 设置 Mock 返回
        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock(message=MagicMock(content=mock_response_content))]
        self.processor.client.chat.completions.create.return_value = mock_completion

        # 调用被测方法
        title = "Test Paper"
        abstract = "This is a test abstract."
        first_page_text = "Test first page content."
        
        result = self.processor.call_api_for_tags_institution_interest(title, abstract, first_page_text)
        
        # 解包结果
        tag1, tag2, tag3_list, institution, code, contributions, llm_summary, mermaid = result

        # 验证结果
        print(f"Tag1: {tag1}")
        self.assertEqual(tag1, "mlsys")
        
        print(f"Tag2: {tag2}")
        self.assertEqual(tag2, "llm training")
        
        print(f"Tag3 List: {tag3_list}")
        self.assertEqual(tag3_list, ["LoRA", "quantization", "distributed training"])
        
        print(f"Institution: {institution}")
        self.assertEqual(institution, "UC Berkeley")
        
        print(f"Code: {code}")
        self.assertEqual(code, "https://github.com/example/project")
        
        print(f"Contributions: {contributions}")
        self.assertIn("1. Proposed Method A", contributions)
        
        print(f"LLM Summary: {llm_summary}")
        self.assertEqual(llm_summary, "This paper proposes Method A for efficient LLM training. It achieves SOTA results.")
        
        # 验证 Mermaid 提取
        expected_mermaid = """graph LR
  A((标题/Title)) --> B(问题/Problem)
  B --> B1(训练慢/Slow training)
  A --> C(方法/Method)
  C --> C1(方法A/Method A)
  A --> D(结果/Results)
  D --> D1(SOTA)"""
        print(f"Mermaid:\n{mermaid}")
        self.assertEqual(mermaid.strip(), expected_mermaid.strip())

    def test_call_api_with_missing_fields(self):
        print("\nTesting extraction with missing fields...")
        # 测试缺少某些字段的情况
        mock_response_content = """
tag1: ai
tag2: cv
tag3: object detection
institution: Stanford
summary: Summary text.
"""
        # 设置 Mock 返回
        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock(message=MagicMock(content=mock_response_content))]
        self.processor.client.chat.completions.create.return_value = mock_completion

        result = self.processor.call_api_for_tags_institution_interest("Title", "Abs", "Text")
        tag1, tag2, tag3_list, institution, code, contributions, llm_summary, mermaid = result

        self.assertEqual(tag1, "ai")
        self.assertEqual(code, "") # Should be empty string if not present
        self.assertEqual(mermaid, "") # Should be empty string if not present
        print("Passed missing fields test.")

    def test_call_api_with_irregular_format(self):
        print("\nTesting extraction with irregular format...")
        # 测试格式不规范的情况，例如 mermaid 块没有正确关闭，或者 key 大小写不同
        mock_response_content = """
TAG1: sys
Tag2: storage
tag3: SSD, file system
Institution: MIT
Code: None
Contributions: 1. New FS.
SUMMARY: A new file system.
Mermaid:
```mermaid
graph TD;
    A-->B;
```
"""
        # 设置 Mock 返回
        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock(message=MagicMock(content=mock_response_content))]
        self.processor.client.chat.completions.create.return_value = mock_completion

        result = self.processor.call_api_for_tags_institution_interest("Title", "Abs", "Text")
        tag1, tag2, tag3_list, institution, code, contributions, llm_summary, mermaid = result

        self.assertEqual(tag1, "sys")
        self.assertEqual(tag2, "storage")
        self.assertEqual(institution, "MIT")
        self.assertEqual(code, "None")
        self.assertEqual(mermaid.strip(), "graph TD;\n    A-->B;")
        print("Passed irregular format test.")

    def test_call_api_with_wrapped_content(self):
        print("\nTesting extraction with content wrapped in < >...")
        mock_response_content = """
tag1: t1
tag2: t2
tag3: t3
institution: inst
code: c
contributions: <1. contri.>
summary: <This is a summary.>
mermaid:
```mermaid
graph LR
A-->B
```
"""
        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock(message=MagicMock(content=mock_response_content))]
        self.processor.client.chat.completions.create.return_value = mock_completion

        result = self.processor.call_api_for_tags_institution_interest("Title", "Abs", "Text")
        tag1, tag2, tag3_list, institution, code, contributions, llm_summary, mermaid = result

        self.assertEqual(contributions, "1. contri.")
        self.assertEqual(llm_summary, "This is a summary.")
        print("Passed wrapped content test.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Test paper extraction logic.')
    parser.add_argument('--id', type=str, help='Run real extraction on a specific arXiv ID (e.g., 2312.00752)')
    
    # Use parse_known_args to allow other arguments to be passed to unittest (e.g. -v)
    args, remaining_argv = parser.parse_known_args()
    
    if args.id:
        run_real_extraction(args.id)
    else:
        # Run unit tests
        # construct argv for unittest: script name + remaining args
        unittest_argv = [sys.argv[0]] + remaining_argv
        unittest.main(argv=unittest_argv)
