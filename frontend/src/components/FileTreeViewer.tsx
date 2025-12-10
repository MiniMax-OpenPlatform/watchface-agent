import React, { useState } from 'react';
import { ChevronRight, ChevronDown, Folder, FolderOpen, File, FileCode, FileJson } from 'lucide-react';

interface FileTreeNode {
  name: string;
  type: 'file' | 'folder';
  path: string;
  children?: FileTreeNode[];
}

interface ProjectFile {
  path: string;
  content: string;
  language: string;
}

interface FileTreeViewerProps {
  fileTree: FileTreeNode;
  files: ProjectFile[];
  onFileSelect: (file: ProjectFile) => void;
  selectedPath?: string;
}

const FileTreeViewer: React.FC<FileTreeViewerProps> = ({ 
  fileTree, 
  files, 
  onFileSelect,
  selectedPath 
}) => {
  const [expandedFolders, setExpandedFolders] = useState<Set<string>>(new Set(['src']));

  const toggleFolder = (path: string) => {
    setExpandedFolders(prev => {
      const newSet = new Set(prev);
      if (newSet.has(path)) {
        newSet.delete(path);
      } else {
        newSet.add(path);
      }
      return newSet;
    });
  };

  const getFileIcon = (filename: string) => {
    if (filename.endsWith('.ux')) return <FileCode className="w-4 h-4 text-blue-500" />;
    if (filename.endsWith('.json')) return <FileJson className="w-4 h-4 text-yellow-500" />;
    return <File className="w-4 h-4 text-gray-500" />;
  };

  const renderNode = (node: FileTreeNode, level: number = 0): React.ReactNode => {
    const isExpanded = expandedFolders.has(node.path);
    const isSelected = selectedPath === node.path;

    if (node.type === 'folder') {
      return (
        <div key={node.path}>
          <div
            className={`flex items-center gap-1 py-1 px-2 rounded cursor-pointer hover:bg-gray-100 ${
              isSelected ? 'bg-blue-50' : ''
            }`}
            style={{ paddingLeft: `${level * 16 + 8}px` }}
            onClick={() => toggleFolder(node.path)}
          >
            {isExpanded ? (
              <ChevronDown className="w-4 h-4 text-gray-600" />
            ) : (
              <ChevronRight className="w-4 h-4 text-gray-600" />
            )}
            {isExpanded ? (
              <FolderOpen className="w-4 h-4 text-blue-500" />
            ) : (
              <Folder className="w-4 h-4 text-blue-500" />
            )}
            <span className="text-sm font-medium text-gray-800">{node.name}</span>
          </div>
          {isExpanded && node.children && (
            <div>
              {node.children.map(child => renderNode(child, level + 1))}
            </div>
          )}
        </div>
      );
    }

    // 文件节点
    const file = files.find(f => f.path === node.path);
    
    return (
      <div
        key={node.path}
        className={`flex items-center gap-1 py-1 px-2 rounded cursor-pointer hover:bg-gray-100 ${
          isSelected ? 'bg-blue-50 font-semibold' : ''
        }`}
        style={{ paddingLeft: `${level * 16 + 24}px` }}
        onClick={() => file && onFileSelect(file)}
      >
        {getFileIcon(node.name)}
        <span className="text-sm text-gray-700">{node.name}</span>
        {node.path.includes('[BINARY_FILE]') && (
          <span className="text-xs text-gray-400 ml-1">(binary)</span>
        )}
      </div>
    );
  };

  return (
    <div className="file-tree-viewer h-full bg-white rounded-lg shadow p-4 overflow-y-auto flex flex-col">
      <h3 className="text-lg font-bold mb-3 flex items-center gap-2 flex-shrink-0">
        <Folder className="w-5 h-5" />
        📁 项目结构
      </h3>
      <div className="text-sm flex-1 overflow-y-auto">
        {renderNode(fileTree)}
      </div>
      
      <div className="mt-4 pt-4 border-t border-gray-200 flex-shrink-0">
        <div className="text-xs text-gray-500 space-y-1">
          <p>💡 点击文件查看代码</p>
          <p>💡 [BINARY_FILE] 标记的是素材文件</p>
        </div>
      </div>
    </div>
  );
};

export default FileTreeViewer;

