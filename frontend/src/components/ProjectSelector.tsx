import React, { useState, useEffect, useRef } from 'react';
import { ChevronDown, FolderOpen, Plus, Clock, RefreshCw, Trash2 } from 'lucide-react';
import { getProjects, getProject, deleteProject, deleteAllProjects } from '../api/client';
import { useAppStore } from '../store/useAppStore';

interface Project {
  project_id: string;
  session_id: string;
  watchface_name: string;
  watchface_id: number;
  mode: string;
  created_at: string;
  updated_at: string;
  last_instruction: string;
  generation_count: number;
}

const ProjectSelector: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(false);
  const [loadingProject, setLoadingProject] = useState<string | null>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const { projectId, loadProject, resetProject, setError } = useAppStore();

  // 获取项目列表
  const fetchProjects = async () => {
    setLoading(true);
    try {
      const response = await getProjects();
      if (response?.success) {
        setProjects(response.projects || []);
      }
    } catch (error) {
      console.error('获取项目列表失败:', error);
    } finally {
      setLoading(false);
    }
  };

  // 首次加载时获取项目列表
  useEffect(() => {
    fetchProjects();
  }, []);

  // 点击外部关闭下拉框
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // 加载项目
  const handleLoadProject = async (project: Project) => {
    setLoadingProject(project.project_id);
    try {
      const response = await getProject(project.project_id);
      if (response?.success) {
        loadProject(response);
        setIsOpen(false);
      } else {
        setError('加载项目失败');
      }
    } catch (error: any) {
      setError(`加载项目失败: ${error.message}`);
    } finally {
      setLoadingProject(null);
    }
  };

  // 创建新项目
  const handleNewProject = () => {
    resetProject();
    setIsOpen(false);
  };

  // 删除单个项目
  const handleDeleteProject = async (project: Project, e: React.MouseEvent) => {
    e.stopPropagation(); // 阻止事件冒泡
    
    if (!confirm(`确定要删除项目 "${project.watchface_name}" 吗？此操作不可恢复！`)) {
      return;
    }
    
    try {
      const response = await deleteProject(project.project_id);
      if (response?.success) {
        // 如果删除的是当前项目，重置状态
        if (project.project_id === projectId) {
          resetProject();
        }
        // 刷新列表
        await fetchProjects();
      }
    } catch (error: any) {
      setError(`删除项目失败: ${error.message}`);
    }
  };

  // 删除所有项目
  const handleDeleteAll = async () => {
    if (!confirm(`确定要删除所有 ${projects.length} 个项目吗？此操作不可恢复！`)) {
      return;
    }
    
    try {
      const response = await deleteAllProjects();
      if (response?.success) {
        alert(`${response.message}`);
        resetProject();
        await fetchProjects();
      }
    } catch (error: any) {
      setError(`批量删除失败: ${error.message}`);
    }
  };

  // 格式化时间
  const formatTime = (isoString: string) => {
    if (!isoString) return '';
    try {
      const date = new Date(isoString);
      const now = new Date();
      const diff = now.getTime() - date.getTime();
      const hours = Math.floor(diff / (1000 * 60 * 60));
      const days = Math.floor(hours / 24);
      
      if (days > 0) return `${days}天前`;
      if (hours > 0) return `${hours}小时前`;
      return '刚刚';
    } catch {
      return '';
    }
  };

  // 获取当前项目名称
  const currentProjectName = projects.find(p => p.project_id === projectId)?.watchface_name || '新建项目';

  return (
    <div className="relative" ref={dropdownRef}>
      {/* 下拉按钮 */}
      <button
        onClick={() => {
          if (!isOpen) fetchProjects(); // 打开时刷新列表
          setIsOpen(!isOpen);
        }}
        className="flex items-center gap-2 px-4 py-2 bg-white/10 hover:bg-white/20 rounded-lg transition-colors text-white"
      >
        <FolderOpen className="w-4 h-4" />
        <span className="max-w-[200px] truncate">
          {projectId ? currentProjectName : '选择项目'}
        </span>
        <ChevronDown className={`w-4 h-4 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {/* 下拉菜单 */}
      {isOpen && (
        <div className="absolute top-full left-1/2 -translate-x-1/2 mt-2 w-80 bg-white rounded-xl shadow-xl border border-gray-200 overflow-hidden z-50">
          {/* 头部 */}
          <div className="px-4 py-3 bg-gray-50 border-b border-gray-200 flex items-center justify-between">
            <span className="font-medium text-gray-700">📂 历史项目</span>
            <div className="flex items-center gap-2">
              <button
                onClick={() => fetchProjects()}
                className="p-1.5 hover:bg-gray-200 rounded-lg transition-colors"
                title="刷新列表"
              >
                <RefreshCw className={`w-4 h-4 text-gray-500 ${loading ? 'animate-spin' : ''}`} />
              </button>
              {projects.length > 0 && (
                <button
                  onClick={handleDeleteAll}
                  className="p-1.5 hover:bg-red-100 rounded-lg transition-colors"
                  title="删除所有项目"
                >
                  <Trash2 className="w-4 h-4 text-red-500" />
                </button>
              )}
              <button
                onClick={handleNewProject}
                className="flex items-center gap-1.5 px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm transition-colors"
              >
                <Plus className="w-3.5 h-3.5" />
                新建
              </button>
            </div>
          </div>

          {/* 项目列表 */}
          <div className="max-h-80 overflow-y-auto">
            {loading ? (
              <div className="px-4 py-8 text-center text-gray-500">
                <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2" />
                加载中...
              </div>
            ) : projects.length === 0 ? (
              <div className="px-4 py-8 text-center text-gray-500">
                <FolderOpen className="w-8 h-8 mx-auto mb-2 opacity-50" />
                <p>暂无历史项目</p>
                <p className="text-sm mt-1">开始创建您的第一个表盘吧！</p>
              </div>
            ) : (
              projects.map((project) => (
                <div
                  key={project.project_id}
                  className={`relative group w-full px-4 py-3 hover:bg-gray-50 transition-colors border-b border-gray-100 last:border-b-0 ${
                    project.project_id === projectId ? 'bg-blue-50' : ''
                  } ${loadingProject === project.project_id ? 'opacity-50' : ''}`}
                >
                  <button
                    onClick={() => handleLoadProject(project)}
                    disabled={loadingProject === project.project_id}
                    className="w-full text-left"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1 min-w-0 pr-8">
                        <div className="flex items-center gap-2">
                          <span className={`font-medium ${project.project_id === projectId ? 'text-blue-600' : 'text-gray-800'}`}>
                            {project.watchface_name}
                          </span>
                          {project.project_id === projectId && (
                            <span className="px-1.5 py-0.5 bg-blue-100 text-blue-700 rounded text-xs">
                              当前
                            </span>
                          )}
                        </div>
                        <p className="text-sm text-gray-500 truncate mt-1">
                          {project.last_instruction || '无描述'}
                        </p>
                      </div>
                      <div className="flex flex-col items-end text-xs text-gray-400 ml-2 flex-shrink-0">
                        <div className="flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          {formatTime(project.updated_at)}
                        </div>
                        <span className="mt-1">
                          迭代 {project.generation_count} 次
                        </span>
                      </div>
                    </div>
                    {loadingProject === project.project_id && (
                      <div className="mt-2 flex items-center gap-2 text-sm text-blue-600">
                        <RefreshCw className="w-3 h-3 animate-spin" />
                        加载中...
                      </div>
                    )}
                  </button>
                  
                  {/* 删除按钮 */}
                  <button
                    onClick={(e) => handleDeleteProject(project, e)}
                    className="absolute top-3 right-3 p-1.5 opacity-0 group-hover:opacity-100 hover:bg-red-100 rounded transition-all"
                    title="删除项目"
                  >
                    <Trash2 className="w-3.5 h-3.5 text-red-500" />
                  </button>
                </div>
              ))
            )}
          </div>

          {/* 底部提示 */}
          {projects.length > 0 && (
            <div className="px-4 py-2 bg-gray-50 border-t border-gray-200 text-xs text-gray-500">
              共 {projects.length} 个项目 · 点击加载历史项目继续编辑
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ProjectSelector;

