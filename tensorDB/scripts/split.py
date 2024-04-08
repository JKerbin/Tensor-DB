import pdfplumber
import re


class SplitPDF:
    def __init__(self, pdf):
        self.pdf_path = pdf

    def split(self):
        extracted = ""

        # 读取PDF
        with pdfplumber.open(self.pdf_path) as pdf:
            # 遍历页面
            for page in pdf.pages:
                text = page.extract_text()
                extracted += text

        # 按句号分割
        split_res = re.split(r'[。.]', extracted)

        # 过滤空字符串
        split_res = [ele.strip() for ele in split_res if ele.strip()]

        return split_res
