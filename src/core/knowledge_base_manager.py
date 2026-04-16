"""知识库管理器"""

import json
import os
from pathlib import Path
from typing import List, Optional, Dict, Any
from loguru import logger

from ..models.schemas import KnowledgeBase


class KnowledgeBaseManager:
    """知识库管理器"""
    
    def __init__(self, config_path: str = "./config/knowledge_bases.json"):
        self.config_path = config_path
        self.config_data = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """加载知识库配置"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                logger.warning(f"知识库配置文件不存在: {self.config_path}")
                return self._get_default_config()
        except Exception as e:
            logger.error(f"加载知识库配置失败: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "knowledge_bases": [
                {
                    "id": "agent-kb-v1.2",
                    "name": "AI Agent 知识库",
                    "path": "./agent kb v1.2",
                    "description": "主要的AI Agent技术文档",
                    "is_active": True
                }
            ],
            "default": "agent-kb-v1.2"
        }
    
    def _save_config(self) -> None:
        """保存配置到文件"""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"保存知识库配置失败: {e}")
    
    def _validate_path(self, path: str) -> bool:
        """验证知识库路径是否存在且包含文档"""
        kb_path = Path(path)
        if not kb_path.exists() or not kb_path.is_dir():
            return False
        
        # 检查是否包含markdown文件
        return any(kb_path.glob("**/*.md"))
    
    def get_knowledge_bases(self) -> List[KnowledgeBase]:
        """获取所有知识库列表"""
        knowledge_bases = []
        
        for kb_config in self.config_data.get("knowledge_bases", []):
            # 验证路径是否存在
            is_path_valid = self._validate_path(kb_config["path"])
            is_active = kb_config.get("is_active", True) and is_path_valid
            
            if not is_path_valid:
                logger.warning(f"知识库路径不存在或无效: {kb_config['path']}")
            
            knowledge_base = KnowledgeBase(
                id=kb_config["id"],
                name=kb_config["name"],
                path=kb_config["path"],
                description=kb_config.get("description", ""),
                is_active=is_active
            )
            knowledge_bases.append(knowledge_base)
        
        return knowledge_bases
    
    def get_current_knowledge_base(self) -> Optional[str]:
        """获取当前知识库ID"""
        return self.config_data.get("default")
    
    def set_current_knowledge_base(self, kb_id: str) -> bool:
        """设置当前知识库"""
        # 验证知识库ID是否存在且有效
        knowledge_bases = self.get_knowledge_bases()
        valid_kb = next((kb for kb in knowledge_bases if kb.id == kb_id and kb.is_active), None)
        
        if not valid_kb:
            logger.error(f"无效的知识库ID: {kb_id}")
            return False
        
        self.config_data["default"] = kb_id
        self._save_config()
        logger.info(f"已设置当前知识库为: {kb_id}")
        return True
    
    def add_knowledge_base(self, kb_config: Dict[str, Any]) -> bool:
        """添加新知识库"""
        # 验证必需字段
        required_fields = ["id", "name", "path"]
        if not all(field in kb_config for field in required_fields):
            logger.error("知识库配置缺少必需字段")
            return False
        
        # 检查ID是否重复
        existing_ids = [kb["id"] for kb in self.config_data.get("knowledge_bases", [])]
        if kb_config["id"] in existing_ids:
            logger.error(f"知识库ID已存在: {kb_config['id']}")
            return False
        
        # 验证路径
        if not self._validate_path(kb_config["path"]):
            logger.error(f"知识库路径无效: {kb_config['path']}")
            return False
        
        # 添加到配置
        if "knowledge_bases" not in self.config_data:
            self.config_data["knowledge_bases"] = []
        
        self.config_data["knowledge_bases"].append({
            "id": kb_config["id"],
            "name": kb_config["name"],
            "path": kb_config["path"],
            "description": kb_config.get("description", ""),
            "is_active": kb_config.get("is_active", True)
        })
        
        self._save_config()
        logger.info(f"已添加知识库: {kb_config['id']}")
        return True
    
    def remove_knowledge_base(self, kb_id: str) -> bool:
        """移除知识库"""
        knowledge_bases = self.config_data.get("knowledge_bases", [])
        original_count = len(knowledge_bases)
        
        # 移除指定ID的知识库
        self.config_data["knowledge_bases"] = [
            kb for kb in knowledge_bases if kb["id"] != kb_id
        ]
        
        if len(self.config_data["knowledge_bases"]) == original_count:
            logger.error(f"知识库ID不存在: {kb_id}")
            return False
        
        # 如果删除的是当前知识库，切换到第一个可用的
        if self.config_data.get("default") == kb_id:
            remaining_kbs = self.get_knowledge_bases()
            active_kbs = [kb for kb in remaining_kbs if kb.is_active]
            if active_kbs:
                self.config_data["default"] = active_kbs[0].id
            else:
                self.config_data["default"] = None
        
        self._save_config()
        logger.info(f"已移除知识库: {kb_id}")
        return True