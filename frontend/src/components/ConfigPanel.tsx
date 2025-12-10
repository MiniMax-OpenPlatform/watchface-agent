import React from 'react';
import { Settings, Lightbulb } from 'lucide-react';

export interface WatchfaceConfig {
  watchface_name: string;
}

interface ConfigPanelProps {
  config: WatchfaceConfig;
  onChange: (config: WatchfaceConfig) => void;
}

const ConfigPanel: React.FC<ConfigPanelProps> = ({ config, onChange }) => {
  const updateConfig = (updates: Partial<WatchfaceConfig>) => {
    onChange({ ...config, ...updates });
  };

  return (
    <div className="config-panel bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
        <Settings className="w-5 h-5" />
        ⚙️ 项目设置
      </h3>

      {/* 项目名称 */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-1">
          项目名称
        </label>
        <input
          type="text"
          value={config.watchface_name}
          onChange={(e) => updateConfig({ watchface_name: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="例如：极简指针表盘"
        />
        <p className="text-xs text-gray-500 mt-1">用于项目识别和保存</p>
      </div>

      {/* 使用提示 */}
      <div className="mt-6 pt-4 border-t border-gray-200">
        <h4 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
          <Lightbulb className="w-4 h-4" />
          智能指令示例
        </h4>
        <div className="text-xs text-gray-600 space-y-2 bg-gray-50 p-3 rounded">
          <p>💡 <strong>表盘类型：</strong>"生成一个指针表盘" 或 "创建一个数字表盘"</p>
          <p>💡 <strong>显示元素：</strong>"显示日期和星期" 或 "只显示时间"</p>
          <p>💡 <strong>样式风格：</strong>"简约风格" 或 "科技感" 或 "复古风"</p>
          <p>💡 <strong>配色方案：</strong>"深色背景" 或 "浅色主题" 或 "渐变效果"</p>
          <p>💡 <strong>特殊元素：</strong>"添加秒针" 或 "显示电量" 或 "天气信息"</p>
        </div>
        <p className="text-xs text-gray-500 mt-3 italic">
          ✨ Agent会智能理解您的自然语言指令，无需预设配置
        </p>
      </div>
    </div>
  );
};

export default ConfigPanel;

