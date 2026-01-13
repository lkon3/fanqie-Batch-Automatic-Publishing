# ChromeDriver 安装指南

如果程序运行时出现 `WinError 193` 或 `ChromeDriver not found` 等错误，请按以下步骤安装 ChromeDriver。

## 方法 1: 自动安装（推荐）

程序会自动尝试下载 ChromeDriver，如果失败请使用方法 2。

## 方法 2: 手动安装

### 步骤 1: 查看 Chrome 版本

1. 打开 Chrome 浏览器
2. 在地址栏输入: `chrome://version/`
3. 记下版本号（如: 120.0.6099.109）

### 步骤 2: 下载 ChromeDriver

访问 ChromeDriver 下载页面:
```
https://googlechromelabs.github.io/chrome-for-testing/
```

或者使用旧版本下载页面（如果上面打不开）:
```
https://chromedriver.chromium.org/downloads
```

选择与您的 Chrome 版本对应的 ChromeDriver 版本。

### 步骤 3: 选择正确的版本

**重要**: 根据您的系统选择:
- Windows 64位: 选择 `win64` 版本
- Windows 32位: 选择 `win32` 版本

大多数现代电脑都是 64 位系统。

### 步骤 4: 安装

有三种安装方式：

#### 方式 A: 放到项目目录（最简单）

1. 下载的文件通常是压缩包（.zip）
2. 解压得到 `chromedriver.exe`
3. 将 `chromedriver.exe` 复制到项目目录:
   ```
   C:\Users\1\Desktop\番茄自动发布\chromedriver.exe
   ```

#### 方式 B: 添加到系统 PATH

1. 将 `chromedriver.exe` 放到一个固定位置，如:
   ```
   C:\Tools\chromedriver.exe
   ```

2. 添加到系统 PATH:
   - 右键"此电脑" → "属性"
   - "高级系统设置" → "环境变量"
   - 在"系统变量"中找到 `Path`
   - 点击"编辑" → "新建"
   - 添加: `C:\Tools`
   - 点击"确定"保存

3. 重新打开命令行窗口

#### 方式 C: 放到 Python 目录

将 `chromedriver.exe` 复制到 Python 的 Scripts 目录:
```
C:\Users\1\AppData\Local\Programs\Python\Python311\Scripts\chromedriver.exe
```

### 步骤 5: 验证安装

打开命令行，输入:
```bash
chromedriver --version
```

如果显示版本号，说明安装成功。

### 步骤 6: 测试程序

```bash
python main.py
```

选择 `3. 测试登录`，应该能正常启动浏览器了。

## 常见问题

### Q: 下载的 ChromeDriver 版本和 Chrome 不匹配怎么办？

A: ChromeDriver 版本不需要完全匹配，主要版本号相同即可。例如:
- Chrome 120.x.x.x 可以使用 ChromeDriver 120.x.x.x

### Q: 下载后还是提示找不到 ChromeDriver？

A:
1. 确认文件名是 `chromedriver.exe`（不是 `chromedriver.exe.txt`）
2. 确认放到了正确的目录
3. 尝试重启命令行窗口
4. 尝试方式 A（直接放到项目目录）

### Q: 提示 "不是有效的 Win32 应用程序"？

A:
- 确认下载的是 Windows 版本（win64 或 win32）
- 确认您的系统是 64 位还是 32 位
- 如果是 64 位系统但下载了 32 位，也会报这个错

### Q: Windows Defender 警告？

A:
- Windows Defender 可能会误报 ChromeDriver 为病毒
- 这是正常的安全软件误报
- 在 Windows Defender 中允许该文件即可

## 快速测试

创建一个测试文件 `test_browser.py`:

```python
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument('--user-data-dir=./chrome_profile')

try:
    # 尝试自动查找 ChromeDriver
    driver = webdriver.Chrome(options=options)
    print("✓ 浏览器启动成功！")
    driver.get("https://www.baidu.com")
    print("✓ 已打开百度")
    input("按回车关闭浏览器...")
    driver.quit()
except Exception as e:
    print(f"✗ 失败: {e}")
```

运行测试:
```bash
python test_browser.py
```

## 需要帮助？

如果仍然无法解决，请提供以下信息:
1. Windows 版本（Win10/Win11）
2. Chrome 浏览器版本
3. 下载的 ChromeDriver 版本
4. 完整的错误信息
