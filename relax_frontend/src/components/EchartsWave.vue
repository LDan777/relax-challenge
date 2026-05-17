<template>
  <div ref="chartRef" class="wave-chart"></div>
</template>

<script>
import { ref, onMounted, onUnmounted, watch } from 'vue';
import * as echarts from 'echarts';

export default {
  name: 'EchartsWave',
  props: {
    // 从父组件 App.vue 传过来的当前实时 RELAX 指数
    currentValue: {
      type: Number,
      required: true
    },
    // 从父组件传过来的目标阈值 (基线计算出来前为 null)
    threshold: {
      type: [Number, Object],
      default: null
    }
  },
  setup(props) {
    const chartRef = ref(null);
    let myChart = null;
    
    // 存放图表历史数据的时间戳和数值
    const timeData = [];
    const valueData = [];
    const MAX_POINTS = 30; // 图表最多显示最近的30个数据点

    // 初始化 ECharts 图表
    const initChart = () => {
      if (!chartRef.value) return;
      
      myChart = echarts.init(chartRef.value);
      
      const option = {
        title: {
          text: '🧠 放松指数 (RELAX Index) 实时趋势',
          left: 'center',
          textStyle: { color: '#333', fontSize: 14 }
        },
        tooltip: {
          trigger: 'axis',
          formatter: '{b} <br/>RELAX指数: {c}'
        },
        grid: { left: '10%', right: '10%', bottom: '15%', top: '20%' },
        xAxis: {
          type: 'category',
          boundaryGap: false,
          data: timeData,
          axisLabel: {
            formatter: (value) => value.split(' ')[1] || value // 只显示时间部分 (如 12:05:23)
          }
        },
        yAxis: {
          type: 'value',
          scale: true, // 坐标轴不从0开始，根据数据自动调整，波形更明显
          name: 'RELAX指数',
          splitLine: { show: true, lineStyle: { type: 'dashed' } }
        },
        series: [
          {
            name: 'RELAX Index',
            type: 'line',
            smooth: true, // 开启平滑曲线，看起来更丝滑
            showSymbol: false,
            data: valueData,
            itemStyle: { color: '#4ecdc4' }, // 科技感青色线
            areaStyle: {
              // 给折线图下方加一点淡青色的渐变阴影
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: 'rgba(78, 205, 196, 0.4)' },
                { offset: 1, color: 'rgba(78, 205, 196, 0.0)' }
              ])
            },
            // 核心功能：动态标记目标阈值水平线
            markLine: {
              symbol: ['none', 'none'], // 不显示箭头
              silent: true,            // 鼠标悬浮不触发交互
              data: props.threshold ? [{
                yAxis: props.threshold,
                name: '目标阈值',
                lineStyle: { color: '#ff6b6b', type: 'dashed', width: 2 },
                label: { formatter: '目标阈值: {c}', position: 'end' }
              }] : []
            }
          }
        ]
      };
      
      myChart.setOption(option);
    };

    // 监听父组件传过来的实时数值变化
    watch(() => props.currentValue, (newValue) => {
      if (!myChart) {
        initChart();
      }

      const now = new Date();
      const timeStr = now.toTimeString().split(' ')[0]; // 获取当前时间字符串 "hh:mm:ss"

      // 往数据队列里推入新点
      timeData.push(timeStr);
      valueData.push(parseFloat(newValue.toFixed(4)));

      // 如果数据点超过最大限制，把最老的数据踢出去，实现平移
      if (timeData.length > MAX_POINTS) {
        timeData.shift();
        valueData.shift();
      }

      // 更新图表数据
      myChart.setOption({
        xAxis: { data: timeData },
        series: [{ data: valueData }]
      });
    });

    // 监听阈值的变化（当10秒基线计算完，阈值从 null 变成具体数值时触发）
    watch(() => props.threshold, (newThreshold) => {
      if (!myChart) return;
      
      // 动态更新红色的目标阈值虚线
      myChart.setOption({
        series: [{
          markLine: {
            data: newThreshold ? [{
              yAxis: newThreshold,
              lineStyle: { color: '#ff6b6b', type: 'dashed', width: 2 },
              label: { formatter: '目标阈值: {c}', position: 'end' }
            }] : []
          }
        }]
      });
    });

    // 监听窗口大小改变，自适应缩放图表
    const handleResize = () => { myChart && myChart.resize(); };

    onMounted(() => {
      initChart();
      window.addEventListener('resize', handleResize);
    });

    onUnmounted(() => {
      window.removeEventListener('resize', handleResize);
      if (myChart) {
        myChart.dispose();
        myChart = null;
      }
    });

    return { chartRef };
  }
};
</script>

<style scoped>
.wave-chart {
  width: 100%;
  height: 350px; /* 控制图表的高度 */
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  padding: 10px;
  box-sizing: border-box;
}
</style>
