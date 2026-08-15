# -*- coding: utf-8 -*-
# 提取 副本1-4.docx 文本 → 06_对话转录/历史版本分享/
import zipfile, re, os

SRC = r'D:\Cola'
OUT = r'D:\Cola\足球分析学习\06_对话转录\历史版本分享'

def extract_docx(path):
    with zipfile.ZipFile(path) as z:
        xml = z.read('word/document.xml').decode('utf-8', errors='ignore')
    # 段落分割
    xml = xml.replace('</w:p>', '\n')
    # 去标签
    text = re.sub(r'<[^>]+>', '', xml)
    # 解实体
    text = text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"').replace('&#39;', "'")
    return text

for i in range(1, 5):
    p = os.path.join(SRC, f'副本{i}.docx')
    t = extract_docx(p)
    out = os.path.join(OUT, f'副本{i}_提取.txt')
    open(out, 'w', encoding='utf-8').write(t)
    lines = t.count('\n')
    print(f'副本{i}: {len(t)} 字符, {lines} 行 → {out}')
