# -*- coding: utf-8 -*-
"""
简化的浏览器测试 - 修复版
不使用特殊字符，避免 Windows 命令行编码问题
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

print("=" * 50)
print("Simple Browser Test")
print("=" * 50)

# Test 1: Simple start
print("\n[Test 1] Starting Chrome...")

try:
    driver = webdriver.Chrome()
    print("[OK] Browser started successfully!")
    print("Opening Baidu...")
    driver.get("https://www.baidu.com")
    print("[OK] Baidu opened")
    print("\nIf you can see the browser window, everything is OK!")
    input("\nPress Enter to close browser...")
    driver.quit()
    print("[OK] Browser closed")

    print("\n" + "=" * 50)
    print("SUCCESS!")
    print("=" * 50)
    print("\nYour ChromeDriver is working!")
    print("You can now use: python main.py")

except Exception as e:
    print(f"\n[FAILED] Error: {e}")

    print("\n" + "=" * 50)
    print("FAILED")
    print("=" * 50)
    print("\nPossible reasons:")
    print("1. ChromeDriver not installed")
    print("2. ChromeDriver version mismatch")
    print("3. Chrome browser not installed")

    print("\n[SOLUTION]")
    print("Please run: python download_chromedriver.py")
    print("Or manually download ChromeDriver from:")
    print("https://googlechromelabs.github.io/chrome-for-testing/")
    print("\nDetailed guide: ChromeDriver安装指南.md")
