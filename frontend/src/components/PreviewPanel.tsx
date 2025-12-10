/**
 * Preview Panel Component - 表盘预览区
 */
import { useEffect, useRef, useState } from 'react';
import { Download, Maximize2, Minimize2 } from 'lucide-react';
import { useAppStore } from '../store/useAppStore';

interface PreviewPanelProps {
  code: string;
}

export default function PreviewPanel({ code }: PreviewPanelProps) {
  const iframeRef = useRef<HTMLIFrameElement>(null);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [previewSrc, setPreviewSrc] = useState<string>('');
  const { projectId } = useAppStore();

  useEffect(() => {
    if (code) {
      try {
        // 替换相对路径为API路径
        let processedCode = code;
        
        if (projectId) {
          // 获取API base URL（与API client保持一致）
          const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://10.11.17.19:10030';
          
          // 替换 ./assets/ 路径为完整的API路径
          processedCode = code.replace(
            /(['"])\.\/assets\/([^'"]+)\1/g,
            `$1${apiBaseUrl}/api/project/${projectId}/assets/$2$1`
          );
          
          // 也处理 url(./assets/...) 的情况
          processedCode = processedCode.replace(
            /url\(\.\/assets\/([^)]+)\)/g,
            `url(${apiBaseUrl}/api/project/${projectId}/assets/$1)`
          );
          
          // 处理 url("./assets/...") 或 url('./assets/...')
          processedCode = processedCode.replace(
            /url\((['"])\.\/assets\/([^)'"]+)\1\)/g,
            `url(${apiBaseUrl}/api/project/${projectId}/assets/$2)`
          );
        }
        
        setPreviewSrc(processedCode);
        setError(null);
      } catch (err: any) {
        console.error('Preview error:', err);
        setError(err.message);
      }
    }
  }, [code, projectId]);

  const handleDownload = () => {
    if (!code) return;

    // 下载时使用原始代码（保持相对路径），便于用户本地使用
    const blob = new Blob([code], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `watchface_${Date.now()}.html`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const toggleFullscreen = () => {
    setIsFullscreen(!isFullscreen);
  };

  if (!code) {
    return (
      <div className="flex-1 flex items-center justify-center bg-gray-900">
        <div className="text-center">
          <div className="text-6xl mb-4">⌚</div>
          <h3 className="text-xl font-semibold text-gray-300 mb-2">
            开始创作您的表盘
          </h3>
          <p className="text-gray-500">
            在左侧对话框中描述您想要的设计
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col bg-gray-900">
      {/* Header */}
      <div className="bg-gray-800 border-b border-gray-700 px-6 py-3 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-white">🎨 表盘预览</h2>
        <div className="flex items-center gap-2">
          <button
            onClick={toggleFullscreen}
            className="px-3 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors text-sm flex items-center gap-2"
            title={isFullscreen ? '退出全屏' : '全屏预览'}
          >
            {isFullscreen ? (
              <Minimize2 className="w-4 h-4" />
            ) : (
              <Maximize2 className="w-4 h-4" />
            )}
          </button>
          <button
            onClick={handleDownload}
            className="px-3 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors text-sm flex items-center gap-2"
          >
            <Download className="w-4 h-4" />
            下载 HTML
          </button>
        </div>
      </div>

      {/* Preview Area */}
      <div className="flex-1 flex items-center justify-center p-4 overflow-auto">
        {error ? (
          <div className="text-center">
            <div className="text-red-500 text-4xl mb-4">⚠️</div>
            <h3 className="text-lg font-semibold text-red-400 mb-2">
              预览错误
            </h3>
            <p className="text-gray-400 text-sm">{error}</p>
          </div>
        ) : (
          <div
            className={`bg-white rounded-lg shadow-2xl ${
              isFullscreen ? 'w-full h-full' : 'w-full h-full max-w-[600px] max-h-[600px]'
            }`}
            style={{
              aspectRatio: '1 / 1',
            }}
          >
            <iframe
              ref={iframeRef}
              className="w-full h-full rounded-lg"
              title="WatchFace Preview"
              srcDoc={previewSrc}
              sandbox="allow-scripts allow-same-origin"
            />
          </div>
        )}
      </div>

      {/* Info */}
      <div className="bg-gray-800 border-t border-gray-700 px-6 py-2 text-xs text-gray-400">
        <div className="flex items-center justify-between">
          <span>实时预览 - 代码自动运行</span>
          <span>预览尺寸: {isFullscreen ? '全屏' : '自适应'}</span>
        </div>
      </div>
    </div>
  );
}

