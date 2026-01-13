# -*- coding: utf-8 -*-
"""
番茄小说自动发布系统 - 主程序
"""
import json
import sys
from datetime import datetime, timedelta
from parser import NovelParser
from publisher import TomatoNovelPublisher
from scheduler import PublishScheduler


def create_config():
    """创建配置文件"""
    config = {
        "novel_id": "",
        "publish_url": "https://fanqienovel.com/page/WriteNovel",
        "headless": False,
        "chapters_per_day": 2,
        "publish_times": ["08:00", "20:00"],
        "account": {
            "phone": "",
            "auto_login": True
        }
    }

    with open('config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

    print("✓ 配置文件已创建: config.json")
    print("请根据需要修改配置文件中的参数\n")


def test_parser():
    """测试小说解析功能"""
    print("\n" + "=" * 50)
    print("小说解析测试")
    print("=" * 50)

    file_path = input("\n请输入小说文件路径（.txt）: ").strip()

    if not file_path:
        print("未输入文件路径")
        return

    try:
        parser = NovelParser(file_path=file_path)
        chapters = parser.get_chapters()

        print(f"\n✓ 解析成功！共找到 {len(chapters)} 章\n")
        print("前 5 章标题:")
        for i, chapter in enumerate(chapters[:5], 1):
            print(f"  {i}. {chapter['title']}")

        if len(chapters) > 5:
            print(f"  ... 还有 {len(chapters) - 5} 章")

        # 询问是否导出章节
        export = input("\n是否将章节导出为单独文件？(y/n): ").strip().lower()
        if export == 'y':
            parser.save_chapters()

    except Exception as e:
        print(f"✗ 解析失败: {e}")


def test_login():
    """测试登录功能"""
    print("\n" + "=" * 50)
    print("登录测试")
    print("=" * 50)
    print("\n首次使用需要登录番茄小说账号")

    try:
        publisher = TomatoNovelPublisher()
        publisher.login()
        publisher.close()
        print("\n✓ 登录状态已保存")
    except Exception as e:
        print(f"✗ 登录失败: {e}")


def view_novels():
    """查看书本列表"""
    print("\n" + "=" * 50)
    print("查看书本列表")
    print("=" * 50)
    print("\n正在获取您的书本列表...")

    try:
        publisher = TomatoNovelPublisher()
        publisher.init_browser()

        novels = publisher.get_novels()

        if novels:
            print(f"\n✓ 共找到 {len(novels)} 本书\n")
        else:
            print("\n⚠ 未能自动获取书本列表")
            print("这可能是因为：")
            print("  1. 您还未登录番茄小说（请先选择功能 3 登录）")
            print("  2. 您还没有创建任何书籍")
            print("  3. 页面元素发生了变化")
            print("\n建议：")
            print("  - 先使用功能 3 登录番茄小说")
            print("  - 在发布时手动选择书本")

        publisher.close()

    except Exception as e:
        print(f"✗ 获取书本列表失败: {e}")


def publish_immediately():
    """立即批量发布"""
    print("\n" + "=" * 50)
    print("立即批量发布模式")
    print("=" * 50)

    file_path = input("\n请输入小说文件路径（.txt）: ").strip()

    if not file_path:
        print("未输入文件路径")
        return

    try:
        scheduler = PublishScheduler()
        scheduler.load_novel(file_path=file_path)

        chapters = scheduler.parser.get_chapters()
        print(f"\n总章节: {len(chapters)}")

        count = input("\n请输入要发布的章节数量（输入 'all' 发布全部）: ").strip()

        if count.lower() == 'all':
            count = None
        else:
            count = int(count)

        confirm = input(f"\n确认立即发布 {len(chapters) if count is None else count} 章？(y/n): ").strip().lower()
        if confirm == 'y':
            scheduler.publish_immediately(count=count)
            scheduler.close()
        else:
            print("已取消")

    except Exception as e:
        print(f"✗ 发布失败: {e}")


def publish_scheduled():
    """批量定时发布"""
    print("\n" + "=" * 50)
    print("批量定时发布模式")
    print("=" * 50)
    print("\n此功能将在番茄小说平台设置定时发布")
    print("您可以一次性设置多章的发布时间，番茄平台会自动按时发布\n")

    file_path = input("请输入小说文件路径（.txt）: ").strip()

    if not file_path:
        print("未输入文件路径")
        return

    try:
        scheduler = PublishScheduler()
        scheduler.load_novel(file_path=file_path)

        chapters = scheduler.parser.get_chapters()
        print(f"\n总章节: {len(chapters)}")

        # 读取配置
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)

        print(f"\n当前配置:")
        print(f"  - 每天发布: {config['chapters_per_day']} 章")
        print(f"  - 发布时间: {', '.join(config['publish_times'])}")

        use_default = input("\n是否使用默认配置？(y/n，默认 y): ").strip().lower()

        if use_default == 'n':
            # 自定义配置
            chapters_per_day = input(f"每天发布章节数（当前 {config['chapters_per_day']}）: ").strip()
            chapters_per_day = int(chapters_per_day) if chapters_per_day else config['chapters_per_day']

            publish_times_input = input(f"发布时间，用逗号分隔（当前 {config['publish_times']}）: ").strip()
            if publish_times_input:
                publish_times = [t.strip() for t in publish_times_input.split(',')]
            else:
                publish_times = config['publish_times']

            start_date_input = input("开始日期（格式：YYYY-MM-DD，留空默认明天）: ").strip()
            if start_date_input:
                try:
                    start_date = datetime.strptime(start_date_input, '%Y-%m-%d')
                except ValueError:
                    print("日期格式错误，将使用默认值（明天）")
                    start_date = datetime.now() + timedelta(days=1)
            else:
                start_date = None  # 使用默认值
        else:
            chapters_per_day = None
            publish_times = None
            start_date = None

        # 计算预计完成时间
        total_days = (len(chapters) + (chapters_per_day or config['chapters_per_day']) - 1) // \
                    (chapters_per_day or config['chapters_per_day'])

        print(f"\n{'=' * 50}")
        print(f"发布计划预览")
        print(f"{'=' * 50}")
        print(f"总章节: {len(chapters)}")
        print(f"每天发布: {chapters_per_day or config['chapters_per_day']} 章")
        print(f"发布时间: {', '.join(publish_times or config['publish_times'])}")
        print(f"预计需要: {total_days} 天")
        print(f"{'=' * 50}")

        confirm = input("\n确认开始批量定时发布？(y/n): ").strip().lower()
        if confirm == 'y':
            scheduler.publish_scheduled(
                start_date=start_date,
                chapters_per_day=chapters_per_day,
                publish_times=publish_times
            )
            scheduler.close()
            print("\n✓ 所有章节已设置定时发布，番茄平台将自动按时发布")
        else:
            print("已取消")

    except Exception as e:
        print(f"✗ 发布失败: {e}")


def show_menu():
    """显示主菜单"""
    print("\n" + "=" * 50)
    print("番茄小说自动发布系统")
    print("=" * 50)
    print("1. 创建/重置配置文件")
    print("2. 测试小说解析")
    print("3. 测试登录（首次使用必须先登录）")
    print("4. 查看书本列表")
    print("5. 立即批量发布")
    print("6. 批量定时发布（在番茄平台设置定时发布）")
    print("0. 退出")
    print("=" * 50)


def main():
    """主函数"""
    # 检查配置文件
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            pass
    except FileNotFoundError:
        print("首次运行，正在创建配置文件...")
        create_config()

    while True:
        show_menu()
        choice = input("\n请选择功能（0-6）: ").strip()

        if choice == '0':
            print("再见！")
            break
        elif choice == '1':
            create_config()
        elif choice == '2':
            test_parser()
        elif choice == '3':
            test_login()
        elif choice == '4':
            view_novels()
        elif choice == '5':
            publish_immediately()
        elif choice == '6':
            publish_scheduled()
        else:
            print("无效选择，请重新输入")


if __name__ == "__main__":
    main()
