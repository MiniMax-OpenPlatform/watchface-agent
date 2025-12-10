import React, { useState, useEffect } from 'react';
import { Key, X, Check, AlertCircle, Info } from 'lucide-react';
import { getClientId } from '../utils/clientId';
import { setApiKey, getApiKey, testApiKey } from '../api/client';

interface ApiKeySettingsProps {
  isOpen: boolean;
  onClose: () => void;
}

const ApiKeySettings: React.FC<ApiKeySettingsProps> = ({ isOpen, onClose }) => {
  const [apiKey, setApiKeyInput] = useState('');
  const [currentKey, setCurrentKey] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [testing, setTesting] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error' | 'info'; text: string } | null>(null);
  const [clientId, setClientId] = useState('');

  // 加载当前的API Key状态
  useEffect(() => {
    if (isOpen) {
      const id = getClientId();
      setClientId(id);
      loadCurrentKey(id);
    }
  }, [isOpen]);

  const loadCurrentKey = async (id: string) => {
    try {
      const response = await getApiKey(id);
      if (response.has_key) {
        setCurrentKey(response.key_preview || '已设置');
      } else {
        setCurrentKey(null);
      }
    } catch (error) {
      console.error('获取API Key状态失败:', error);
    }
  };

  const handleSave = async () => {
    if (!apiKey.trim()) {
      setMessage({ type: 'error', text: '请输入API Key' });
      return;
    }

    setLoading(true);
    setMessage(null);

    try {
      const response = await setApiKey(clientId, apiKey.trim());
      
      if (response.success) {
        setMessage({ type: 'success', text: '✅ API Key保存成功！' });
        setCurrentKey(response.key_preview || '已设置');
        setApiKeyInput('');
        
        // 3秒后关闭
        setTimeout(() => {
          onClose();
        }, 1500);
      } else {
        setMessage({ type: 'error', text: `❌ ${response.message || '保存失败'}` });
      }
    } catch (error: any) {
      setMessage({ type: 'error', text: `❌ 保存失败: ${error.message}` });
    } finally {
      setLoading(false);
    }
  };

  const handleTest = async () => {
    if (!apiKey.trim()) {
      setMessage({ type: 'error', text: '请先输入API Key' });
      return;
    }

    setTesting(true);
    setMessage(null);

    try {
      const response = await testApiKey(apiKey.trim());
      
      if (response.success) {
        setMessage({ type: 'success', text: '✅ API Key验证成功！' });
      } else {
        setMessage({ type: 'error', text: `❌ ${response.message || '验证失败'}` });
      }
    } catch (error: any) {
      setMessage({ type: 'error', text: `❌ 验证失败: ${error.message}` });
    } finally {
      setTesting(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <div className="flex items-center gap-3">
            <Key className="w-6 h-6 text-blue-600" />
            <h2 className="text-xl font-bold text-gray-800">API Key 设置</h2>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-4">
          {/* 客户端ID显示 */}
          <div className="bg-gray-50 p-4 rounded-md">
            <div className="flex items-center gap-2 mb-2">
              <Info className="w-4 h-4 text-blue-600" />
              <span className="text-sm font-medium text-gray-700">客户端标识</span>
            </div>
            <code className="text-xs text-gray-600 break-all">{clientId}</code>
          </div>

          {/* 当前状态 */}
          {currentKey && (
            <div className="bg-green-50 border border-green-200 p-4 rounded-md">
              <div className="flex items-center gap-2">
                <Check className="w-5 h-5 text-green-600" />
                <span className="text-sm text-green-800">
                  当前已设置API Key: <code className="text-xs">{currentKey}</code>
                </span>
              </div>
            </div>
          )}

          {/* API Key输入 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              MiniMax API Key
            </label>
            <input
              type="password"
              value={apiKey}
              onChange={(e) => setApiKeyInput(e.target.value)}
              placeholder="请输入您的MiniMax API Key"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all"
            />
            <p className="mt-2 text-xs text-gray-500">
              💡 您的API Key将仅在本浏览器中使用，不会分享给其他用户
            </p>
          </div>

          {/* 使用说明 */}
          <div className="bg-blue-50 border border-blue-200 p-4 rounded-md">
            <h3 className="text-sm font-semibold text-blue-800 mb-2">📖 如何获取API Key？</h3>
            <ol className="text-xs text-blue-700 space-y-1 list-decimal list-inside">
              <li>访问 <a href="https://platform.minimaxi.com/" target="_blank" rel="noopener noreferrer" className="underline">MiniMax开放平台</a></li>
              <li>注册或登录账号</li>
              <li>进入控制台，创建API Key</li>
              <li>复制API Key并粘贴到上方输入框</li>
            </ol>
          </div>

          {/* 消息提示 */}
          {message && (
            <div className={`p-4 rounded-md flex items-center gap-2 ${
              message.type === 'success' ? 'bg-green-50 text-green-800 border border-green-200' :
              message.type === 'error' ? 'bg-red-50 text-red-800 border border-red-200' :
              'bg-blue-50 text-blue-800 border border-blue-200'
            }`}>
              <AlertCircle className="w-5 h-5 flex-shrink-0" />
              <span className="text-sm">{message.text}</span>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end gap-3 p-6 border-t bg-gray-50">
          <button
            onClick={handleTest}
            disabled={testing || !apiKey.trim()}
            className="px-4 py-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {testing ? '验证中...' : '测试连接'}
          </button>
          <button
            onClick={onClose}
            className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
          >
            取消
          </button>
          <button
            onClick={handleSave}
            disabled={loading || !apiKey.trim()}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            {loading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                保存中...
              </>
            ) : (
              '保存'
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ApiKeySettings;

