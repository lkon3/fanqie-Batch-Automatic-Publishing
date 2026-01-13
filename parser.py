# -*- coding: utf-8 -*-
"""
小说章节解析器
支持识别章节标题和正文内容
"""
import re
from typing import List, Dict
from pathlib import Path


class NovelParser:
    """小说解析器，自动识别章节标题和正文"""

    # 常见章节标题正则表达式
    CHAPTER_PATTERNS = [
        r'^[第]\s*[0-9零一二三四五六七八九十百千]+\s*[章节卷集回部篇]',
        r'^Chapter\s*\d+',
        r'^\d+\.',
        r'^\d+、',
        r'^【.*第.*章.*】',
        r'^.*第.*[0-9零一二三四五六七八九十百千]+.*章.*',
    ]

    def __init__(self, file_path: str = None, content: str = None):
        """
        初始化解析器

        Args:
            file_path: 小说文件路径（支持 .txt）
            content: 小说文本内容
        """
        if file_path:
            self.file_path = Path(file_path)
            if not self.file_path.exists():
                raise FileNotFoundError(f"文件不存在: {file_path}")
            # 尝试多种编码
            encodings = ['utf-8', 'gbk', 'gb2312', 'utf-16']
            self.content = None
            for encoding in encodings:
                try:
                    with open(self.file_path, 'r', encoding=encoding) as f:
                        self.content = f.read()
                    break
                except UnicodeDecodeError:
                    continue
            if self.content is None:
                raise ValueError("无法识别文件编码，请确保文件是 utf-8 或 gbk 格式")
        elif content:
            self.content = content
            self.file_path = None
        else:
            raise ValueError("必须提供 file_path 或 content 参数")

        self.chapters = []
        self._parse()

    def _is_chapter_title(self, line: str) -> bool:
        """判断是否为章节标题"""
        line = line.strip()
        if not line:
            return False

        for pattern in self.CHAPTER_PATTERNS:
            if re.match(pattern, line, re.IGNORECASE):
                return True
        return False

    def _parse(self):
        """解析小说内容"""
        lines = self.content.split('\n')
        chapters = []

        current_chapter = None
        current_content = []

        for line in lines:
            if self._is_chapter_title(line):
                # 保存上一个章节
                if current_chapter:
                    chapters.append({
                        'title': current_chapter,
                        'content': '\n'.join(current_content).strip()
                    })

                # 开始新章节
                current_chapter = line.strip()
                current_content = []
            else:
                if current_chapter:  # 如果已经找到第一个章节
                    current_content.append(line)

        # 保存最后一个章节
        if current_chapter:
            chapters.append({
                'title': current_chapter,
                'content': '\n'.join(current_content).strip()
            })

        self.chapters = chapters

    def get_chapters(self) -> List[Dict[str, str]]:
        """获取所有章节"""
        return self.chapters

    def get_chapter_count(self) -> int:
        """获取章节数量"""
        return len(self.chapters)

    def get_chapter(self, index: int) -> Dict[str, str]:
        """获取指定章节（从0开始）"""
        if 0 <= index < len(self.chapters):
            return self.chapters[index]
        raise IndexError(f"章节索引超出范围: {index}")

    def save_chapters(self, output_dir: str = "chapters"):
        """将每个章节保存为单独文件"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        for i, chapter in enumerate(self.chapters, 1):
            filename = f"{i:03d}_{chapter['title'][:20]}.txt"
            filename = filename.replace('/', '_').replace('\\', '_').replace(':', '_')
            file_path = output_path / filename

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"{chapter['title']}\n\n")
                f.write(chapter['content'])

        print(f"已保存 {len(self.chapters)} 个章节到 {output_dir} 目录")

    def __repr__(self):
        return f"NovelParser(chapters={len(self.chapters)}, file={self.file_path})"


if __name__ == "__main__":
    # 测试代码
    test_content = """
    第一章 开始

    这是第一章的内容。

    第二章 继续

    这是第二章的内容。
    更多的正文内容在这里。

    第三章 结束

    这是第三章的内容。
    """

    parser = NovelParser(content=test_content)
    print(f"解析到 {parser.get_chapter_count()} 个章节:")
    for chapter in parser.get_chapters():
        print(f"- {chapter['title']}")
