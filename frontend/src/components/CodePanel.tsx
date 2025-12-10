/**
 * Code Panel Component - 代码查看和编辑（带语法高亮）
 */
import { useState, useEffect } from 'react';
import { Copy, Check, Download } from 'lucide-react';
import Editor from '@monaco-editor/react';

interface CodePanelProps {
  code: string;
  language?: string;
}

export default function CodePanel({ code, language = 'html' }: CodePanelProps) {
  const [copied, setCopied] = useState(false);
  const [editorError, setEditorError] = useState(false);
  const [editorLoaded, setEditorLoaded] = useState(false);

  // Timeout fallback: If Monaco doesn't load in 10 seconds, use plain text
  useEffect(() => {
    if (!editorLoaded && code) {
      const timeout = setTimeout(() => {
        if (!editorLoaded) {
          console.warn('⚠️ Monaco Editor failed to load, using fallback');
          setEditorError(true);
        }
      }, 10000); // 10 seconds timeout

      return () => clearTimeout(timeout);
    }
  }, [code, editorLoaded]);

  const handleCopy = async () => {
    if (!code) return;

    try {
      await navigator.clipboard.writeText(code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  const handleDownload = () => {
    if (!code) return;

    // 根据language类型确定文件扩展名
    const extMap: { [key: string]: string } = {
      'html': '.ux',
      'json': '.json',
      'javascript': '.js',
      'css': '.css',
    };
    const ext = extMap[language] || '.txt';

    const blob = new Blob([code], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `file_${Date.now()}${ext}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  if (!code) {
    return (
      <div className="flex-1 flex items-center justify-center bg-gray-900">
        <div className="text-center">
          <div className="text-6xl mb-4">💻</div>
          <h3 className="text-xl font-semibold text-gray-300 mb-2">
            暂无代码
          </h3>
          <p className="text-gray-500">
            生成表盘后可在此查看完整代码
          </p>
        </div>
      </div>
    );
  }

  const lineCount = code.split('\n').length;
  const charCount = code.length;

  return (
    <div className="h-full flex flex-col bg-gray-900">
      {/* Header */}
      <div className="bg-gray-800 border-b border-gray-700 px-6 py-3 flex items-center justify-between flex-shrink-0">
        <div>
          <h2 className="text-lg font-semibold">💻 代码预览</h2>
          <p className="text-xs text-gray-400 mt-1">
            {lineCount} 行 • {charCount} 字符
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={handleCopy}
            className="px-3 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors text-sm flex items-center gap-2"
          >
            {copied ? (
              <>
                <Check className="w-4 h-4 text-green-400" />
                已复制
              </>
            ) : (
              <>
                <Copy className="w-4 h-4" />
                复制代码
              </>
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

      {/* Code Display - .ux文件用纯文本，其他用Monaco */}
      <div className="flex-1 min-h-0 overflow-hidden">
        {/* .ux文件直接显示纯文本，不高亮 */}
        {language === 'html' || editorError ? (
          <div className="h-full overflow-y-auto bg-gray-900">
            <pre className="p-6 text-sm font-mono text-gray-300 leading-relaxed whitespace-pre-wrap">
              {code}
            </pre>
          </div>
        ) : (
          // JSON等其他文件使用Monaco Editor
          <Editor
            height="100%"
            language={language}
            value={code}
            theme="vs-dark"
            loading={
              <div className="flex items-center justify-center h-full bg-gray-900">
                <div className="text-center">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
                  <p className="text-gray-400">加载编辑器...</p>
                </div>
              </div>
            }
            onMount={() => {
              console.log('✅ Monaco Editor mounted successfully');
              setEditorLoaded(true);
              setEditorError(false);
            }}
            options={{
              readOnly: true,
              minimap: { enabled: true },
              scrollBeyondLastLine: false,
              fontSize: 13,
              lineNumbers: 'on',
              wordWrap: 'on',
              automaticLayout: true,
              scrollbar: {
                vertical: 'visible',
                horizontal: 'visible',
                useShadows: false,
                verticalScrollbarSize: 12,
                horizontalScrollbarSize: 12,
              },
              overviewRulerLanes: 0,
              hideCursorInOverviewRuler: true,
              renderLineHighlight: 'none',
            }}
          />
        )}
      </div>

      {/* Info */}
      <div className="bg-gray-800 border-t border-gray-700 px-6 py-2 text-xs text-gray-400 flex-shrink-0">
        <div className="flex items-center justify-between">
          <span>
            {language === 'html' && 'vivo BlueOS .ux文件 - 单文件组件格式'}
            {language === 'json' && 'JSON配置文件'}
            {language === 'javascript' && 'JavaScript代码'}
            {!['html', 'json', 'javascript'].includes(language) && '代码文件'}
          </span>
          <span className="font-mono">{language.toUpperCase()}</span>
        </div>
      </div>
    </div>
  );
}

