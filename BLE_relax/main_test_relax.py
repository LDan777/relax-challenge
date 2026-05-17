# main.py - 主程序
from Aurora520project.BLE_relax.BLE_relax0 import start 
def handler(data):
    # 解析RELAX数据
    if data.startswith('RELAX:'):
        try:
            # 提取冒号后面的数值部分并转换为float
            value = float(data.split(':')[1])
            print(f"RELAX：{value}")
        except (IndexError, ValueError) as e:
            print(f"数据解析失败: {e}")
        #测试用，实际可直接输出value
        
# 启动蓝牙连接
if __name__ == "__main__":
    start(handler)