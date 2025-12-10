"""
API Key管理器 - 管理客户端ID和API Key的映射关系
简单的JSON文件存储实现
"""

import json
from pathlib import Path
from typing import Optional, Dict
import hashlib
from datetime import datetime


# API Key存储文件路径
API_KEYS_FILE = Path(__file__).parent.parent.parent / "storage" / "api_keys.json"


class ApiKeyManager:
    """API Key管理器"""
    
    def __init__(self):
        self.storage_file = API_KEYS_FILE
        self._ensure_storage_file()
    
    def _ensure_storage_file(self):
        """确保存储文件存在"""
        self.storage_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.storage_file.exists():
            self._save_data({})
    
    def _load_data(self) -> Dict:
        """加载数据"""
        try:
            with self.storage_file.open('r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ 加载API Key数据失败: {e}")
            return {}
    
    def _save_data(self, data: Dict):
        """保存数据"""
        try:
            with self.storage_file.open('w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ 保存API Key数据失败: {e}")
    
    def _hash_key(self, api_key: str) -> str:
        """对API Key进行hash（安全存储）"""
        return hashlib.sha256(api_key.encode()).hexdigest()
    
    def _mask_key(self, api_key: str) -> str:
        """遮罩API Key（用于显示）"""
        if len(api_key) <= 8:
            return "*" * len(api_key)
        return f"{api_key[:4]}...{api_key[-4:]}"
    
    def set_api_key(self, client_id: str, api_key: str) -> Dict:
        """
        设置客户端的API Key
        
        Args:
            client_id: 客户端ID
            api_key: API Key
            
        Returns:
            操作结果
        """
        try:
            data = self._load_data()
            
            # 存储加密后的key（实际应该加密，这里简单hash）
            data[client_id] = {
                "api_key": api_key,  # 实际生产环境应该加密存储
                "api_key_hash": self._hash_key(api_key),
                "key_preview": self._mask_key(api_key),
                "set_at": datetime.now().isoformat(),
                "last_used": None,
            }
            
            self._save_data(data)
            
            print(f"✅ 设置API Key成功: 客户端 {client_id[:16]}...")
            
            return {
                "success": True,
                "message": "API Key设置成功",
                "key_preview": self._mask_key(api_key)
            }
        except Exception as e:
            print(f"❌ 设置API Key失败: {e}")
            return {
                "success": False,
                "message": f"设置失败: {str(e)}"
            }
    
    def get_api_key(self, client_id: str) -> Optional[str]:
        """
        获取客户端的API Key
        
        Args:
            client_id: 客户端ID
            
        Returns:
            API Key或None
        """
        try:
            data = self._load_data()
            
            if client_id in data:
                # 更新最后使用时间
                data[client_id]["last_used"] = datetime.now().isoformat()
                self._save_data(data)
                
                return data[client_id]["api_key"]
            
            return None
        except Exception as e:
            print(f"❌ 获取API Key失败: {e}")
            return None
    
    def has_api_key(self, client_id: str) -> Dict:
        """
        检查客户端是否设置了API Key
        
        Args:
            client_id: 客户端ID
            
        Returns:
            包含状态和预览的字典
        """
        try:
            data = self._load_data()
            
            if client_id in data:
                return {
                    "has_key": True,
                    "key_preview": data[client_id]["key_preview"],
                    "set_at": data[client_id].get("set_at"),
                    "last_used": data[client_id].get("last_used")
                }
            
            return {"has_key": False}
        except Exception as e:
            print(f"❌ 检查API Key失败: {e}")
            return {"has_key": False}
    
    def delete_api_key(self, client_id: str) -> bool:
        """
        删除客户端的API Key
        
        Args:
            client_id: 客户端ID
            
        Returns:
            是否成功
        """
        try:
            data = self._load_data()
            
            if client_id in data:
                del data[client_id]
                self._save_data(data)
                print(f"✅ 删除API Key成功: 客户端 {client_id[:16]}...")
                return True
            
            return False
        except Exception as e:
            print(f"❌ 删除API Key失败: {e}")
            return False
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        try:
            data = self._load_data()
            return {
                "total_clients": len(data),
                "clients": list(data.keys())
            }
        except Exception as e:
            print(f"❌ 获取统计信息失败: {e}")
            return {"total_clients": 0, "clients": []}


# 创建全局实例
api_key_manager = ApiKeyManager()

