# -*- coding: utf-8 -*-
import asyncio
import json
import math
import random
import time
from websockets import serve

# ==================== 配置项 ====================
MOCK_MODE = True  # True: 模拟测试模式 | False: 真实蓝牙连接模式
PORT = 8765       # WebSocket 服务器端口
CONTROL_PORT = 8766  # 控制端口

# 保存所有连接到后端的网页客户端
relax_clients = set()

# 蓝牙监听线程
ble_thread = None
mock_task = None
main_loop = None

# ==================== 数据广播核心 ====================
async def _send_to_all(clients, message):
    """ 真正执行异步分发的协程函数 """
    if clients:
        await asyncio.gather(*(client.send(message) for client in clients), return_exceptions=True)

def broadcast_relax_index(relax_value):
    """ 广播 RELAX 指数给所有连接的客户端 """
    payload = {
        "relax_index": relax_value,
        "timestamp": time.time()
    }
    message = json.dumps(payload)
    
    if relax_clients and main_loop:
        asyncio.run_coroutine_threadsafe(_send_to_all(relax_clients, message), main_loop)

# ==================== 蓝牙接收回调 ====================
def bluetooth_handler(msg):
    """
    接收来自主控的 RELAX 指数数据
    格式: "RELAX:0.95" (每秒发一次)
    """
    try:
        if msg.startswith('RELAX:'):
            relax_value = float(msg.split(':')[1])
            broadcast_relax_index(relax_value)
        else:
            print(f"[蓝牙数据异常] 未知格式: {msg}")
    except (ValueError, IndexError) as e:
        print(f"[蓝牙数据异常] 解析失败: {e}")

# ==================== 仿真模拟器 ====================
async def mock_eeg_generator():
    print(" [仿真提示] 当前处于模拟模式，正在生成虚拟 RELAX 指数数据...")
    print("    模拟数据范围：0.6 ~ 1.2（会有波动）")
    print("    更新频率：每秒一次\n")
    
    base_value = 0.8
    time_counter = 0
    
    while MOCK_MODE:
        sine_wave = 0.2 * math.sin(2 * math.pi * time_counter / 10)
        noise = random.uniform(-0.1, 0.1)
        mock_relax_value = base_value + sine_wave + noise
        mock_relax_value = max(0.5, min(1.5, mock_relax_value))
        
        broadcast_relax_index(mock_relax_value)
        print(f"[模拟数据] RELAX指数: {mock_relax_value:.4f}")
        
        await asyncio.sleep(1)
        time_counter += 1

# ==================== WebSocket 路由 ====================
async def connection_router(websocket, path=None):
    try:
        current_path = websocket.request.path
    except:
        current_path = path if path else getattr(websocket, 'path', '')
    
    print(f"[DEBUG] 收到连接请求，path={current_path}")
    
    if "/relax" in current_path:
        relax_clients.add(websocket)
        print(f" [OK] 连接成功：放松挑战数据源已上线 ({websocket.remote_address})")
        print(f"    当前 relax_clients 数量: {len(relax_clients)}")
        try:
            await websocket.wait_closed()
        finally:
            relax_clients.discard(websocket)
            print(f" [CLOSE] 断开连接：放松挑战数据源已下线 ({websocket.remote_address})")
    else:
        print(f"[警告] 未知路由: {current_path}，关闭连接")
        await websocket.close(reason="未知路由")

async def control_router(websocket, path=None):
    """ 处理模式切换控制信号 """
    global MOCK_MODE, mock_task, ble_thread
    
    print(f"[控制] 收到控制连接 ({websocket.remote_address})")
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                mode = data.get("mode")
                
                if mode == "mock":
                    print("💡 [控制] 切换为仿真模拟模式")
                    MOCK_MODE = True
                    if mock_task is None or mock_task.done():
                        mock_task = asyncio.create_task(mock_eeg_generator())
                    
                elif mode == "ble":
                    print("🔌 [控制] 切换为真实蓝牙模式")
                    MOCK_MODE = False
                    if mock_task and not mock_task.done():
                        mock_task.cancel()
                    
                    # 启动蓝牙监听
                    if ble_thread is None or not ble_thread.is_alive():
                        try:
                            from BLE_relax.BLE_relax0 import start
                            import threading
                            ble_thread = threading.Thread(target=start, args=(bluetooth_handler,), daemon=True)
                            ble_thread.start()
                            print("✅ 蓝牙监听已启动")
                        except ImportError as e:
                            print(f"❌ 蓝牙模块导入失败: {e}")
                            MOCK_MODE = True  # 回退到模拟模式
                
            except json.JSONDecodeError:
                pass
    except asyncio.CancelledError:
        pass
    except Exception as e:
        print(f"[控制] 错误: {e}")
    finally:
        print(f"[控制] 连接已关闭 ({websocket.remote_address})")

# ==================== 主程序启动 ====================
async def start_server():
    global main_loop, mock_task, MOCK_MODE, ble_thread
    main_loop = asyncio.get_running_loop()
    
    # 启动数据服务
    server = await serve(connection_router, "localhost", PORT)
    print(f"=== Aurora 统一后端服务器已启动 (端口: {PORT}) ===")
    print(f"-> 放松挑战数据源: ws://localhost:{PORT}/relax\n")
    
    # 启动控制服务
    control_server = await serve(control_router, "localhost", CONTROL_PORT)
    print(f"=== 控制服务已启动 (端口: {CONTROL_PORT}) ===\n")
    
    # 启动初始数据生成器
    if MOCK_MODE:
        print(" [仿真提示] 当前处于模拟模式，正在生成虚拟脑电数据...")
        mock_task = asyncio.create_task(mock_eeg_generator())
    else:
        print(" [蓝牙提示] 正在启动真实蓝牙监听...")
        try:
            from BLE_relax.BLE_relax0 import start
            import threading
            ble_thread = threading.Thread(target=start, args=(bluetooth_handler,), daemon=True)
            ble_thread.start()
        except ImportError as e:
            print(f"[ERROR] 蓝牙模块导入失败: {e}")
            print("   回退到模拟模式")
            MOCK_MODE = True
            mock_task = asyncio.create_task(mock_eeg_generator())
    
    await asyncio.gather(server.wait_closed(), control_server.wait_closed())

if __name__ == "__main__":
    try:
        asyncio.run(start_server())
    except KeyboardInterrupt:
        print("\n服务器已手动关闭。")
