# -*- coding: utf-8 -*-
"""
测试本地 chromedriver.exe
"""
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import os

print("=" * 50)
print("Testing Local ChromeDriver")
print("=" * 50)

# 检查 chromedriver.exe 是否存在
chromedriver_path = os.path.join(os.getcwd(), "chromedriver.exe")

print(f"\nCurrent directory: {os.getcwd()}")
print(f"ChromeDriver path: {chromedriver_path}")
print(f"File exists: {os.path.exists(chromedriver_path)}")

if os.path.exists(chromedriver_path):
    file_size = os.path.getsize(chromedriver_path)
    print(f"File size: {file_size} bytes ({file_size/1024/1024:.2f} MB)")
else:
    print("\n[ERROR] chromedriver.exe NOT found!")
    print("Please download chromedriver.exe and put it in this directory.")
    exit(1)

print("\n[Test] Starting Chrome with local chromedriver...")

try:
    # 明确指定使用本地的 chromedriver.exe
    service = Service(executable_path=chromedriver_path)
    driver = webdriver.Chrome(service=service)

    print("[OK] Browser started!")
    print("Opening Baidu...")
    driver.get("https://www.baidu.com")
    print("[OK] Baidu opened!")
    print("\n" + "=" * 50)
    print("SUCCESS!")
    print("=" * 50)
    print("\nYour ChromeDriver is working perfectly!")
    print("You can now run: python main.py")

    input("\nPress Enter to close browser...")
    driver.quit()
    print("[OK] Browser closed")

except Exception as e:
    print(f"\n[ERROR] {e}")
    print("\n" + "=" * 50)
    print("FAILED")
    print("=" * 50)

    if "driver" in str(e).lower() or "chromedriver" in str(e).lower():
        print("\nChromeDriver issue detected!")
        print("\nPossible solutions:")
        print("1. ChromeDriver version doesn't match Chrome version")
        print("2. ChromeDriver is corrupted")
        print("3. Antivirus blocked ChromeDriver")
        print("\nPlease check your Chrome version and download matching ChromeDriver")
    else:
        print("\nSelenium or Chrome issue")
        print("Try updating: pip install -U selenium")
