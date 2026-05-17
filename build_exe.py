# -*- coding: utf-8 -*-
"""
Aurora520 EXE 打包脚本
使用 PyInstaller 将应用打包成单个 EXE 文件
"""

import os
import sys
import shutil
from pathlib import Path

def remove_directory(path, max_retries=3):
    """安全删除目录，处理文件被占用的情况"""
    import time
    for attempt in range(max_retries):
        try:
            if path.exists():
                shutil.rmtree(path)
                return True
        except PermissionError:
            if attempt < max_retries - 1:
                print(f"⚠️ 目录被占用，等待 2 秒后重试... ({attempt + 1}/{max_retries})")
                time.sleep(2)
            else:
                print(f"❌ 无法删除目录: {path}")
                print("   请确保 EXE 文件未在运行，然后重试")
                return False
    return True

def build_exe():
    """构建 EXE 文件"""
    
    project_root = Path(__file__).parent
    dist_dir = project_root / "dist"
    build_dir = project_root / "build"
    
    print("=" * 60)
    print("[1/4] 清理旧的构建文件...")
    print("=" * 60)
    
    # 删除旧的 dist 和 build 目录
    if not remove_directory(dist_dir):
        return False
    
    if not remove_directory(build_dir):
        return False
    
    print("✅ 旧文件已清理")
    
    print("\n" + "=" * 60)
    print("[2/4] 编译前端...")
    print("=" * 60)
    
    # 编译前端
    frontend_dir = project_root / "relax_frontend"
    os.chdir(frontend_dir)
    
    result = os.system("npm run build")
    if result != 0:
        print("❌ 前端编译失败")
        return False
    
    print("✅ 前端编译成功")
    
    print("\n" + "=" * 60)
    print("[3/4] 准备 PyInstaller 打包...")
    print("=" * 60)
    
    os.chdir(project_root)
    
    # PyInstaller 命令
    pyinstaller_cmd = (
        "pyinstaller "
        "--noconfirm "
        "--onedir "
        "--console "
        "--name main_app "
        f"--add-data \"relax_frontend/dist;relax_frontend/dist\" "
        f"--add-data \"BLE_relax;BLE_relax\" "
        f"--add-data \"aurora_server.py;.\" "
        f"--add-data \"relax_challenge.py;.\" "
        "main_app.py"
    )
    
    print(f"执行命令: {pyinstaller_cmd}\n")
    result = os.system(pyinstaller_cmd)
    
    if result != 0:
        print("❌ PyInstaller 打包失败")
        return False
    
    print("\n" + "=" * 60)
    print("[4/4] 打包完成")
    print("=" * 60)
    
    exe_path = dist_dir / "main_app" / "main_app.exe"
    if exe_path.exists():
        print(f"✅ EXE 文件已生成: {exe_path}")
        print(f"\n使用方法:")
        print(f"  双击运行: {exe_path}")
        print(f"  或在命令行运行: {exe_path}")
        return True
    else:
        print(f"❌ EXE 文件未找到: {exe_path}")
        return False

if __name__ == "__main__":
    try:
        success = build_exe()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ 打包过程出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
