# -*- coding: utf-8 -*-
"""
批量定时发布调度器
在番茄小说平台设置定时发布
"""
import json
from datetime import datetime, timedelta
from typing import List, Dict

from parser import NovelParser
from publisher import TomatoNovelPublisher


class PublishScheduler:
    """批量定时发布调度器"""

    def __init__(self, config_file: str = "config.json"):
        """
        初始化调度器

        Args:
            config_file: 配置文件路径
        """
        self.config = self._load_config(config_file)
        self.parser = None
        self.publisher = None

    def _load_config(self, config_file: str) -> dict:
        """加载配置文件"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"配置文件 {config_file} 不存在")
            raise

    def load_novel(self, file_path: str = None, content: str = None):
        """
        加载小说文件

        Args:
            file_path: 小说文件路径
            content: 小说文本内容
        """
        self.parser = NovelParser(file_path=file_path, content=content)
        print(f"✓ 已加载小说，共 {self.parser.get_chapter_count()} 章")

    def init_publisher(self):
        """初始化发布器"""
        self.publisher = TomatoNovelPublisher()
        self.publisher.init_browser()
        print("✓ 浏览器已启动")

    def login(self):
        """登录番茄小说"""
        if not self.publisher:
            self.init_publisher()
        self.publisher.login()

    def select_novel(self):
        """选择要发布的书本"""
        if not self.publisher:
            self.init_publisher()

        print("\n" + "=" * 50)
        print("书本选择")
        print("=" * 50)

        success = self.publisher.select_novel_interactive()

        if not success:
            print("✗ 书本选择失败")
            return False

        return True

    def publish_immediately(self, count: int = None, start_index: int = 0, select_novel_first: bool = True):
        """
        立即发布指定数量的章节

        Args:
            count: 发布章节数量（None表示全部）
            start_index: 起始章节索引
            select_novel_first: 是否先选择书本
        """
        if not self.parser:
            raise ValueError("请先使用 load_novel() 加载小说文件")

        if not self.publisher:
            self.init_publisher()

        # 选择书本
        if select_novel_first:
            if not self.select_novel():
                print("✗ 无法选择书本，发布流程终止")
                return

        chapters = self.parser.get_chapters()

        if start_index >= len(chapters):
            print("起始索引超出范围")
            return

        if count is None:
            chapters_to_publish = chapters[start_index:]
        else:
            chapters_to_publish = chapters[start_index:start_index + count]

        print(f"\n{'=' * 50}")
        print(f"立即发布模式")
        print(f"{'=' * 50}")
        print(f"总章节: {len(chapters)}")
        print(f"即将发布: {len(chapters_to_publish)} 章")
        if self.publisher.selected_novel:
            print(f"目标书本: {self.publisher.selected_novel['title']}")
        print(f"{'=' * 50}\n")

        result = self.publisher.publish_batch(chapters_to_publish)

        print(f"\n{'=' * 50}")
        print(f"发布完成")
        print(f"成功: {len(result['success'])} 章")
        print(f"失败: {len(result['failed'])} 章")
        print(f"{'=' * 50}\n")

        return result

    def publish_scheduled(self,
                         start_date: datetime = None,
                         chapters_per_day: int = None,
                         publish_times: List[str] = None,
                         start_index: int = 0,
                         select_novel_first: bool = True):
        """
        批量定时发布（在番茄平台设置定时发布）

        Args:
            start_date: 开始日期（默认为明天）
            chapters_per_day: 每天发布章节数
            publish_times: 发布时间列表（如 ["08:00", "20:00"]）
            start_index: 起始章节索引
            select_novel_first: 是否先选择书本
        """
        if not self.parser:
            raise ValueError("请先使用 load_novel() 加载小说文件")

        if not self.publisher:
            self.init_publisher()

        # 选择书本
        if select_novel_first:
            if not self.select_novel():
                print("✗ 无法选择书本，发布流程终止")
                return

        chapters = self.parser.get_chapters()

        if start_index >= len(chapters):
            print("起始索引超出范围")
            return

        # 从配置文件读取默认值
        if chapters_per_day is None:
            chapters_per_day = self.config.get('chapters_per_day', 2)

        if publish_times is None:
            publish_times = self.config.get('publish_times', ['08:00', '20:00'])

        if start_date is None:
            # 默认从明天开始
            start_date = datetime.now() + timedelta(days=1)

        chapters_to_publish = chapters[start_index:]

        print(f"\n{'=' * 50}")
        print(f"批量定时发布模式")
        print(f"{'=' * 50}")
        print(f"总章节: {len(chapters)}")
        print(f"待发布: {len(chapters_to_publish)} 章")
        print(f"开始索引: {start_index}")
        if self.publisher.selected_novel:
            print(f"目标书本: {self.publisher.selected_novel['title']}")
        print(f"每天发布: {chapters_per_day} 章")
        print(f"发布时间: {', '.join(publish_times)}")
        print(f"{'=' * 50}\n")

        result = self.publisher.publish_batch_scheduled(
            chapters=chapters_to_publish,
            start_date=start_date,
            chapters_per_day=chapters_per_day,
            publish_times=publish_times
        )

        return result

    def close(self):
        """关闭浏览器"""
        if self.publisher:
            self.publisher.close()


def main():
    """主函数 - 命令行交互"""
    print("=" * 50)
    print("番茄小说批量定时发布系统")
    print("=" * 50)

    # 加载配置
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
    except FileNotFoundError:
        print("错误：配置文件不存在，请先运行 main.py 创建配置文件")
        return

    # 创建调度器
    scheduler = PublishScheduler()

    # 加载小说
    novel_file = input("\n请输入小说文件路径（.txt）: ").strip()
    if not novel_file:
        print("未输入文件路径，程序退出")
        return

    try:
        scheduler.load_novel(file_path=novel_file)
    except Exception as e:
        print(f"✗ 加载小说失败: {e}")
        return

    # 选择发布模式
    print("\n请选择发布模式:")
    print("1. 批量定时发布（在番茄平台设置定时发布）")
    print("2. 立即批量发布")

    choice = input("\n请输入选择（1 或 2）: ").strip()

    if choice == '1':
        # 批量定时发布
        print("\n批量定时发布配置:")
        start_date_input = input("开始日期（格式：YYYY-MM-DD，留空默认明天）: ").strip()

        if start_date_input:
            try:
                start_date = datetime.strptime(start_date_input, '%Y-%m-%d')
            except ValueError:
                print("日期格式错误，将使用默认值（明天）")
                start_date = datetime.now() + timedelta(days=1)
        else:
            start_date = datetime.now() + timedelta(days=1)

        chapters_per_day = input(f"每天发布章节数（留空默认 {config['chapters_per_day']}）: ").strip()
        chapters_per_day = int(chapters_per_day) if chapters_per_day else config['chapters_per_day']

        publish_times_input = input(f"发布时间，用逗号分隔（留空默认 {config['publish_times']}）: ").strip()
        if publish_times_input:
            publish_times = [t.strip() for t in publish_times_input.split(',')]
        else:
            publish_times = config['publish_times']

        scheduler.publish_scheduled(
            start_date=start_date,
            chapters_per_day=chapters_per_day,
            publish_times=publish_times
        )

        scheduler.close()

    elif choice == '2':
        # 立即发布
        count_input = input("发布章节数量（留空或输入 'all' 发布全部）: ").strip()

        if count_input.lower() == 'all' or not count_input:
            count = None
        else:
            count = int(count_input)

        scheduler.publish_immediately(count=count)
        scheduler.close()

    else:
        print("无效选择")


if __name__ == "__main__":
    main()
