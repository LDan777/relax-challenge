import asyncio
import struct
from bleak import BleakClient, BleakScanner

DEVICE_NAME = "Aurora"
CHARACTERISTIC_UUID_TX = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"

#  核心接口函数
# 作用：接收一个「处理消息的函数」，收到蓝牙消息就调用它
# --------------------------
async def connect_ble(handler):
    # 1. 搜索ESP32
    devices = await BleakScanner.discover()
    addr = None
    for d in devices:
        if d.name and DEVICE_NAME in d.name:
            addr = d.address
            break
    if addr is None:
       print(f"错误：没找到名字包含'{DEVICE_NAME}'的设备！")
       return
    # 2. 连接蓝牙
    async with BleakClient(addr) as client:
        print("蓝牙连接成功！")
        # 3. 收到消息 → 调用传入的函数
        def callback(sender, data):
            # 1. 检查是否以字母'R'开头（放松指数数据）- 需要处理
            if len(data) > 0 and chr(data[0]) == 'R':
                # 将字节数据转换为字符串并传递给handler
                try:
                    message = data.decode('utf-8').strip()
                    handler(message)
                except Exception as e:
                    print(f"数据解码失败: {e}")
                return
            # 2. 其他数据（包括原始脑电数据0x01开头）- 忽略
        
        # 注册通知回调
        await client.start_notify(CHARACTERISTIC_UUID_TX, callback)
        # 保持连接活跃（循环等待）
        while True:
            await asyncio.sleep(1)
# 启动函数
def start(handler):
    asyncio.run(connect_ble(handler))