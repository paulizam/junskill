"""
提取 epub 指定章节内容
"""
import ebooklib
from ebooklib import epub
import bs4
import sys
import argparse

def extract_chapter(epub_path, chapter_num):
    """提取指定章节"""
    book = epub.read_epub(epub_path)

    for item in book.get_items():
        if item.get_type() != ebooklib.ITEM_DOCUMENT:
            continue

        content = item.get_content()
        soup = bs4.BeautifulSoup(content, 'html.parser')
        text = soup.get_text()

        # 查找包含目标章节的内容
        if f"第{chapter_num}" in text or f"chapter{chapter_num}" in text.lower():
            return text, item.get_name()

    print(f"[WARN] 未找到第{chapter_num}章")
    return None, None

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("epub", help="epub 文件路径")
    parser.add_argument("chapter", type=int, help="章节数")
    parser.add_argument("-o", "--output", default="content.txt", help="输出文件")
    args = parser.parse_args()

    content, filename = extract_chapter(args.epub, args.chapter)

    if content:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"[OK] 章节内容已保存到: {args.output}")
    else:
        sys.exit(1)
