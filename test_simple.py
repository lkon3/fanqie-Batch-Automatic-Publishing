# -*- coding: utf-8 -*-
"""
简化的浏览器测试
不使用 user-data-dir，避免配置冲突
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

print("=" * 50)
print("简单浏览器测试")
print("=" * 50)

# 测试 1: 最简单的启动方式
print("\n[测试 1] 最简单的启动方式...")
try:
    driver = webdriver.Chrome()
    print("✓ 浏览器启动成功！")
    print("正在打开百度...")
    driver.get("https://www.baidu.com")
    print("✓ 已打开百度")
    print("\n如果能看到浏览器窗口，说明基础环境正常！")
    input("按回车键关闭浏览器...")
    driver.quit()
    print("✓ 浏览器已关闭")
    success = True
except Exception as e:
    print(f"✗ 失败: {e}")
    success = False

if success:
    print("\n" + "=" * 50)
    print("✓ 测试成功！")
    print("=" * 50)
    print("\n问题原因：user-data-dir 配置导致冲突")
    print("解决方案：删除 chrome_profile 目录")
    print("\n请执行以下命令：")
    print("  rmdir /s /q chrome_profile")
    print("  python main.py")
else:
    print("\n" + "=" * 50)
    print("✗ 测试失败")
    print("=" * 50)
    print("\n可能的问题：")
    print("1. Chrome 浏览器版本太旧")
    print("2. ChromeDriver 版本不匹配")
    print("3. Chrome 进程残留")
    print("\n建议操作：")
    print("1. 更新 Chrome 浏览器到最新版本")
    print("2. 重启电脑")
    print("3. 检查任务管理器，关闭所有 chrome.exe 进程")
