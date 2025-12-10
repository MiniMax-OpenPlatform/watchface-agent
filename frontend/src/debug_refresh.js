/**
 * 页面刷新调试工具
 * 在浏览器控制台中粘贴此代码来监控刷新原因
 */

console.log('🔍 页面刷新监控已启动');

let refreshCount = 0;
const refreshLog = [];

// 监听页面卸载前事件
window.addEventListener('beforeunload', (e) => {
  refreshCount++;
  const logEntry = {
    count: refreshCount,
    time: new Date().toISOString(),
    stack: new Error().stack,
  };
  refreshLog.push(logEntry);
  
  console.warn(`⚠️ 页面即将刷新 (第 ${refreshCount} 次)`);
  console.log('刷新时间:', logEntry.time);
  console.trace('刷新触发位置:');
  
  // 尝试保存日志到sessionStorage
  try {
    sessionStorage.setItem('refreshLog', JSON.stringify(refreshLog));
  } catch (err) {
    console.error('无法保存刷新日志:', err);
  }
});

// 恢复之前的刷新日志
try {
  const savedLog = sessionStorage.getItem('refreshLog');
  if (savedLog) {
    const previousRefreshes = JSON.parse(savedLog);
    console.log('📋 之前的刷新记录:', previousRefreshes);
    refreshCount = previousRefreshes.length;
  }
} catch (err) {
  console.error('无法读取刷新日志:', err);
}

// 监听Vite HMR事件
if (import.meta && import.meta.hot) {
  console.log('🔥 Vite HMR 已启用');
  
  import.meta.hot.on('vite:beforeUpdate', () => {
    console.log('🔄 Vite HMR 正在更新模块...');
  });
  
  import.meta.hot.on('vite:afterUpdate', () => {
    console.log('✅ Vite HMR 模块更新完成');
  });
  
  import.meta.hot.on('vite:beforeFullReload', () => {
    console.warn('⚠️ Vite 即将执行完整页面刷新!');
    console.trace('刷新触发原因:');
  });
  
  import.meta.hot.on('vite:error', (err) => {
    console.error('❌ Vite HMR 错误:', err);
  });
} else {
  console.log('ℹ️ Vite HMR 未启用（可能是生产构建）');
}

// 监听WebSocket连接状态
const originalWebSocket = window.WebSocket;
window.WebSocket = function(...args) {
  const ws = new originalWebSocket(...args);
  
  console.log('🔌 WebSocket 连接创建:', args[0]);
  
  ws.addEventListener('open', () => {
    console.log('✅ WebSocket 连接已打开');
  });
  
  ws.addEventListener('close', (event) => {
    console.warn('🔴 WebSocket 连接已关闭');
    console.log('关闭代码:', event.code);
    console.log('关闭原因:', event.reason);
  });
  
  ws.addEventListener('error', (error) => {
    console.error('❌ WebSocket 错误:', error);
  });
  
  return ws;
};

// 拦截location.reload
const originalReload = location.reload.bind(location);
location.reload = function(...args) {
  console.warn('🔄 location.reload() 被调用!');
  console.trace('调用位置:');
  return originalReload(...args);
};

// 定期报告状态
setInterval(() => {
  const uptime = Math.floor(performance.now() / 1000);
  console.log(`📊 页面运行时间: ${uptime}秒, 刷新次数: ${refreshCount}`);
}, 30000); // 每30秒报告一次

console.log('✅ 刷新监控工具已就绪');
console.log('💡 如果页面自动刷新，请检查上面的日志来确定原因');

