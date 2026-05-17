<template>
  <div class="challenge-container">
    <h1>极速放松挑战 (RELAX BCI)</h1>
    
    <div class="status-panel">
      <div class="status-badge" :class="challengeStatus">
        状态: {{ statusText }}
      </div>
      <div class="timer" :class="{ 'warning': remainingTime <= 20 }">
        <span v-if="challengeStatus === 'baseline'">
          ⏱️ 基线采集: {{ baselineCountdown }} / 10 秒
        </span>
        <span v-else>
          ⏱️ 倒计时: {{ remainingTime }} 秒
        </span>
      </div>
    </div>

    <div class="control-section">
      <div class="mode-selector">
        <button 
          @click="chooseMode('mock')" 
          :class="{ active: selectedMode === 'mock' }"
          class="mode-btn mock-btn"
        >
          💡 仿真模拟挑战
        </button>
        <button 
          @click="chooseMode('ble')" 
          :class="{ active: selectedMode === 'ble' }"
          class="mode-btn ble-btn"
        >
          🔌 连蓝牙设备
        </button>
      </div>
      
      <div class="button-group">
        <button 
          @click="startChallenge" 
          :disabled="challengeStatus !== 'idle'"
          class="start-btn"
        >
          开始挑战
        </button>
        
        <button 
          @click="pauseChallenge" 
          :disabled="challengeStatus !== 'challenging'"
          class="pause-btn"
        >
          ⏸️ 暂停
        </button>
        
        <button 
          @click="stopChallenge" 
          :disabled="challengeStatus === 'idle'"
          class="end-btn"
        >
          ⏹️ 结束
        </button>
      </div>
      
      <div class="metrics">
        <div class="metric-box">
          <span class="label">当前放松指数</span>
          <span class="value">{{ currentRatio.toFixed(3) }}</span>
        </div>
        <div class="metric-box">
          <span class="label">目标阈值</span>
          <span class="value">{{ targetThreshold ? targetThreshold.toFixed(3) : '计算中...' }}</span>
        </div>
      </div>
    </div>

    <div class="chart-container">
      <EchartsWave :current-value="currentRatio" :threshold="targetThreshold" />
    </div>

    <div v-if="showModal" class="modal-overlay">
      <div class="modal-content" :class="challengeStatus">
        <h2>{{ modalTitle }}</h2>
        <p class="modal-message">{{ modalMessage }}</p>
        <button @click="closeModal" class="close-btn">确定</button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onUnmounted } from 'vue';
import EchartsWave from './components/EchartsWave.vue';

export default {
  components: { EchartsWave },
  setup() {
    const challengeStatus = ref('idle'); // idle, baseline, challenging, success, failed
    const remainingTime = ref(120);
    const baselineCountdown = ref(10);
    const currentRatio = ref(0.0);
    const targetThreshold = ref(null);
    const showModal = ref(false);
    const successTime = ref(0);
    const selectedMode = ref('mock'); // 默认选择模拟模式

    let ws = null;
    let timerInterval = null;
    let baselineTimer = null;

    const statusText = computed(() => {
      if (challengeStatus.value === 'idle') return '未开始';
      if (challengeStatus.value === 'baseline') return '正在采集10秒基线...';
      if (challengeStatus.value === 'challenging') return '挑战中！请放松大脑...';
      if (challengeStatus.value === 'success') return '挑战成功 🎉';
      return '挑战失败 ❌';
    });

    // 弹窗文本控制
    const modalTitle = computed(() => challengeStatus.value === 'success' ? '🎉 挑战成功！' : '❌ 挑战失败');
    const modalMessage = computed(() => {
      return challengeStatus.value === 'success' 
        ? `太棒了！你成功进入了放松状态，总耗时：${successTime.value} 秒！`
        : '挑战已结束，调整呼吸，再试一次吧！';
    });

    // 启动基线倒计时
    const startBaselineCountdown = () => {
      baselineCountdown.value = 10;
      baselineTimer = setInterval(() => {
        if (baselineCountdown.value > 0) {
          baselineCountdown.value--;
        } else {
          clearInterval(baselineTimer);
          // 基线采集完成，等待后端发送 challenging 状态
          console.log('⏱️ 基线采集倒计时完成，等待后端进入挑战阶段...');
        }
      }, 1000);
    };

    // 启动挑战
    const startChallenge = () => {
      challengeStatus.value = 'baseline';
      remainingTime.value = 120;
      baselineCountdown.value = 10;
      targetThreshold.value = null;
      
      // 启动基线倒计时
      startBaselineCountdown();
      
      // 连接到 relax_challenge.py 的算法服务 (端口 8888)
      ws = new WebSocket('ws://localhost:8888');
      
      ws.onopen = () => {
        console.log('✅ 已连接到算法服务');
        // 发送重置命令给后端
        ws.send(JSON.stringify({ action: 'reset' }));
        console.log('🔄 已发送重置命令');
      };
      
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          // 算法端发来：{ relax_index: 1.45, threshold: 1.32, status: 'challenging', useTime: 5.2 }
          currentRatio.value = data.relax_index;
          if (data.threshold) targetThreshold.value = data.threshold;
          
          // 同步状态
          if (data.status === 'challenging' && challengeStatus.value === 'baseline') {
            challengeStatus.value = 'challenging';
            startCountdown(); // 进入挑战，启动倒计时
          }
          
          if (data.status === 'success') {
            showResult('success', data.useTime);
          }
          
          if (data.status === 'failed') {
            showResult('failed', data.useTime);
          }
        } catch (error) {
          console.error('❌ 数据解析错误:', error);
        }
      };
      
      ws.onerror = (error) => {
        console.error('❌ WebSocket 连接错误:', error);
        showResult('failed');
      };
      
      ws.onclose = () => {
        console.log('⚠️ 已断开连接');
      };
    };

    const startCountdown = () => {
      timerInterval = setInterval(() => {
        if (remainingTime.value > 0) {
          remainingTime.value--;
        } else {
          showResult('failed');
        }
      }, 1000);
    };

    const pauseChallenge = () => {
      if (ws && challengeStatus.value === 'challenging') {
        ws.send(JSON.stringify({ action: 'pause' }));
        console.log('⏸️ 已发送暂停命令');
      }
    };

    const stopChallenge = () => {
      if (ws) {
        ws.send(JSON.stringify({ action: 'end' }));
        console.log('⏹️ 已发送结束命令');
        showResult('failed');
      }
    };

    const showResult = (result, timeTaken = 0) => {
      clearInterval(timerInterval);
      if (ws) ws.close();
      challengeStatus.value = result;
      successTime.value = timeTaken;
      showModal.value = true;
    };

    const closeModal = () => {
      showModal.value = false;
      challengeStatus.value = 'idle';
    };

    const chooseMode = async (mode) => {
      selectedMode.value = mode;
      console.log(`📋 已选择模式: ${mode === 'mock' ? '仿真模拟' : '真实蓝牙'}`);
      
      // 通知后端切换模式
      try {
        const response = await fetch('ws://localhost:8888', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ action: `choose_${mode}` })
        });
      } catch (error) {
        // WebSocket 不支持 fetch，改用 WebSocket 发送
        if (ws && ws.readyState === WebSocket.OPEN) {
          ws.send(JSON.stringify({ action: `choose_${mode}` }));
        }
      }
    };

    onUnmounted(() => {
      clearInterval(timerInterval);
      clearInterval(baselineTimer);
      if (ws) ws.close();
    });

    return {
      challengeStatus, remainingTime, baselineCountdown, currentRatio, targetThreshold,
      showModal, statusText, modalTitle, modalMessage, successTime, selectedMode,
      startChallenge, pauseChallenge, stopChallenge, closeModal, chooseMode
    };
  }
};
</script>

<style scoped>
.challenge-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 20px;
  text-align: center;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
  border-radius: 20px;
  color: white;
}

h1 {
  font-size: 2.5rem;
  margin-bottom: 30px;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
}

.status-panel {
  display: flex;
  justify-content: space-around;
  margin: 20px 0;
  font-size: 1.2rem;
  gap: 20px;
}

.status-badge {
  padding: 15px 30px;
  border-radius: 15px;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  border: 2px solid rgba(255, 255, 255, 0.3);
  font-weight: bold;
  flex: 1;
}

.status-badge.baseline {
  background: rgba(255, 193, 7, 0.3);
  border-color: #ffc107;
}

.status-badge.challenging {
  background: rgba(76, 175, 80, 0.3);
  border-color: #4caf50;
}

.status-badge.success {
  background: rgba(76, 175, 80, 0.3);
  border-color: #4caf50;
}

.status-badge.failed {
  background: rgba(244, 67, 54, 0.3);
  border-color: #f44336;
}

.timer {
  padding: 15px 30px;
  border-radius: 15px;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  border: 2px solid rgba(255, 255, 255, 0.3);
  font-weight: bold;
  flex: 1;
  font-size: 1.3rem;
}

.timer.warning {
  background: rgba(244, 67, 54, 0.3);
  border-color: #f44336;
  animation: pulse 1s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

.control-section {
  margin: 30px 0;
}

.mode-selector {
  display: flex;
  gap: 15px;
  justify-content: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.mode-btn {
  padding: 12px 30px;
  font-size: 1rem;
  border: 2px solid rgba(255, 255, 255, 0.5);
  border-radius: 25px;
  color: white;
  cursor: pointer;
  font-weight: bold;
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
}

.mode-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  border-color: white;
  transform: translateY(-2px);
}

.mode-btn.active {
  background: rgba(255, 255, 255, 0.3);
  border-color: white;
  box-shadow: 0 0 20px rgba(255, 255, 255, 0.5);
}

.mock-btn.active {
  background: rgba(76, 175, 80, 0.4);
  border-color: #4caf50;
  box-shadow: 0 0 20px rgba(76, 175, 80, 0.6);
}

.ble-btn.active {
  background: rgba(33, 150, 243, 0.4);
  border-color: #2196f3;
  box-shadow: 0 0 20px rgba(33, 150, 243, 0.6);
}

.button-group {
  display: flex;
  gap: 15px;
  justify-content: center;
  margin-bottom: 30px;
  flex-wrap: wrap;
}

button {
  padding: 12px 30px;
  font-size: 1rem;
  border: none;
  border-radius: 25px;
  color: white;
  cursor: pointer;
  font-weight: bold;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
}

button:disabled {
  background: #ccc;
  cursor: not-allowed;
  opacity: 0.5;
}

.start-btn {
  background: linear-gradient(135deg, #4ecdc4 0%, #44a08d 100%);
  min-width: 120px;
}

.pause-btn {
  background: linear-gradient(135deg, #ffa500 0%, #ff8c00 100%);
  min-width: 120px;
}

.end-btn {
  background: linear-gradient(135deg, #f44336 0%, #d32f2f 100%);
  min-width: 120px;
}

.metrics {
  display: flex;
  justify-content: space-between;
  margin: 30px 0;
  gap: 20px;
}

.metric-box {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  padding: 20px;
  border-radius: 15px;
  width: 45%;
  border: 2px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.metric-box .label {
  display: block;
  font-size: 0.9rem;
  opacity: 0.9;
  margin-bottom: 10px;
}

.metric-box .value {
  display: block;
  font-size: 2rem;
  font-weight: bold;
  color: #4ecdc4;
}

.chart-container {
  margin: 30px 0;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  padding: 20px;
  border-radius: 15px;
  border: 2px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 40px;
  border-radius: 20px;
  text-align: center;
  max-width: 400px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
  color: #333;
}

.modal-content h2 {
  font-size: 2rem;
  margin-bottom: 20px;
}

.modal-message {
  font-size: 1.1rem;
  margin-bottom: 30px;
  color: #666;
}

.close-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 12px 40px;
  font-size: 1rem;
  border: none;
  border-radius: 25px;
  cursor: pointer;
  font-weight: bold;
  transition: all 0.3s ease;
}

.close-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
}

@media (max-width: 768px) {
  .challenge-container {
    padding: 15px;
  }

  h1 {
    font-size: 1.8rem;
  }

  .status-panel {
    flex-direction: column;
  }

  .button-group {
    flex-direction: column;
  }

  button {
    width: 100%;
  }

  .metrics {
    flex-direction: column;
  }

  .metric-box {
    width: 100%;
  }
}
</style>
