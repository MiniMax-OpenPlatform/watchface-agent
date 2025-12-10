import React, { useState, useEffect } from 'react';
import { Download, Code, Eye, Key } from 'lucide-react';
import ChatPanel from './components/ChatPanel';
import CodePanel from './components/CodePanel';
import PreviewPanel from './components/PreviewPanel';
import AssetUploadPanel from './components/AssetUploadPanel';
import ConfigPanel from './components/ConfigPanel';
import ProjectSelector from './components/ProjectSelector';
import ApiKeySettings from './components/ApiKeySettings';
import { useAppStore } from './store/useAppStore';
import { generateProject, editProject, downloadProject } from './api/client';
import type { WatchfaceConfig } from './components/ConfigPanel';

function App() {
  const {
    sessionId,
    projectId,
    setProjectId,
    assets,
    addAsset,
    removeAsset,
    clearAssets,
    config,
    updateConfig,
    files,
    fileTree,
    selectedFile,
    setFiles,
    setSelectedFile,
    conversation,
    addMessage,
    setConversation,
    loadProject,
    setLastReasoning,
    setLastGeneratedCode,
    isGenerating,
    setIsGenerating,
    error,
    setError,
  } = useAppStore();

  const [showUploadPanel, setShowUploadPanel] = useState(true);
  const [viewMode, setViewMode] = useState<'code' | 'preview'>('preview'); // 默认预览模式
  const [showApiKeySettings, setShowApiKeySettings] = useState(false);

  // 页面加载时恢复项目
  useEffect(() => {
    const restoreProject = async () => {
      // 如果有 projectId 但没有文件，说明是刷新后需要恢复
      if (projectId && files.length === 0) {
        console.log('🔄 检测到项目ID，尝试从后端恢复...', projectId);
        try {
          const response = await fetch(`/api/project/${projectId}`);
          const data = await response.json();
          
          if (data.success) {
            console.log('✅ 项目恢复成功', data);
            // 使用loadProject函数完整恢复项目状态（包括对话历史、配置、素材等）
            loadProject(data);
          }
        } catch (err) {
          console.error('❌ 恢复项目失败:', err);
          // 不显示错误给用户，静默失败
        }
      }
    };
    
    restoreProject();
  }, [projectId, files.length, loadProject]); // 当 projectId 变化或需要恢复时执行

  // 处理生成/编辑请求
  const handleGenerate = async (instruction: string) => {
    setIsGenerating(true);
    setError(null);

    // 🔥 立即添加用户消息到对话列表，提升交互体验
    addMessage({
      role: 'user',
      content: instruction,
      timestamp: new Date().toISOString(),
    });

    try {
      let response;

      if (projectId) {
        // 编辑现有项目
        response = await editProject({
          instruction,
          session_id: sessionId,
          project_id: projectId,
          assets,  // 传递当前的素材（包括新上传的）
        });
      } else {
        // 生成新项目
        response = await generateProject({
          instruction,
          assets,
          config,
          session_id: sessionId,
        });

        // 保存项目ID
        setProjectId(response.project_id);
      }

      // 更新文件和文件树
      setFiles(response.files, response.file_tree);

      // 自动选择 index.html 文件
      const indexHtml = response.files.find((f: any) =>
        f.path.includes('index.html')
      );
      if (indexHtml) {
        setSelectedFile(indexHtml);
        setLastGeneratedCode(indexHtml.content);
      }

      // 保存reasoning
      setLastReasoning(response.reasoning || '');

      // 使用后端返回的对话历史更新前端（这样可以保证同步）
      if (response.conversation_history && response.conversation_history.length > 0) {
        setConversation(response.conversation_history);
      }
    } catch (err: any) {
      setError(err.message);
      // 错误时手动添加错误消息
      addMessage({
        role: 'assistant',
        content: `❌ 错误: ${err.message}`,
        timestamp: new Date().toISOString(),
      });
    } finally {
      setIsGenerating(false);
    }
  };

  // 处理下载
  const handleDownload = async () => {
    if (!projectId) {
      alert('请先生成项目');
      return;
    }

    try {
      const blob = await downloadProject(projectId);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${config.watchface_name}.zip`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error: any) {
      alert(`下载失败: ${error.message}`);
    }
  };

  // 处理素材删除
  const handleAssetDeleted = (assetType: string, filename: string) => {
    console.log('🗑️ 删除素材:', assetType, filename);
    removeAsset(assetType, filename);
  };

  // 处理新建项目（清空素材）
  const handleNewProject = () => {
    setProjectId(null);
    clearAssets();
    setFiles([], null);
    setConversation([]);
    console.log('🆕 新建项目，素材已清空');
  };

  return (
    <div className="h-screen flex flex-col bg-gray-100">
      {/* 顶部标题栏 */}
      <header className="bg-gradient-to-r from-blue-600 to-blue-700 text-white px-6 py-4 shadow-lg">
        <div className="flex items-center justify-between">
          {/* 左侧标题 */}
          <div className="flex-shrink-0">
            <h1 className="text-xl font-bold">表盘 Code Agent</h1>
            <p className="text-blue-100 text-sm mt-0.5">
              AI 智能表盘 UI 生成助手
            </p>
          </div>
          
          {/* 中间项目选择器 */}
          <div className="flex-1 flex justify-center">
            <ProjectSelector />
          </div>
          
          {/* 右侧操作按钮 */}
          <div className="flex items-center gap-3 flex-shrink-0">
            {/* 预览/代码切换 */}
            {projectId && (
              <div className="flex items-center gap-1 bg-white bg-opacity-20 rounded-lg p-1">
                <button
                  onClick={() => setViewMode('preview')}
                  className={`px-3 py-1.5 rounded-md text-sm flex items-center gap-1.5 transition-colors ${
                    viewMode === 'preview' 
                      ? 'bg-white text-blue-600' 
                      : 'text-white hover:bg-white hover:bg-opacity-10'
                  }`}
                >
                  <Eye className="w-4 h-4" />
                  预览
                </button>
                <button
                  onClick={() => setViewMode('code')}
                  className={`px-3 py-1.5 rounded-md text-sm flex items-center gap-1.5 transition-colors ${
                    viewMode === 'code' 
                      ? 'bg-white text-blue-600' 
                      : 'text-white hover:bg-white hover:bg-opacity-10'
                  }`}
                >
                  <Code className="w-4 h-4" />
                  代码
                </button>
              </div>
            )}

            {/* API Key设置 */}
            <button
              onClick={() => setShowApiKeySettings(true)}
              className="flex items-center gap-2 px-3 py-2 bg-white bg-opacity-20 text-white hover:bg-opacity-30 rounded-lg transition-colors font-medium border border-white border-opacity-30"
              title="设置API Key"
            >
              <Key className="w-4 h-4" />
              API Key
            </button>

            {/* 下载按钮 - 已隐藏 */}
            {/* {projectId && (
              <button
                onClick={handleDownload}
                className="flex items-center gap-2 px-3 py-2 bg-white text-blue-600 rounded-lg hover:bg-blue-50 transition-colors font-medium"
              >
                <Download className="w-4 h-4" />
                下载项目
              </button>
            )} */}

            {/* 会话ID */}
            <div className="text-sm text-blue-100">
              会话ID: {sessionId.slice(-8)}
            </div>
          </div>
        </div>
      </header>

      {/* 主内容区 */}
      <div className="flex-1 flex overflow-hidden">
        {/* 左侧：素材上传和配置 */}
        <div className="w-80 flex flex-col p-4 bg-gray-50 overflow-hidden">
          {/* 素材上传区域 - 占据一半空间 */}
          <div className="flex-1 overflow-y-auto mb-4">
            {showUploadPanel && (
              <AssetUploadPanel
                sessionId={sessionId}
                onAssetUploaded={addAsset}
                onAssetDeleted={handleAssetDeleted}
                assets={assets}
              />
            )}
          </div>

          {/* 项目配置区域 - 占据一半空间 */}
          <div className="flex-1 overflow-y-auto">
            <ConfigPanel
              config={config as WatchfaceConfig}
              onChange={(newConfig) => updateConfig(newConfig)}
            />
          </div>

          {/* 收起/展开按钮 */}
          <button
            onClick={() => setShowUploadPanel(!showUploadPanel)}
            className="mt-4 text-sm text-gray-600 hover:text-gray-800"
          >
            {showUploadPanel ? '▲ 收起素材面板' : '▼ 展开素材面板'}
          </button>
        </div>

        {/* 中间：对话区 - 占据一半空间 */}
        <div className="flex-1 flex flex-col p-4 border-r border-gray-200">
          <ChatPanel
            conversation={conversation}
            onSendMessage={handleGenerate}
            isGenerating={isGenerating}
            error={error}
          />
        </div>

        {/* 右侧：代码和预览 */}
        <div className="flex-1 flex flex-col p-4 bg-gray-50 overflow-hidden">
          {/* 内容区：根据模式显示预览或代码 */}
          <div className="flex-1 min-h-0">
            {selectedFile ? (
              viewMode === 'preview' ? (
                <div className="h-full rounded-lg shadow overflow-hidden">
                  <PreviewPanel code={selectedFile.content} />
                </div>
              ) : (
                <CodePanel code={selectedFile.content} language={selectedFile.language} />
              )
            ) : (
              <div className="h-full bg-white rounded-lg shadow p-6 flex items-center justify-center text-gray-400">
                <div className="text-center">
                  <p className="text-6xl mb-4">⌚</p>
                  <p className="text-lg mb-2">开始创作您的表盘</p>
                  <p className="text-sm">
                    1. 在对话框描述您想要的表盘设计
                    <br />
                    2. AI 将生成可运行的 HTML 表盘
                    <br />
                    3. 实时预览效果，支持下载
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* 底部状态栏 */}
      <footer className="bg-gray-800 text-gray-300 px-6 py-3 text-sm flex justify-between items-center">
        <div className="flex items-center gap-6">
          {/* <span>🚀 后端: http://10.11.17.19:10030</span>
          <span>🎨 前端: http://10.11.17.19:10031</span> */}
          {projectId && <span>📁 项目ID: {projectId.slice(0, 8)}...</span>}
        </div>
        <div className="flex items-center gap-4">
          <span>素材: {Object.keys(assets).filter(k => assets[k as keyof typeof assets]).length}</span>
          <span>文件: {files.length}</span>
          <span>消息: {conversation.length}</span>
        </div>
      </footer>

      {/* API Key 设置弹窗 */}
      <ApiKeySettings
        isOpen={showApiKeySettings}
        onClose={() => setShowApiKeySettings(false)}
      />
    </div>
  );
}

export default App;
