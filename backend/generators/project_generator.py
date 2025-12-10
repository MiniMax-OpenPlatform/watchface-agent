"""
表盘项目文件生成器 - 生成标准 HTML 项目
"""

import json
from pathlib import Path
from typing import Dict, List, Any
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.project import WatchfaceConfig, ProjectMetadata
from models.assets import WatchfaceAssets


class WatchfaceProjectGenerator:
    """表盘项目生成器 - 生成 HTML 项目"""
    
    def __init__(self, metadata: ProjectMetadata):
        self.metadata = metadata
        self.config = metadata.config
        self.assets = metadata.assets
    
    def generate_file_structure(self, html_content: str) -> Dict[str, str]:
        """
        生成文件结构
        
        Args:
            html_content: index.html 文件内容
            
        Returns:
            文件路径 -> 文件内容的字典
        """
        files = {
            "index.html": html_content,
            "README.md": self._generate_readme(),
        }
        
        # 添加素材文件路径
        asset_files = self.assets.get_all_filenames()
        for asset_filename in asset_files:
            files[f"assets/{asset_filename}"] = "[BINARY_FILE]"
        
        return files
    
    def _generate_readme(self) -> str:
        """生成 README 文件"""
        asset_count = len(self.assets.get_all_filenames())
        
        return f"""# {self.config.watchface_name}

## AI 生成的智能表盘

使用 AI 智能生成的表盘 UI，支持多种样式和功能。

### 运行方式

直接在浏览器中打开 `index.html` 文件即可预览表盘。

### 项目特点

- ✨ AI 智能生成代码
- 🎨 灵活的样式定制
- 📱 响应式设计
- ⚡ 纯前端实现，无需服务器

### 素材

- 素材文件数量: {asset_count}
- 素材目录: `assets/`

### 技术栈

- HTML5
- CSS3
- JavaScript (ES6+)
- SVG / Canvas（可选）

### 自定义

可以通过编辑 `index.html` 来调整表盘样式和功能。
"""
    
    def generate_file_tree(self, files: Dict[str, str]) -> Dict[str, Any]:
        """生成文件树结构"""
        tree = {
            "name": "project",
            "type": "folder",
            "path": "",
            "children": []
        }
        
        sorted_paths = sorted(files.keys())
        
        for file_path in sorted_paths:
            parts = file_path.split('/')
            current = tree
            
            for i, part in enumerate(parts):
                is_file = (i == len(parts) - 1)
                
                existing = None
                if "children" in current:
                    existing = next(
                        (child for child in current["children"] if child["name"] == part),
                        None
                    )
                
                if existing:
                    current = existing
                else:
                    node = {
                        "name": part,
                        "type": "file" if is_file else "folder",
                        "path": "/".join(parts[:i+1])
                    }
                    
                    if not is_file:
                        node["children"] = []
                    
                    current.setdefault("children", []).append(node)
                    current = node
        
        return tree
    
    def detect_language(self, file_path: str) -> str:
        """根据文件路径检测语言类型"""
        if file_path.endswith('.html'):
            return 'html'
        elif file_path.endswith('.json'):
            return 'json'
        elif file_path.endswith('.js'):
            return 'javascript'
        elif file_path.endswith('.css'):
            return 'css'
        elif file_path.endswith('.md'):
            return 'markdown'
        else:
            return 'plaintext'


# 保持向后兼容
VivoWatchfaceProjectGenerator = WatchfaceProjectGenerator
