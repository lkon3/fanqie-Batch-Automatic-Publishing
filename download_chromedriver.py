# -*- coding: utf-8 -*-
"""
ChromeDriver 自动下载助手
帮助您快速下载正确的 ChromeDriver
"""
import requests
import zipfile
import os
import sys
import platform
import re

def get_chrome_version():
    """尝试获取 Chrome 版本"""
    print("正在检测 Chrome 版本...")
    try:
        # Windows 上 Chrome 的可能位置
        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe")
        ]

        chrome_path = None
        for path in chrome_paths:
            if os.path.exists(path):
                chrome_path = path
                break

        if not chrome_path:
            print("⚠ 无法自动检测 Chrome 版本")
            return None

        # 读取版本文件
        version_file = os.path.join(os.path.dirname(chrome_path), "chrome.VisualElementsManifest.xml")
        if os.path.exists(version_file):
            with open(version_file, 'r', encoding='utf-8') as f:
                content = f.read()
                match = re.search(r'(\d+\.\d+\.\d+\.\d+)', content)
                if match:
                    version = match.group(1)
                    print(f"✓ 检测到 Chrome 版本: {version}")
                    return version

        print("⚠ 无法读取 Chrome 版本信息")
        return None
    except Exception as e:
        print(f"⚠ 检测失败: {e}")
        return None


def download_chromedriver(version):
    """下载 ChromeDriver"""
    print(f"\n正在为 Chrome {version} 下载 ChromeDriver...")

    # 确定系统类型
    system = platform.system()
    if system != "Windows":
        print("⚠ 此脚本仅支持 Windows 系统")
        return False

    # 检查是否是 64 位
    is_64bit = platform.machine().endswith('64')
    if not is_64bit:
        print("⚠ 检测到 32 位系统，但大多数现代电脑都是 64 位")
        print("如果您的电脑是 64 位，请下载 win64 版本")

    # ChromeDriver 下载链接（使用新版本）
    major_version = version.split('.')[0]

    if int(major_version) >= 115:
        # 新版本 Chrome (115+)
        print("使用新版 ChromeDriver 下载地址...")
        url = f"https://storage.googleapis.com/chrome-for-testing-public/LATEST_RELEASE_{version}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                driver_version = response.text.strip()
                print(f"ChromeDriver 版本: {driver_version}")

                download_url = f"https://storage.googleapis.com/chrome-for-testing-public/{driver_version}/win64/chromedriver-win64.zip"
            else:
                print("⚠ 无法获取精确版本，尝试使用最新版...")
                download_url = "https://storage.googleapis.com/chrome-for-testing-public/LATEST_RELEASE_WIN64/download"
        except:
            print("⚠ 自动检测失败，请手动下载")
            return False
    else:
        # 旧版本 Chrome
        print("⚠ Chrome 版本较旧，请手动下载")
        return False

    # 下载文件
    print(f"\n下载地址: {download_url}")
    print("正在下载... (可能需要几分钟)")

    try:
        response = requests.get(download_url, stream=True)
        total_size = int(response.headers.get('content-length', 0))

        zip_path = "chromedriver.zip"
        with open(zip_path, 'wb') as f:
            if total_size == 0:
                f.write(response.content)
            else:
                downloaded = 0
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        percent = (downloaded / total_size) * 100
                        print(f"\r进度: {percent:.1f}%", end='')

        print("\n✓ 下载完成")

        # 解压
        print("正在解压...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(".")

        # 查找 chromedriver.exe
        for root, dirs, files in os.walk("."):
            for file in files:
                if file == "chromedriver.exe":
                    src = os.path.join(root, file)
                    dst = "chromedriver.exe"
                    if src != dst:
                        import shutil
                        shutil.move(src, dst)
                    print(f"✓ ChromeDriver 已提取到: {os.path.abspath(dst)}")

        # 清理
        os.remove(zip_path)
        if os.path.exists("chromedriver-win64"):
            import shutil
            shutil.rmtree("chromedriver-win64")

        return True

    except Exception as e:
        print(f"\n✗ 下载失败: {e}")
        return False


def main():
    print("=" * 50)
    print("ChromeDriver 自动下载助手")
    print("=" * 50)

    # 获取 Chrome 版本
    version = get_chrome_version()

    if not version:
        print("\n请手动输入您的 Chrome 版本号")
        print("格式如: 120.0.6099.109")
        version = input("Chrome 版本: ").strip()

        if not version:
            print("\n未输入版本号，无法继续")
            return

    # 下载
    success = download_chromedriver(version)

    if success:
        print("\n" + "=" * 50)
        print("✓ 下载完成！")
        print("=" * 50)
        print("\n现在可以运行程序了:")
        print("  python main.py")
    else:
        print("\n" + "=" * 50)
        print("自动下载失败，请手动下载")
        print("=" * 50)
        print("\n手动下载步骤:")
        print("1. 访问: https://googlechromelabs.github.io/chrome-for-testing/")
        print("2. 下载对应版本的 win64 ChromeDriver")
        print("3. 解压后将 chromedriver.exe 放到项目目录")
        print("\n详细教程请查看: ChromeDriver安装指南.md")


if __name__ == "__main__":
    main()
