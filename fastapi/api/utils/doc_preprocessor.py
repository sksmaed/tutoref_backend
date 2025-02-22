import PyPDF2
import re
from sentence_transformers import SentenceTransformer
from typing import Dict, List, Tuple
import logging

class TeachingPlanProcessor:
    def __init__(self):
        self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        
    def extract_pdf_text(self, pdf_path: str) -> str:
        """從 PDF 檔案提取文字內容"""
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                return text.strip()
        except Exception as e:
            logging.error(f"PDF 處理錯誤: {str(e)}")
            raise

    def parse_teaching_plan(self, text: str) -> Tuple[Dict, str]:
        """解析教案內容，返回基本資料和需要向量化的內容"""
        # 提取基本資料
        semester_match = re.search(r'(\d+)學年度第\s*([一二])\s*學期', text)
        semester = f"{semester_match.group(1)}-{semester_match.group(2)}" if semester_match else ""

        # 提取家別
        team_match = re.search(r'■\s*(加拿|初來|新武|霧鹿|利稻|電光)', text)
        team = team_match.group(1) if team_match else ""
        
        # 基本資料映射
        basic_info = {
            'tp_name': self._extract_field(text, r'課程名稱\s*(.*?)\s*(?:課程目標|$)'),
            'writer_name': self._extract_field(text, r'設計者\s*(.*?)\s*(?:\n|$)'),
            'team': team,
            'semester': semester,
            'category': self._extract_field(text, r'課程類別\s*(.*?)\s*(?:\n|$)'),
            'grade': self._extract_field(text, r'適用上課年級\s*(.*?)\s*(?:\n|$)'),
            'duration': self._extract_duration(text),
            'staffing': self._extract_field(text, r'課程所需人力\s*(.*?)\s*(?:\n|$)'),
            'venue': self._extract_field(text, r'課程所需場地\s*(.*?)\s*(?:\n|$)'),
            'objectives': self._extract_field(text, r'課程目標\s*(.*?)\s*(?:課程大綱|$)'),
            'outline': self._extract_field(text, r'課程大綱\s*(.*?)\s*(?:適用上課年級|$)')
        }

        # 提取流程內容
        # content = self._extract_procedure_content(text)
        
        return basic_info

    def _extract_field(self, text: str, pattern: str) -> str:
        """提取特定欄位內容"""
        match = re.search(pattern, text, re.DOTALL)
        return match.group(1).strip() if match else ""

    def _extract_duration(self, text: str) -> int:
        """提取課程時間並轉換為分鐘"""
        duration_match = re.search(r'課程所需時間\s*(\d+)\s*分鐘', text)
        return int(duration_match.group(1)) if duration_match else 0

    def _extract_procedure_content(self, text: str) -> str:
        """提取流程中的講解綱要與進行方式"""
        procedure_start = text.find("流程")
        if procedure_start == -1:
            return ""

        budget_start = text.find("經費預算")
        if budget_start == -1:
            budget_start = len(text)

        procedure_text = text[procedure_start:budget_start]

        # 提取多段流程文字
        content_parts = re.findall(
            r'第\d+-\d+分鐘.*?講解綱要與進行方式\s*(.*?)(?:教具種類與數量|$)',
            procedure_text,
            re.DOTALL
        )
        
        return "\n".join([part.strip() for part in content_parts if part.strip()])

    def generate_embeddings(self, text: str) -> Dict[str, List]:
        """生成文本的分段和 BERT embeddings"""
        try:
            # 分段處理
            chunks = text.split("\n\n")
            embeddings = [self.model.encode(chunk).tolist() for chunk in chunks]
            return {"chunks": chunks, "embeddings": embeddings}
        except Exception as e:
            logging.error(f"Embedding 生成錯誤: {str(e)}")
            raise