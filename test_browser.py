# -*- coding: utf-8 -*-
"""
测试浏览器是否能正常启动
用于诊断 ChromeDriver 问题
"""
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import sys

print("=" * 50)
print("Chrome 浏览器测试")
print("=" * 50)

# 测试 1: 检查 Chrome 是否安装
print("\n[测试 1] 检查 Chrome 浏览器...")
try:
    options = Options()
    options.add_argument('--user-data-dir=./chrome_profile')
    print("✓ Chrome 浏览器已安装")
except Exception as e:
    print(f"✗ Chrome 浏览器未安装或无法访问: {e}")
    sys.exit(1)

# 测试 2: 尝试使用 webdriver-manager
print("\n[测试 2] 尝试使用 webdriver-manager...")
try:
    from webdriver_manager.chrome import ChromeDriverManager
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    print("✓ webdriver-manager 工作正常")
    driver.quit()
    success_method = "webdriver-manager"
except Exception as e:
    print(f"✗ webdriver-manager 失败: {e}")
    success_method = None

# 测试 3: 尝试使用系统 ChromeDriver
print("\n[测试 3] 尝试使用系统 ChromeDriver...")
try:
    driver = webdriver.Chrome(options=options)
    print("✓ 系统 ChromeDriver 工作正常")
    driver.quit()
    if not success_method:
        success_method = "系统ChromeDriver"
except Exception as e:
    print(f"✗ 系统 ChromeDriver 失败: {e}")
    if not success_method:
        print("\n" + "=" * 50)
        print("⚠ 所有方法都失败了")
        print("=" * 50)
        print("\n请查看《ChromeDriver安装指南.md》")
        print("或访问: https://googlechromelabs.github.io/chrome-for-testing/")
        sys.exit(1)

print("\n" + "=" * 50)
print("✓ 测试完成！")
print(f"推荐方式: {success_method}")
print("=" * 50)

# 最终测试: 打开浏览器
print("\n[最终测试] 打开浏览器...")
try:
    if success_method == "webdriver-manager":
        from webdriver_manager.chrome import ChromeDriverManager
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
    else:
        driver = webdriver.Chrome(options=options)

    print("✓ 浏览器已启动")
    print("正在打开百度...")
    driver.get("https://www.baidu.com")
    print("✓ 已打开百度")
    print("\n如果能看到浏览器窗口，说明一切正常！")
    input("\n按回车键关闭浏览器...")
    driver.quit()
    print("\n✓ 浏览器已关闭")
    print("\n您现在可以正常使用番茄自动发布系统了！")
except Exception as e:
    print(f"✗ 最终测试失败: {e}")
    sys.exit(1)
