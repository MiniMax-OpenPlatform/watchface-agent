import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';

export interface WatchfaceAsset {
  asset_type: string;
  filename: string;
  stored_filename: string;
  file_path?: string;
  file_size: number;
  mime_type: string;
}

export interface WatchfaceAssets {
  background_round?: WatchfaceAsset;
  background_square?: WatchfaceAsset;
  pointer_hour?: WatchfaceAsset;
  pointer_minute?: WatchfaceAsset;
  pointer_second?: WatchfaceAsset;
  digits: WatchfaceAsset[];
  week_images: WatchfaceAsset[];
  decorations: WatchfaceAsset[];
  preview_image?: WatchfaceAsset;
}

export interface WatchfaceConfig {
  watchface_name: string;
}

export interface ProjectFile {
  path: string;
  content: string;
  language: string;
}

export interface ConversationMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  reasoning?: string;
  codeSnapshot?: string;
  rawContent?: string;  // Agent返回的完整原始内容
  raw_content?: string; // 兼容后端的snake_case命名
}

interface AppState {
  // 会话和项目
  sessionId: string;
  projectId: string | null;
  
  // 素材
  assets: WatchfaceAssets;
  
  // 配置
  config: WatchfaceConfig;
  
  // 项目文件
  files: ProjectFile[];
  fileTree: any;
  selectedFile: ProjectFile | null;
  
  // 对话
  conversation: ConversationMessage[];
  lastReasoning: string;
  lastGeneratedCode: string;
  
  // UI状态
  isGenerating: boolean;
  error: string | null;
  
  // Actions
  setSessionId: (id: string) => void;
  setProjectId: (id: string | null) => void;
  addAsset: (asset: WatchfaceAsset) => void;
  removeAsset: (assetType: string, filename: string) => void;  // 新增：删除素材
  clearAssets: () => void;  // 新增：清空所有素材
  setAssets: (assets: WatchfaceAssets) => void;
  updateConfig: (config: Partial<WatchfaceConfig>) => void;
  setConfig: (config: WatchfaceConfig) => void;
  setFiles: (files: ProjectFile[], fileTree: any) => void;
  setSelectedFile: (file: ProjectFile | null) => void;
  addMessage: (message: ConversationMessage) => void;
  setConversation: (messages: ConversationMessage[]) => void;
  setLastReasoning: (reasoning: string) => void;
  setLastGeneratedCode: (code: string) => void;
  setIsGenerating: (isGenerating: boolean) => void;
  setError: (error: string | null) => void;
  resetProject: () => void;
  loadProject: (projectData: any) => void;
}

const defaultConfig: WatchfaceConfig = {
  watchface_name: 'AI生成表盘',
};

const defaultAssets: WatchfaceAssets = {
  digits: [],
  week_images: [],
  decorations: [],
};

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      // 初始状态
      sessionId: `session_${Date.now()}`,
      projectId: null,
      assets: defaultAssets,
      config: defaultConfig,
      files: [],
      fileTree: null,
      selectedFile: null,
      conversation: [],
      lastReasoning: '',
      lastGeneratedCode: '',
      isGenerating: false,
      error: null,

      // Actions
      setSessionId: (id) => set({ sessionId: id }),
      
      setProjectId: (id) => set({ projectId: id }),
      
      addAsset: (asset) => set((state) => {
    const newAssets = { ...state.assets };
    const type = asset.asset_type;
    
    // 根据类型存储素材
    if (type === 'background_round') {
      newAssets.background_round = asset;
    } else if (type === 'background_square') {
      newAssets.background_square = asset;
    } else if (type === 'pointer_hour') {
      newAssets.pointer_hour = asset;
    } else if (type === 'pointer_minute') {
      newAssets.pointer_minute = asset;
    } else if (type === 'pointer_second') {
      newAssets.pointer_second = asset;
    } else if (type.startsWith('digit_')) {
      // 数字素材
      const existing = newAssets.digits.filter(d => d.asset_type !== type);
      newAssets.digits = [...existing, asset];
    } else if (type.startsWith('week_')) {
      // 星期素材
      const existing = newAssets.week_images.filter(w => w.asset_type !== type);
      newAssets.week_images = [...existing, asset];
    } else if (type === 'preview') {
      newAssets.preview_image = asset;
    } else if (type === 'decoration') {
      newAssets.decorations.push(asset);
    }
    
    return { assets: newAssets };
  }),

  removeAsset: (assetType, filename) => set((state) => {
    const newAssets = { ...state.assets };
    
    // 根据类型删除素材
    if (assetType === 'background_round') {
      newAssets.background_round = undefined;
    } else if (assetType === 'background_square') {
      newAssets.background_square = undefined;
    } else if (assetType === 'pointer_hour') {
      newAssets.pointer_hour = undefined;
    } else if (assetType === 'pointer_minute') {
      newAssets.pointer_minute = undefined;
    } else if (assetType === 'pointer_second') {
      newAssets.pointer_second = undefined;
    } else if (assetType.startsWith('digit_')) {
      newAssets.digits = newAssets.digits.filter(d => d.stored_filename !== filename);
    } else if (assetType.startsWith('week_')) {
      newAssets.week_images = newAssets.week_images.filter(w => w.stored_filename !== filename);
    } else if (assetType === 'preview') {
      newAssets.preview_image = undefined;
    } else if (assetType === 'decoration') {
      newAssets.decorations = newAssets.decorations.filter(d => d.stored_filename !== filename);
    }
    
    return { assets: newAssets };
  }),

  clearAssets: () => set({ assets: { ...defaultAssets } }),
  
  updateConfig: (updates) => set((state) => ({
    config: { ...state.config, ...updates },
  })),
  
  setFiles: (files, fileTree) => set({ files, fileTree }),
  
  setSelectedFile: (file) => set({ selectedFile: file }),
  
  addMessage: (message) => set((state) => ({
    conversation: [...state.conversation, message],
  })),
  
  setLastReasoning: (reasoning) => set({ lastReasoning: reasoning }),
  
  setLastGeneratedCode: (code) => set({ lastGeneratedCode: code }),
  
  setIsGenerating: (isGenerating) => set({ isGenerating }),
  
  setError: (error) => set({ error }),
  
  resetProject: () => set({
    projectId: null,
    files: [],
    fileTree: null,
    selectedFile: null,
    conversation: [],
    lastReasoning: '',
    lastGeneratedCode: '',
    error: null,
    assets: { ...defaultAssets },  // 🆕 新建项目时清空素材
  }),
  
  setAssets: (assets) => set({ assets }),
  
  setConfig: (config) => set({ config }),
  
  setConversation: (messages) => set({ conversation: messages }),
  
  loadProject: (projectData) => {
    const files = projectData.files || [];
    // 自动选择 index.html 文件作为默认显示
    const indexHtml = files.find((f: any) => f.path.includes('index.html'));
    
    set({
      projectId: projectData.project_id,
      files: files,
      fileTree: projectData.file_tree,
      selectedFile: indexHtml || null,
      conversation: projectData.conversation || [],
      config: projectData.config ? { ...defaultConfig, ...projectData.config } : defaultConfig,
      assets: projectData.assets ? { ...defaultAssets, ...projectData.assets } : defaultAssets,
      lastReasoning: '',
      lastGeneratedCode: indexHtml?.content || '',
      error: null,
    });
  },
    }),
    {
      name: 'watchface-agent-storage', // localStorage key
      storage: createJSONStorage(() => localStorage),
      
      // 选择要持久化的字段
      partialize: (state) => ({
        sessionId: state.sessionId,
        projectId: state.projectId,
        config: state.config,
        assets: state.assets,
        files: state.files,
        fileTree: state.fileTree,
        selectedFile: state.selectedFile,
        conversation: state.conversation,
        // 不持久化：isGenerating, error（这些是临时状态）
      }),
    }
  )
);
