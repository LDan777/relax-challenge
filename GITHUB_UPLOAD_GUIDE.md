# Aurora520 项目 GitHub 上传指南

## 📋 文件清理清单

### ✅ 需要保留的文件/文件夹

```
Aurora520project/
├── aurora_server.py              ⭐ 核心后端服务
├── relax_challenge.py            ⭐ 核心算法控制台
├── main_app.py                   ⭐ 聚合启动脚本
├── BLE_relax/                    ⭐ 蓝牙模块
│   ├── BLE_relax0.py
│   └── main_test_relax.py
├── relax_frontend/               ⭐ 前端项目
│   ├── src/
│   ├── public/
│   ├── package.json
│   ├── package-lock.json
│   ├── vite.config.js
│   └── index.html
├── README.md                     ⭐ 项目说明
├── README_EXE.md                 ⭐ EXE 使用说明
├── .gitignore                    ⭐ Git 忽略文件
└── requirements.txt              ⭐ Python 依赖
```

### ❌ 需要删除的文件/文件夹

```
Aurora520project/
├── build/                        ❌ PyInstaller 构建目录（本地生成）
├── dist/                         ❌ PyInstaller 输出目录（本地生成）
├── main_app.spec                 ❌ PyInstaller 配置（本地生成）
├── 基线采集问题修复说明.md        ❌ 临时文档
├── 快速测试.py                   ❌ 临时测试文件
├── 启动指南.md                   ❌ 临时文档
├── 项目完整说明文档.md           ❌ 临时文档
├── main_test.py                  ❌ 临时测试文件
└── relax_frontend/
    ├── dist/                     ❌ 前端编译输出（本地生成）
    ├── node_modules/             ❌ npm 依赖（本地生成）
    └── .venv/                    ❌ Python 虚拟环境（本地生成）
```

---

## 🚀 上传步骤

### 第一步：本地清理

在 Aurora520project 目录下执行以下命令删除不必要的文件：

```bash
# Windows (PowerShell)
Remove-Item -Recurse -Force build
Remove-Item -Recurse -Force dist
Remove-Item -Recurse -Force relax_frontend\dist
Remove-Item -Recurse -Force relax_frontend\node_modules
Remove-Item main_app.spec
Remove-Item "基线采集问题修复说明.md"
Remove-Item "快速测试.py"
Remove-Item "启动指南.md"
Remove-Item "项目完整说明文档.md"
Remove-Item main_test.py
```

```bash
# Linux/Mac
rm -rf build dist relax_frontend/dist relax_frontend/node_modules
rm main_app.spec "基线采集问题修复说明.md" "快速测试.py" "启动指南.md" "项目完整说明文档.md" main_test.py
```

### 第二步：创建 .gitignore 文件

在 Aurora520project 目录下创建 `.gitignore` 文件（已自动生成）

### 第三步：创建 requirements.txt

在 Aurora520project 目录下创建 `requirements.txt`：

```bash
pip freeze > requirements.txt
```

或手动创建包含以下内容：

```
websockets>=12.0
asyncio>=3.4.3
```

### 第四步：初始化 Git 仓库

```bash
cd Aurora520project
git init
git add .
git commit -m "Initial commit: Aurora520 放松挑战应用"
```

### 第五步：添加远程仓库

```bash
# 替换 YOUR_USERNAME 和 YOUR_REPO_NAME
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git branch -M main
git push -u origin main
```

### 第六步：验证上传

访问 GitHub 仓库检查文件是否正确上传

---

## 📁 最终项目结构

上传后的 GitHub 仓库应该看起来像这样：

```
Aurora520/
├── .gitignore
├── README.md
├── README_EXE.md
├── GITHUB_UPLOAD_GUIDE.md
├── requirements.txt
├── aurora_server.py
├── relax_challenge.py
├── main_app.py
├── BLE_relax/
│   ├── BLE_relax0.py
│   └── main_test_relax.py
└── relax_frontend/
    ├── src/
    │   ├── App.vue
    │   ├── main.js
    │   └── components/
    │       └── EchartsWave.vue
    ├── public/
    ├── index.html
    ├── package.json
    ├── package-lock.json
    └── vite.config.js
```

---

## 📝 README.md 建议内容

```markdown
# Aurora520 - 极速放松挑战应用

基于脑电波（EEG）的放松挑战应用，通过实时监测用户的放松指数（RELAX Index），帮助用户进入放松状态。

## 功能特性

- 🧠 实时脑电波数据采集与处理
- 📊 动态波形图显示
- 🎯 自适应阈值计算
- 🔌 支持真实蓝牙设备和模拟模式
- 💡 一键启动，无需复杂配置

## 快速开始

### 方式一：运行 EXE（推荐）

1. 下载最新的 EXE 文件
2. 双击运行
3. 选择模式（仿真/蓝牙）
4. 开始挑战

### 方式二：开发模式

```bash
# 安装依赖
pip install -r requirements.txt
cd relax_frontend && npm install

# 启动服务
python aurora_server.py
python relax_challenge.py
cd relax_frontend && npm run dev
```

## 系统要求

- Python 3.8+
- Node.js 14+
- 现代浏览器（Chrome、Firefox、Safari）

## 项目结构

- `aurora_server.py` - 数据源服务
- `relax_challenge.py` - 算法控制台
- `main_app.py` - 聚合启动脚本
- `relax_frontend/` - Vue 前端项目
- `BLE_relax/` - 蓝牙模块

## 详细文档

- [EXE 使用说明](README_EXE.md)
- [GitHub 上传指南](GITHUB_UPLOAD_GUIDE.md)

## 许可证

MIT License

## 作者

[Your Name]
```

---

## 🔍 检查清单

上传前请确认：

- [ ] 已删除 `build/` 目录
- [ ] 已删除 `dist/` 目录
- [ ] 已删除 `relax_frontend/dist/` 目录
- [ ] 已删除 `relax_frontend/node_modules/` 目录
- [ ] 已删除 `main_app.spec` 文件
- [ ] 已删除所有临时文档文件
- [ ] 已创建 `.gitignore` 文件
- [ ] 已创建 `requirements.txt` 文件
- [ ] 已创建或更新 `README.md` 文件
- [ ] 所有核心代码文件都在项目根目录
- [ ] `relax_frontend/` 目录包含所有源代码

---

## 💡 后续维护

### 更新依赖

```bash
pip freeze > requirements.txt
```

### 前端依赖

```bash
cd relax_frontend
npm install
```

### 生成新的 EXE

```bash
pip install pyinstaller
pyinstaller --noconfirm --onedir --console --add-data "relax_frontend/dist;relax_frontend/dist" --add-data "BLE_relax;BLE_relax" main_app.py
```

---

## 📞 常见问题

**Q: 为什么要删除 node_modules？**
A: node_modules 很大（通常 200MB+），GitHub 有文件大小限制。用户可以通过 `npm install` 重新安装。

**Q: 为什么要删除 dist 目录？**
A: dist 是编译输出，可以通过 `npm run build` 重新生成。

**Q: 为什么要删除 build 和 dist（PyInstaller）？**
A: 这些是本地构建输出，用户可以自己运行 PyInstaller 生成。

**Q: .gitignore 有什么作用？**
A: 防止 Git 追踪不必要的文件（如 node_modules、虚拟环境等）。

---

**准备好了吗？按照上面的步骤上传到 GitHub 吧！🚀**
