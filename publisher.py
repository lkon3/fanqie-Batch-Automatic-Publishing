# -*- coding: utf-8 -*-
"""
番茄小说自动发布器
使用 Selenium 自动化发布章节到番茄小说
支持定时发布功能
"""
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


class TomatoNovelPublisher:
    """番茄小说自动发布器"""

    def __init__(self, config_file: str = "config.json"):
        """
        初始化发布器

        Args:
            config_file: 配置文件路径
        """
        self.config = self._load_config(config_file)
        self.driver = None
        self.wait = None
        self.novels = []  # 书本列表
        self.selected_novel = None  # 选中的书本

    def _load_config(self, config_file: str) -> dict:
        """加载配置文件"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"配置文件 {config_file} 不存在，将创建默认配置")
            return self._create_default_config(config_file)

    def _create_default_config(self, config_file: str) -> dict:
        """创建默认配置文件"""
        default_config = {
            "novel_id": "",  # 番茄小说中你的小说ID
            "publish_url": "https://fanqienovel.com/page/WriteNovel",  # 发布页面URL
            "headless": False,  # 是否无头模式（True时不显示浏览器）
            "chapters_per_day": 2,  # 每天发布章节数
            "publish_times": ["08:00", "20:00"],  # 发布时间
            "account": {
                "phone": "",  # 手机号
                "auto_login": True  # 是否自动登录（需要手动扫码一次）
            }
        }

        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, ensure_ascii=False, indent=2)

        print(f"已创建默认配置文件: {config_file}")
        print("请修改配置文件中的参数后重新运行")
        return default_config

    def init_browser(self):
        """初始化浏览器"""
        chrome_options = Options()

        if self.config.get('headless', False):
            chrome_options.add_argument('--headless')

        # 设置用户数据目录，保持登录状态
        chrome_options.add_argument('--user-data-dir=./chrome_profile')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        # 禁用自动化标识
        chrome_options.add_argument('--disable-infobars')

        try:
            # 尝试使用 webdriver-manager 自动下载 ChromeDriver
            from webdriver_manager.chrome import ChromeDriverManager
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
        except Exception as e:
            print(f"⚠ 使用 webdriver-manager 失败: {e}")
            print("尝试使用系统已安装的 ChromeDriver...")
            try:
                # 尝试使用系统路径中的 chromedriver
                self.driver = webdriver.Chrome(options=chrome_options)
            except Exception as e2:
                print(f"✗ 初始化浏览器失败: {e2}")
                print("\n请按以下步骤操作：")
                print("1. 确保已安装 Chrome 浏览器")
                print("2. 下载 ChromeDriver: https://googlechromelabs.github.io/chrome-for-testing/")
                print("3. 将 ChromeDriver 放到系统 PATH 环境变量中")
                print("4. 或将 ChromeDriver.exe 放到当前目录")
                raise

        self.wait = WebDriverWait(self.driver, 30)
        print("✓ 浏览器已启动")

    def login(self):
        """
        登录番茄小说
        首次需要手动扫码登录，之后会保持登录状态
        """
        if not self.driver:
            self.init_browser()

        self.driver.get("https://fanqienovel.com/")

        print("=" * 50)
        print("请在浏览器中扫码登录番茄小说")
        print("登录成功后，程序会继续执行...")
        print("=" * 50)

        # 等待用户手动登录
        input("登录完成后，按回车键继续...")

        print("登录状态已保存，下次可自动登录")

    def get_novels(self) -> List[Dict]:
        """
        获取用户的书本列表

        Returns:
            书本列表 [{'id': '', 'title': '', 'url': ''}, ...]
        """
        if not self.driver:
            self.init_browser()

        try:
            # 导航到作家主页或作品管理页面
            self.driver.get("https://fanqienovel.com/page/WriteNovel")
            time.sleep(3)

            novels = []

            # 尝试多种方式获取书本列表
            # 方式1: 从发布页面获取书本选择器
            try:
                # 查找书本选择元素（可能是下拉框、按钮列表等）
                novel_selectors = [
                    '//div[contains(@class, "novel-selector")]',
                    '//select[contains(@class, "novel")]',
                    '//div[@role="combobox"]',
                    '//button[contains(text(), "选择作品")]',
                    '//div[contains(@class, "book")]',
                ]

                novel_elements = []
                for selector in novel_selectors:
                    try:
                        elements = self.driver.find_elements(By.XPATH, selector)
                        if elements:
                            novel_elements = elements
                            break
                    except:
                        continue

                # 如果找到了书本元素，解析书本信息
                if novel_elements:
                    for elem in novel_elements:
                        try:
                            title = elem.text.strip()
                            if title:
                                novel_id = elem.get_attribute('data-id') or \
                                          elem.get_attribute('value') or \
                                          elem.get_attribute('id')
                                novels.append({
                                    'id': novel_id,
                                    'title': title,
                                    'element': elem
                                })
                        except:
                            continue

            except Exception as e:
                print(f"⚠ 自动获取书本列表失败: {e}")

            # 方式2: 从URL或API获取（如果需要）
            # 这里可以添加API调用或页面解析逻辑

            self.novels = novels

            if novels:
                print(f"\n✓ 找到 {len(novels)} 本书:")
                for i, novel in enumerate(novels, 1):
                    print(f"  {i}. {novel['title']}")
            else:
                print("\n⚠ 未找到书本列表")
                print("提示：程序可能无法自动获取书本列表")
                print("您可以在发布页面手动选择书本")

            return novels

        except Exception as e:
            print(f"✗ 获取书本列表失败: {e}")
            return []

    def select_novel(self, novel_index: int = None) -> bool:
        """
        选择要发布的书本

        Args:
            novel_index: 书本索引（从1开始），None表示手动选择

        Returns:
            是否选择成功
        """
        if not self.novels:
            print("⚠ 请先获取书本列表（使用 get_novels()）")
            return False

        if novel_index is None:
            # 交互式选择
            print("\n请选择要发布的书本:")
            for i, novel in enumerate(self.novels, 1):
                print(f"  {i}. {novel['title']}")

            try:
                choice = input(f"\n请输入书本编号（1-{len(self.novels)}）: ").strip()
                novel_index = int(choice)
            except ValueError:
                print("✗ 输入无效")
                return False

        if 1 <= novel_index <= len(self.novels):
            self.selected_novel = self.novels[novel_index - 1]
            print(f"\n✓ 已选择书本: {self.selected_novel['title']}")
            return True
        else:
            print(f"✗ 书本编号超出范围（1-{len(self.novels)}）")
            return False

    def select_novel_interactive(self) -> bool:
        """
        交互式选择书本（自动获取列表并让用户选择）
        适合在发布流程中使用

        Returns:
            是否选择成功
        """
        # 获取书本列表
        novels = self.get_novels()

        if not novels:
            print("\n无法自动获取书本列表")
            print("请按以下步骤操作：")
            print("1. 浏览器会打开发布页面")
            print("2. 手动在页面中选择要发布的书本")
            print("3. 选择完成后，在命令行输入 'ok' 继续")

            input("\n按回车键打开浏览器...")

            if not self.driver:
                self.init_browser()

            self.driver.get(self.config['publish_url'])
            time.sleep(2)

            input("\n在浏览器中手动选择书本后，输入 'ok' 继续: ")
            return True

        # 显示书本列表并让用户选择
        print("\n" + "=" * 50)
        print("书本列表")
        print("=" * 50)

        for i, novel in enumerate(novels, 1):
            print(f"{i}. {novel['title']}")

        print("=" * 50)

        try:
            choice = input(f"\n请选择书本编号（1-{len(novels)}）: ").strip()
            novel_index = int(choice)

            if 1 <= novel_index <= len(novels):
                self.selected_novel = novels[novel_index - 1]
                print(f"✓ 已选择: {self.selected_novel['title']}")

                # 尝试点击选择书本（如果找到了元素）
                if 'element' in self.selected_novel:
                    try:
                        self.selected_novel['element'].click()
                        time.sleep(1)
                    except:
                        pass

                return True
            else:
                print(f"✗ 编号超出范围")
                return False

        except ValueError:
            print("✗ 输入无效")
            return False

    def publish_chapter(self, title: str, content: str, scheduled_time: Optional[datetime] = None) -> bool:
        """
        发布单个章节（支持立即发布或定时发布）

        Args:
            title: 章节标题
            content: 章节内容
            scheduled_time: 定时发布时间（None表示立即发布）

        Returns:
            是否发布成功
        """
        if not self.driver:
            self.init_browser()

        try:
            # 导航到发布页面
            self.driver.get(self.config['publish_url'])
            time.sleep(3)

            # 等待页面加载
            # 注意：番茄小说的页面元素可能变化，需要根据实际情况调整

            # 选择小说（如果有多个）
            # TODO: 根据实际页面元素选择小说

            # 输入章节标题
            title_input = self.wait.until(
                EC.presence_of_element_located((By.XPATH, '//input[@placeholder="请输入章节标题" or @type="text"]'))
            )
            title_input.clear()
            title_input.send_keys(title)

            # 输入章节内容
            content_input = self.driver.find_element(By.XPATH,
                                                     '//textarea[@placeholder="请输入章节内容"] | //div[@contenteditable="true"]')

            if content_input.tag_name == 'textarea':
                content_input.clear()
                content_input.send_keys(content)
            else:
                # contenteditable div
                self.driver.execute_script("arguments[0].innerText = arguments[1];", content_input, content)

            time.sleep(1)

            # 如果需要定时发布
            if scheduled_time:
                self._set_scheduled_publish(scheduled_time)

            # 点击发布按钮
            publish_button = self.driver.find_element(By.XPATH, '//button[contains(text(),"发布") or contains(text(),"提交")]')
            publish_button.click()

            # 等待发布完成
            time.sleep(3)

            if scheduled_time:
                print(f"✓ 章节《{title}》已设置定时发布: {scheduled_time.strftime('%Y-%m-%d %H:%M')}")
            else:
                print(f"✓ 章节《{title}》立即发布成功")
            return True

        except Exception as e:
            print(f"✗ 章节《{title}》发布失败: {str(e)}")
            return False

    def _set_scheduled_publish(self, publish_time: datetime):
        """
        设置定时发布

        Args:
            publish_time: 发布时间
        """
        try:
            # 查找并点击"定时发布"选项
            # 注意：这里需要根据番茄小说实际页面的元素进行调整

            # 尝试多种可能的选择器
            schedule_selectors = [
                '//label[contains(text(),"定时发布")]',
                '//span[contains(text(),"定时发布")]',
                '//div[contains(text(),"定时发布")]',
                '//input[@value="scheduled"]',
                '//button[contains(text(),"定时发布")]',
            ]

            schedule_element = None
            for selector in schedule_selectors:
                try:
                    schedule_element = self.driver.find_element(By.XPATH, selector)
                    if schedule_element:
                        break
                except:
                    continue

            if not schedule_element:
                print("⚠ 未找到定时发布选项，将立即发布")
                return

            # 点击定时发布选项
            schedule_element.click()
            time.sleep(1)

            # 设置日期和时间
            # 根据番茄小说实际的日期时间选择器进行调整
            date_str = publish_time.strftime('%Y-%m-%d')
            time_str = publish_time.strftime('%H:%M')

            # 尝试查找日期输入框
            date_inputs = self.driver.find_elements(By.XPATH, '//input[@type="date"] | //input[contains(@placeholder,"日期")]')
            if date_inputs:
                date_inputs[0].clear()
                date_inputs[0].send_keys(date_str)

            # 尝试查找时间输入框
            time_inputs = self.driver.find_elements(By.XPATH, '//input[@type="time"] | //input[contains(@placeholder,"时间")]')
            if time_inputs:
                time_inputs[0].clear()
                time_inputs[0].send_keys(time_str)

            print(f"已设置定时发布时间: {date_str} {time_str}")

        except Exception as e:
            print(f"⚠ 设置定时发布失败，将立即发布: {str(e)}")

    def publish_batch(self, chapters: List[Dict[str, str]]) -> Dict[str, List[str]]:
        """
        批量立即发布章节

        Args:
            chapters: 章节列表 [{'title': '', 'content': ''}, ...]

        Returns:
            发布结果 {'success': [titles], 'failed': [titles]}
        """
        if not self.driver:
            self.init_browser()

        result = {
            'success': [],
            'failed': []
        }

        for i, chapter in enumerate(chapters, 1):
            print(f"\n正在发布第 {i}/{len(chapters)} 章...")
            success = self.publish_chapter(chapter['title'], chapter['content'])

            if success:
                result['success'].append(chapter['title'])
            else:
                result['failed'].append(chapter['title'])

            # 避免频繁发布，等待几秒
            if i < len(chapters):
                time.sleep(5)

        return result

    def publish_batch_scheduled(self, chapters: List[Dict[str, str]],
                                start_date: datetime = None,
                                chapters_per_day: int = 2,
                                publish_times: List[str] = None) -> Dict[str, List[str]]:
        """
        批量定时发布章节（在番茄平台设置定时发布）

        Args:
            chapters: 章节列表
            start_date: 开始日期（默认为明天）
            chapters_per_day: 每天发布章节数
            publish_times: 每天的发布时间列表（如 ["08:00", "20:00"]）

        Returns:
            发布结果 {'success': [titles], 'failed': [titles], 'schedule': [datetime]}
        """
        if not self.driver:
            self.init_browser()

        if publish_times is None:
            publish_times = ["08:00", "20:00"]

        if start_date is None:
            start_date = datetime.now() + timedelta(days=1)

        result = {
            'success': [],
            'failed': [],
            'schedule': []
        }

        # 生成发布时间表
        schedule = self._generate_schedule(
            total_chapters=len(chapters),
            start_date=start_date,
            chapters_per_day=chapters_per_day,
            publish_times=publish_times
        )

        print(f"\n{'=' * 50}")
        print(f"批量定时发布计划")
        print(f"{'=' * 50}")
        print(f"总章节数: {len(chapters)}")
        print(f"每天发布: {chapters_per_day} 章")
        print(f"发布时间: {', '.join(publish_times)}")
        print(f"开始日期: {start_date.strftime('%Y-%m-%d')}")
        print(f"预计完成: {schedule[-1].strftime('%Y-%m-%d')}")
        print(f"{'=' * 50}\n")

        # 按计划发布每一章
        for i, (chapter, publish_time) in enumerate(zip(chapters, schedule), 1):
            print(f"\n[{i}/{len(chapters)}] 设置《{chapter['title']}》...")
            print(f"    发布时间: {publish_time.strftime('%Y-%m-%d %H:%M')}")

            success = self.publish_chapter(chapter['title'], chapter['content'], publish_time)

            if success:
                result['success'].append(chapter['title'])
                result['schedule'].append(publish_time)
            else:
                result['failed'].append(chapter['title'])

            # 避免频繁操作，等待几秒
            if i < len(chapters):
                time.sleep(5)

        print(f"\n{'=' * 50}")
        print(f"批量定时发布完成")
        print(f"成功: {len(result['success'])} 章")
        print(f"失败: {len(result['failed'])} 章")
        print(f"{'=' * 50}\n")

        return result

    def _generate_schedule(self, total_chapters: int,
                          start_date: datetime,
                          chapters_per_day: int,
                          publish_times: List[str]) -> List[datetime]:
        """
        生成发布时间表

        Args:
            total_chapters: 总章节数
            start_date: 开始日期
            chapters_per_day: 每天发布章节数
            publish_times: 发布时间列表

        Returns:
            发布时间列表
        """
        schedule = []
        current_date = start_date
        time_index = 0

        for i in range(total_chapters):
            # 获取当天的发布时间
            publish_time_str = publish_times[time_index % len(publish_times)]
            hour, minute = map(int, publish_time_str.split(':'))

            # 创建发布时间
            publish_time = current_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
            schedule.append(publish_time)

            # 更新索引
            time_index += 1

            # 如果完成一天的发布量，移动到下一天
            if time_index >= len(publish_times):
                time_index = 0
                current_date += timedelta(days=1)

        return schedule

    def close(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()
            print("浏览器已关闭")


if __name__ == "__main__":
    # 测试代码
    publisher = TomatoNovelPublisher()
    publisher.login()
    publisher.close()
