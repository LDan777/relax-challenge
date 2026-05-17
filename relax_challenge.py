import asyncio
import json
import time
import websockets
from websockets.server import serve

# ==================== 1. 挑战配置 ====================
BASELINE_DURATION = 10.0          # 基线采集时长（秒）
THRESHOLD_BOOST = 1.15            # 阈值提升系数（基线 × 1.15）
REQUIRED_HOLD_TIME = 4.0          # 需要保持的时长（秒）
CHALLENGE_TIMEOUT = 120.0         # 挑战超时时长（秒）

# ==================== 2. 挑战状态机变量 ====================
baseline_data = []
baseline_value = None
target_threshold = None

start_time = None
challenge_start_time = None
above_threshold_start = None
challenge_ended = False
challenge_started = False  # 标记是否已经开始挑战

# 存放连接进来的 Vue 前端网页客户端
frontend_clients = set()
current_status_string = "idle"    # idle, baseline, challenging, success, failed
use_time = 0

# ==================== 3. 核心算法与网页广播 ====================
def broadcast_to_frontend(relax_index):
    """
    把当前算法算出的所有状态，打包成 JSON 秒级同步给 Vue 网页
    """
    global current_status_string, target_threshold, use_time
    if not frontend_clients:
        return
        
    payload = {
        "relax_index": relax_index,
        "threshold": target_threshold,
        "status": current_status_string,
        "useTime": round(use_time, 2)
    }
    message = json.dumps(payload)
    
    # 广播给连上 8888 端口的 Vue 网页
    async def send_all():
        tasks = [client.send(message) for client in frontend_clients]
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    asyncio.run_coroutine_threadsafe(send_all(), main_loop)

def reset_challenge_state():
    """ 重置所有挑战状态变量 """
    global baseline_data, baseline_value, target_threshold, start_time, challenge_start_time, above_threshold_start, challenge_ended, current_status_string, use_time, challenge_started
    baseline_data = []
    baseline_value = None
    target_threshold = None
    start_time = None
    challenge_start_time = None
    above_threshold_start = None
    challenge_ended = False
    challenge_started = True  # 标记挑战已开始
    current_status_string = "baseline"
    use_time = 0

def process_challenge_logic(relax_index):
    """ 
    消费 RELAX 指数，并更新挑战状态
    RELAX 指数由主控每秒发送一次
    """
    global start_time, challenge_start_time, baseline_value, target_threshold, above_threshold_start, challenge_ended, current_status_string, use_time, challenge_started
    
    # 只有当前端点击"开始挑战"时才处理数据
    if not challenge_started or challenge_ended:
        return
        
    current_time = time.time()
    if start_time is None:
        start_time = current_time
        print("--- 收到有效 RELAX 指数，开始计算10秒基线 ---")
        
    elapsed_time = current_time - start_time

    # ---- 阶段一：计算基线 ----
    if elapsed_time < BASELINE_DURATION:
        baseline_data.append(relax_index)
        current_status_string = "baseline"
        broadcast_to_frontend(relax_index)
        print(f"[基线采集] 进度: {elapsed_time:.1f}s/{BASELINE_DURATION}s | RELAX指数: {relax_index:.4f}")
        return

    # ---- 阶段二：初始化阈值 ----
    if baseline_value is None:
        baseline_value = sum(baseline_data) / len(baseline_data)
        target_threshold = baseline_value * THRESHOLD_BOOST
        challenge_start_time = current_time
        current_status_string = "challenging"
        print(f"\n【基线完成】平均基线: {baseline_value:.4f} | 目标阈值: {target_threshold:.4f}\n")

    # ---- 阶段三：实时检测与超时 ----
    challenge_elapsed = current_time - challenge_start_time
    use_time = challenge_elapsed
    
    if challenge_elapsed > CHALLENGE_TIMEOUT:
        current_status_string = "failed"
        challenge_ended = True
        broadcast_to_frontend(relax_index)
        print("❌ 挑战超时失败！")
        return

    # ---- 阶段四：阈值保持检测 ----
    if relax_index >= target_threshold:
        if above_threshold_start is None:
            above_threshold_start = current_time
        
        hold_duration = current_time - above_threshold_start
        print(f"[保持中] 已连续保持: {hold_duration:.1f}s/{REQUIRED_HOLD_TIME}s | RELAX指数: {relax_index:.4f}")
        
        if hold_duration >= REQUIRED_HOLD_TIME:
            current_status_string = "success"
            challenge_ended = True
            print(f"🎉 挑战成功！耗时: {challenge_elapsed:.2f}s")
    else:
        if above_threshold_start is not None:
            above_threshold_start = None
            print(f"[中断] RELAX指数下跌 ({relax_index:.4f})，重新计时...")

    # 实时把最新状态同步给 Vue 前端
    broadcast_to_frontend(relax_index)

# ==================== 4. 通信接口管理 ====================
async def frontend_handler(websocket, path=None):
    """ 管理 Vue 前端的连接 """
    frontend_clients.add(websocket)
    print(f" ✅ 网页端已成功连入算法控制台 ({websocket.remote_address})")
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                if data.get("action") == "reset":
                    reset_challenge_state()
                    print("🔄 已重置挑战状态")
                elif data.get("action") == "choose_mock":
                    print("💡 切换为仿真模拟模式")
                    # 通知 aurora_server 切换到模拟模式
                    await notify_aurora_server({"mode": "mock"})
                elif data.get("action") == "choose_ble":
                    print("🔌 切换为真实蓝牙模式")
                    # 通知 aurora_server 切换到蓝牙模式
                    await notify_aurora_server({"mode": "ble"})
                elif data.get("action") == "pause":
                    if current_status_string == "challenging":
                        print("⏸️ 挑战已暂停")
                elif data.get("action") == "resume":
                    if current_status_string == "challenging":
                        print("▶️ 挑战已恢复")
                elif data.get("action") == "end":
                    challenge_ended = True
                    current_status_string = "failed"
                    broadcast_to_frontend(0)
                    print("⏹️ 挑战已结束")
            except json.JSONDecodeError:
                pass
    except Exception as e:
        print(f"⚠️ 前端通信错误: {e}")
    finally:
        frontend_clients.discard(websocket)
        print(f" ❌ 网页端已断开连接 ({websocket.remote_address})")

async def notify_aurora_server(data):
    """ 通知 aurora_server 切换模式 """
    try:
        # 连接到 aurora_server 的控制端口
        async with websockets.connect("ws://localhost:8766/control") as ws:
            await ws.send(json.dumps(data))
            print(f"✅ 已通知 aurora_server: {data}")
    except Exception as e:
        print(f"⚠️ 无法通知 aurora_server: {e}")

async def listen_to_aurora_server():
    """ 从统一后端拿 RELAX 指数数据 """
    uri = "ws://localhost:8765/relax"
    
    try:
        async with websockets.connect(uri) as websocket:
            print(f"✅ 已连接到数据源服务器 {uri}")
            async for message in websocket:
                if challenge_ended: 
                    break
                try:
                    data = json.loads(message)
                    relax_index = data.get("relax_index")
                    if relax_index is not None:
                        process_challenge_logic(relax_index)
                except json.JSONDecodeError as e:
                    print(f"[数据解析错误] {e}")
    except ConnectionRefusedError:
        print(f"❌ 无法连接到数据源服务器 {uri}，请先启动 aurora_server.py")
    except Exception as e:
        print(f"❌ 数据源连接错误: {e}")

async def main():
    global main_loop
    main_loop = asyncio.get_running_loop()
    
    # 1. 启动给前端网页提供数据的服务 (端口 8888)
    frontend_server = await serve(frontend_handler, "localhost", 8888)
    print("=== 算法控制台已就绪 (Port: 8888)，等待 Vue 前端连接... ===")
    
    # 2. 并发连接数据源头服务器（不阻塞前端服务）
    asyncio.create_task(listen_to_aurora_server())
    
    await frontend_server.wait_closed()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n程序已关闭。")
