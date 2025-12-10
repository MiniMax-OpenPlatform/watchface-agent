/**
 * 测试页面 - 用于诊断渲染问题
 */
import React from 'react';

function TestApp() {
  return (
    <div style={{ padding: '20px', fontFamily: 'Arial' }}>
      <h1 style={{ color: 'blue' }}>✅ React渲染正常</h1>
      <p>如果你能看到这段文字，说明React基础渲染没有问题。</p>
      <div style={{ marginTop: '20px', padding: '10px', background: '#f0f0f0' }}>
        <h2>系统信息</h2>
        <ul>
          <li>当前时间: {new Date().toLocaleString()}</li>
          <li>React版本: {React.version}</li>
          <li>环境: {import.meta.env.MODE}</li>
        </ul>
      </div>
      <div style={{ marginTop: '20px' }}>
        <p>如果主应用（App.tsx）无法加载，可能是以下原因：</p>
        <ol>
          <li>某个组件导入失败</li>
          <li>TypeScript类型错误</li>
          <li>zustand store初始化问题</li>
          <li>API client配置问题</li>
        </ol>
      </div>
    </div>
  );
}

export default TestApp;

