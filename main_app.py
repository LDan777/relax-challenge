# -*- coding: utf-8 -*-
"""
Aurora520 放松挑战应用 - 聚合启动脚本
一键启动所有服务：aurora_server.py、relax_challenge.py、前端静态服务
"""

import asyncio
import os
import sys
import webbrowser
import threading
import time
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler

# ==================== 配置 ====================
FRONTEND_PORT = 5173
AURORA_SERVER_PORT = 8765
RELAX_CHALLENGE_PORT = 8888

# 获取项目根目录
PROJECT_ROOT = Path(__file__).parent
DIST_DIR = PROJECT_ROOT / "relax_frontend" / "dist"

# ==================== 前端静态服务器 ====================
class CORSRequestHandler(SimpleHTTPRequestHandler):
    """支持 CORS 的 HTTP 请求处理器"""
    
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()
    
    def log_message(self, format, *args):
        """简化日志输出"""
        print(f"[前端服务] {format % args}")

def start_frontend_server():
    """启动前端静态文件服务器"""
    # 检查 dist 目录是否存在
    if not DIST_DIR.exists():
        print(f"❌ 前端编译目录不存在: {DIST_DIR}")
        print("   请先执行: cd relax_frontend && npm run build")
        return False
    
    # 切换到 dist 目录
    os.chdir(DIST_DIR)
    
    # 创建 HTTP 服务器
    server = HTTPServer(('localhost', FRONTEND_PORT), CORSRequestHandler)
    print(f"✅ 前端服务已启动 (http://localhost:{FRONTEND_PORT})")
    
    # 在新线程中运行服务器
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    
    return True

# ==================== 后端服务启动 ====================
async def start_backend_services():
    """启动 aurora_server 和 relax_challenge"""
    
    # 导入后端模块
    sys.path.insert(0, str(PROJECT_ROOT))
    
    try:
        # 导入 aurora_server
        import aurora_server
        
        # 启动 aurora_server
        print("🚀 正在启动 Aurora 数据服务...")
        aurora_task = asyncio.create_task(aurora_server.start_server())
        
        # 等待一秒让 aurora_server 启动
        await asyncio.sleep(1)
        
        # 导入 relax_challenge
        import relax_challenge
        
        # 启动 relax_challenge
        print("🚀 正在启动算法控制台...")
        relax_task = asyncio.create_task(relax_challenge.main())
        
        # 等待两个服务
        await asyncio.gather(aurora_task, relax_task)
        
    except Exception as e:
        print(f"❌ 后端服务启动失败: {e}")
        import traceback
        traceback.print_exc()

# ==================== 主程序 ====================
def main():
    print("=" * 60)
    print("🎉 Aurora520 极速放松挑战应用")
    print("=" * 60)
    
    # 1. 启动前端静态服务
    print("\n[步骤 1/3] 启动前端服务...")
    if not start_frontend_server():
        print("❌ 前端服务启动失败，请检查 dist 目录")
        return
    
    # 2. 等待一秒
    time.sleep(1)
    
    # 3. 打开浏览器
    print("\n[步骤 2/3] 打开浏览器...")
    try:
        webbrowser.open(f'http://localhost:{FRONTEND_PORT}')
        print(f"✅ 浏览器已打开: http://localhost:{FRONTEND_PORT}")
    except Exception as e:
        print(f"⚠️ 无法自动打开浏览器: {e}")
        print(f"   请手动访问: http://localhost:{FRONTEND_PORT}")
    
    # 4. 启动后端服务
    print("\n[步骤 3/3] 启动后端服务...")
    try:
        asyncio.run(start_backend_services())
    except KeyboardInterrupt:
        print("\n\n👋 应用已关闭")
    except Exception as e:
        print(f"❌ 应用运行出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
