# Aurora520 EXE 打包指南

## 概述

本指南说明如何将 Aurora520 应用打包成 Windows EXE 可执行文件。

---

## 前置要求

### 1. 安装必要的工具

```bash
# 安装 PyInstaller
pip install pyinstaller

# 确保已安装 Node.js 和 npm
node --version
npm --version
```

### 2. 确保项目结构完整

```
Aurora520project/
├── aurora_server.py          # 必须存在
├── relax_challenge.py        # 必须存在
├── main_app.py               # 必须存在
├── build_exe.py              # 打包脚本
├── BLE_relax/                # 蓝牙模块
└── relax_frontend/           # 前端项目
    ├── src/
    ├── package.json
    └── vite.config.js
```

---

## 打包步骤

### 方法一：使用打包脚本（推荐）

最简单的方式，一键完成所有步骤：

```bash
cd Aurora520project
python build_exe.py
```

脚本会自动：
1. 清理旧的构建文件
2. 编译前端（npm run build）
3. 使用 PyInstaller 打包
4. 生成 EXE 文件

### 方法二：手动打包

如果脚本出现问题，可以手动执行以下步骤：

#### 步骤 1：编译前端

```bash
cd relax_frontend
npm install
npm run build
cd ..
```

#### 步骤 2：运行 PyInstaller

```bash
pyinstaller --noconfirm --onedir --console --name main_app ^
  --add-data "relax_frontend/dist;relax_frontend/dist" ^
  --add-data "BLE_relax;BLE_relax" ^
  --add-data "aurora_server.py;." ^
  --add-data "relax_challenge.py;." ^
  main_app.py
```

**注意**：
- Windows 命令行中使用 `^` 作为行继续符
- PowerShell 中使用 `` ` `` 作为行继续符

---

## 生成的文件

打包完成后，会生成以下文件结构：

```
Aurora520project/
├── dist/
│   └── main_app/
│       ├── main_app.exe          # 主程序（双击运行）
│       ├── _internal/            # 依赖库
│       ├── relax_frontend/       # 前端文件
│       ├── BLE_relax/            # 蓝牙模块
│       ├── aurora_server.py
│       └── relax_challenge.py
├── build/                        # 构建临时文件（可删除）
└── main_app.spec                 # PyInstaller 配置文件
```

---

## 运行 EXE

### 方式 1：双击运行

直接双击 `dist/main_app/main_app.exe` 文件

### 方式 2：命令行运行

```bash
dist/main_app/main_app.exe
```

### 预期输出

```
============================================================
Aurora520 极速放松挑战应用
============================================================

[步骤 1/3] 启动前端服务...
[前端服务] 前端服务已启动 (http://localhost:5173)

[步骤 2/3] 打开浏览器...
浏览器已打开: http://localhost:5173

[步骤 3/3] 启动后端服务...
=== Aurora 统一后端服务器已启动 (端口: 8765) ===
=== 算法控制台已就绪 (Port: 8888)，等待 Vue 前端连接...
```

---

## 常见问题

### Q: 打包失败，提示找不到模块

**A:** 确保：
1. 所有 Python 依赖已安装：`pip install -r requirements.txt`
2. 前端已编译：`cd relax_frontend && npm run build`
3. 项目根目录正确

### Q: EXE 运行后没有反应

**A:** 
1. 检查命令行窗口是否有错误信息
2. 确保端口 5173、8765、8888 未被占用
3. 查看 `relax_frontend/dist` 目录是否存在

### Q: 前端页面显示空白

**A:**
1. 检查浏览器控制台（F12）是否有错误
2. 确保后端服务已启动
3. 尝试刷新页面

### Q: 如何减小 EXE 文件大小

**A:** 可以在 PyInstaller 命令中添加 `--onefile` 参数生成单个 EXE 文件（但启动速度会变慢）

```bash
pyinstaller --onefile --console --name main_app main_app.py
```

### Q: 如何在其他电脑上运行 EXE

**A:** 
1. 只需复制 `dist/main_app` 整个文件夹
2. 在目标电脑上双击 `main_app.exe` 即可
3. 无需安装 Python 或其他依赖

---

## 打包优化建议

### 1. 减少依赖

在 `requirements.txt` 中只保留必要的包：
- websockets
- asyncio（Python 内置）

### 2. 使用 UPX 压缩

安装 UPX 后，PyInstaller 会自动压缩 EXE：

```bash
# 下载 UPX：https://upx.github.io/
# 解压后添加到 PATH
pyinstaller --upx-dir=path/to/upx main_app.py
```

### 3. 隐藏控制台窗口

如果不需要显示控制台，将 `--console` 改为 `--windowed`：

```bash
pyinstaller --windowed --name main_app main_app.py
```

---

## 故障排除

### 问题：PyInstaller 找不到模块

```
ModuleNotFoundError: No module named 'xxx'
```

**解决方案**：
```bash
# 使用 --hidden-import 参数
pyinstaller --hidden-import=xxx main_app.py
```

### 问题：前端文件未被打包

**解决方案**：
1. 确保 `relax_frontend/dist` 目录存在
2. 检查 `--add-data` 参数中的路径是否正确
3. 使用绝对路径而不是相对路径

### 问题：蓝牙模块导入失败

**解决方案**：
1. 确保 `BLE_relax` 目录存在
2. 检查 `--add-data` 参数中的路径
3. 在 `aurora_server.py` 中添加错误处理

---

## 发布 EXE

### 1. 创建安装程序（可选）

使用 NSIS 或 Inno Setup 创建安装程序：
- NSIS：https://nsis.sourceforge.io/
- Inno Setup：https://jrsoftware.org/isinfo.php

### 2. 上传到 GitHub Release

```bash
# 创建 Release
gh release create v3.0 dist/main_app/main_app.exe

# 或手动上传到 GitHub
```

### 3. 创建便携版本

直接压缩 `dist/main_app` 文件夹：

```bash
# Windows
tar -czf Aurora520-v3.0-portable.tar.gz dist/main_app

# 或使用 7-Zip
7z a Aurora520-v3.0-portable.7z dist/main_app
```

---

## 更新 EXE

每次修改代码后，重新运行打包脚本：

```bash
python build_exe.py
```

新的 EXE 文件会覆盖旧的版本。

---

## 技术细节

### main_app.py 的工作流程

1. **启动前端服务**
   - 检查 `relax_frontend/dist` 是否存在
   - 启动 HTTP 服务器（端口 5173）
   - 提供静态文件服务

2. **打开浏览器**
   - 自动打开 `http://localhost:5173`
   - 如果失败，提示用户手动访问

3. **启动后端服务**
   - 导入 `aurora_server.py`
   - 导入 `relax_challenge.py`
   - 并发运行两个异步服务

### PyInstaller 参数说明

| 参数 | 说明 |
|------|------|
| `--noconfirm` | 不询问，直接覆盖 |
| `--onedir` | 生成目录（包含依赖） |
| `--console` | 显示控制台窗口 |
| `--name` | 指定输出名称 |
| `--add-data` | 添加数据文件 |
| `--hidden-import` | 隐式导入模块 |

---

## 相关文档

- [README.md](./README.md) - 项目说明
- [GITHUB_UPLOAD_GUIDE.md](./GITHUB_UPLOAD_GUIDE.md) - GitHub 上传指南
- [PyInstaller 官方文档](https://pyinstaller.org/)

---

**祝您打包顺利！** 🚀
