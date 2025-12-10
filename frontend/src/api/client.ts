/**
 * API Client for WatchFace Code Agent Backend
 */
import axios from 'axios';
import { getClientId } from '../utils/clientId';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://10.11.17.19:10030';

export interface GenerateRequest {
  instruction: string;
  current_code?: string;
  conversation_history?: ConversationMessage[];
  session_id?: string;
}

export interface ConversationMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp?: string;
  reasoning?: string;  // Agent的思考过程
  codeSnapshot?: string;  // 生成的代码快照
}

export interface GenerateResponse {
  success: boolean;
  code?: string;
  reasoning?: string;
  diff?: CodeDiff;
  message: string;
  stats?: {
    lines: number;
    characters?: number;
    changes?: number;
  };
  timestamp: string;
}

export interface CodeDiff {
  added_lines: { line_number: number; content: string }[];
  removed_lines: { line_number: number; content: string }[];
  total_changes: number;
}

export interface SessionState {
  session_id: string;
  current_code?: string;
  conversation_history: ConversationMessage[];
  created_at: string;
  updated_at: string;
}

class APIClient {
  private baseURL: string;

  constructor() {
    this.baseURL = API_BASE_URL;
    console.log('🔗 API Client initialized:', this.baseURL);
  }

  /**
   * 获取带client_id的请求headers
   */
  private getHeaders(additionalHeaders?: any) {
    const clientId = getClientId();
    return {
      'X-Client-ID': clientId,
      ...additionalHeaders,
    };
  }

  /**
   * 上传素材文件
   */
  async uploadAsset(file: File, assetType: string, sessionId: string): Promise<any> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('asset_type', assetType);
    formData.append('session_id', sessionId);

    const response = await axios.post(`${this.baseURL}/api/upload-asset`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  /**
   * 批量上传素材（ZIP文件）
   */
  async uploadBatchAssets(file: File, assetCategory: string, sessionId: string): Promise<any> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('asset_category', assetCategory);
    formData.append('session_id', sessionId);

    const response = await axios.post(`${this.baseURL}/api/upload-batch-assets`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      timeout: 60000, // ZIP文件可能较大，延长超时时间
    });
    return response.data;
  }

  /**
   * 生成新项目
   */
  async generateProject(request: any): Promise<any> {
    try {
      console.log('📤 Sending generate project request');

      const response = await axios.post(
        `${this.baseURL}/api/generate-project`,
        request,
        {
          timeout: 180000, // 3分钟超时
          headers: this.getHeaders(),
        }
      );

      console.log('✅ Project generated:', response.data.project_id);
      return response.data;
    } catch (error: any) {
      console.error('❌ Generate project failed:', error);
      this._handleError(error);
    }
  }

  /**
   * 编辑现有项目
   */
  async editProject(request: any): Promise<any> {
    try {
      console.log('📤 Sending edit project request');

      const response = await axios.post(
        `${this.baseURL}/api/edit-project`,
        request,
        {
          timeout: 180000,
          headers: this.getHeaders(),
        }
      );

      console.log('✅ Project edited:', response.data.project_id);
      return response.data;
    } catch (error: any) {
      console.error('❌ Edit project failed:', error);
      this._handleError(error);
    }
  }

  /**
   * 下载项目
   */
  async downloadProject(projectId: string): Promise<Blob> {
    const response = await axios.get(
      `${this.baseURL}/api/download-project/${projectId}`,
      {
        responseType: 'blob',
      }
    );
    return response.data;
  }

  /**
   * 获取历史项目列表
   */
  async getProjects(sessionId?: string): Promise<any> {
    try {
      const url = sessionId 
        ? `${this.baseURL}/api/projects?session_id=${sessionId}`
        : `${this.baseURL}/api/projects`;
      
      const response = await axios.get(url);
      console.log('📋 获取到项目列表:', response.data.total);
      return response.data;
    } catch (error: any) {
      console.error('❌ 获取项目列表失败:', error);
      this._handleError(error);
    }
  }

  /**
   * 获取单个项目详情
   */
  async getProject(projectId: string): Promise<any> {
    try {
      const response = await axios.get(`${this.baseURL}/api/project/${projectId}`);
      console.log('📂 获取项目详情:', projectId);
      return response.data;
    } catch (error: any) {
      console.error('❌ 获取项目详情失败:', error);
      this._handleError(error);
    }
  }

  /**
   * 删除单个项目
   */
  async deleteProject(projectId: string): Promise<any> {
    try {
      const response = await axios.delete(`${this.baseURL}/api/project/${projectId}`);
      console.log('🗑️ 删除项目:', projectId);
      return response.data;
    } catch (error: any) {
      console.error('❌ 删除项目失败:', error);
      this._handleError(error);
    }
  }

  /**
   * 删除所有项目
   */
  async deleteAllProjects(sessionId?: string): Promise<any> {
    try {
      const url = sessionId 
        ? `${this.baseURL}/api/projects?session_id=${sessionId}`
        : `${this.baseURL}/api/projects`;
      
      const response = await axios.delete(url);
      console.log('🗑️ 批量删除项目');
      return response.data;
    } catch (error: any) {
      console.error('❌ 批量删除项目失败:', error);
      this._handleError(error);
    }
  }

  /**
   * 删除单个素材文件
   */
  async deleteAsset(sessionId: string, filename: string): Promise<any> {
    try {
      const response = await axios.delete(`${this.baseURL}/api/asset/${sessionId}/${filename}`);
      console.log('🗑️ 删除素材:', filename);
      return response.data;
    } catch (error: any) {
      console.error('❌ 删除素材失败:', error);
      this._handleError(error);
    }
  }

  /**
   * 删除会话所有素材
   */
  async deleteAllAssets(sessionId: string): Promise<any> {
    try {
      const response = await axios.delete(`${this.baseURL}/api/assets/${sessionId}`);
      console.log('🗑️ 清空会话素材');
      return response.data;
    } catch (error: any) {
      console.error('❌ 清空素材失败:', error);
      this._handleError(error);
    }
  }

  /**
   * 生成或编辑表盘代码 (保留向后兼容)
   */
  async generateCode(request: GenerateRequest): Promise<GenerateResponse> {
    try {
      console.log('📤 Sending generate request:', {
        instruction: request.instruction,
        hasCurrentCode: !!request.current_code,
        sessionId: request.session_id,
      });

      const response = await axios.post<GenerateResponse>(
        `${this.baseURL}/api/generate`,
        request,
        {
          timeout: 180000,
        }
      );

      console.log('✅ Generate response received:', {
        success: response.data.success,
        codeLength: response.data.code?.length,
        hasReasoning: !!response.data.reasoning,
        hasDiff: !!response.data.diff,
      });

      return response.data;
    } catch (error: any) {
      console.error('❌ Generate request failed:', error);
      this._handleError(error);
    }
  }

  /**
   * 获取会话状态
   */
  async getSession(sessionId: string): Promise<SessionState> {
    const response = await axios.get<SessionState>(
      `${this.baseURL}/api/session/${sessionId}`
    );
    return response.data;
  }

  /**
   * 删除会话
   */
  async deleteSession(sessionId: string): Promise<void> {
    await axios.delete(`${this.baseURL}/api/session/${sessionId}`);
  }

  /**
   * 健康检查
   */
  async healthCheck(): Promise<{ status: string; timestamp: string }> {
    const response = await axios.get(`${this.baseURL}/health`);
    return response.data;
  }

  /**
   * 设置API Key
   */
  async setApiKey(clientId: string, apiKey: string): Promise<any> {
    try {
      console.log('💾 设置API Key...', clientId);
      const response = await axios.post(`${this.baseURL}/api/set-api-key`, {
        client_id: clientId,
        api_key: apiKey,
      }, {
        headers: this.getHeaders(),
      });
      return response.data;
    } catch (error) {
      this._handleError(error);
    }
  }

  /**
   * 获取API Key状态
   */
  async getApiKey(clientId: string): Promise<any> {
    try {
      console.log('🔍 获取API Key状态...', clientId);
      const response = await axios.get(`${this.baseURL}/api/get-api-key`, {
        params: { client_id: clientId },
        headers: this.getHeaders(),
      });
      return response.data;
    } catch (error) {
      this._handleError(error);
    }
  }

  /**
   * 测试API Key
   */
  async testApiKey(apiKey: string): Promise<any> {
    try {
      console.log('🧪 测试API Key...');
      const response = await axios.post(`${this.baseURL}/api/test-api-key`, {
        api_key: apiKey,
      }, {
        headers: this.getHeaders(),
      });
      return response.data;
    } catch (error) {
      this._handleError(error);
    }
  }

  /**
   * 统一错误处理
   */
  private _handleError(error: any): never {
    if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
      throw new Error('请求超时：AI生成代码时间较长，请稍后重试或简化指令');
    } else if (error.response) {
      throw new Error(`服务器错误: ${error.response.data?.detail || error.response.statusText}`);
    } else if (error.request) {
      throw new Error('无法连接到后端服务，请检查服务是否运行');
    } else {
      throw new Error(error.message || '未知错误');
    }
  }
}

// 导出便捷函数
export const uploadAsset = (file: File, assetType: string, sessionId: string) =>
  apiClient.uploadAsset(file, assetType, sessionId);

export const uploadBatchAssets = (file: File, assetCategory: string, sessionId: string) =>
  apiClient.uploadBatchAssets(file, assetCategory, sessionId);

export const generateProject = (request: any) =>
  apiClient.generateProject(request);

export const editProject = (request: any) =>
  apiClient.editProject(request);

export const downloadProject = (projectId: string) =>
  apiClient.downloadProject(projectId);

export const getProjects = (sessionId?: string) =>
  apiClient.getProjects(sessionId);

export const getProject = (projectId: string) =>
  apiClient.getProject(projectId);

export const deleteProject = (projectId: string) =>
  apiClient.deleteProject(projectId);

export const deleteAllProjects = (sessionId?: string) =>
  apiClient.deleteAllProjects(sessionId);

export const deleteAsset = (sessionId: string, filename: string) =>
  apiClient.deleteAsset(sessionId, filename);

export const deleteAllAssets = (sessionId: string) =>
  apiClient.deleteAllAssets(sessionId);

export const setApiKey = (clientId: string, apiKey: string) =>
  apiClient.setApiKey(clientId, apiKey);

export const getApiKey = (clientId: string) =>
  apiClient.getApiKey(clientId);

export const testApiKey = (apiKey: string) =>
  apiClient.testApiKey(apiKey);

// Export singleton instance
export const apiClient = new APIClient();

