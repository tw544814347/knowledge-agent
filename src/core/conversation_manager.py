"""对话历史管理"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any

from ..models.schemas import Conversation, ConversationMessage, SourceInfo


class ConversationManager:
    """对话历史管理器"""
    
    def __init__(self, data_dir: str = "./data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.conversations_file = self.data_dir / "conversations.json"
        self._conversations: Dict[str, Dict[str, Any]] = {}
        self._load_conversations()
    
    def _load_conversations(self):
        """从文件加载对话历史"""
        if self.conversations_file.exists():
            try:
                with open(self.conversations_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._conversations = data.get('conversations', {})
            except (json.JSONDecodeError, OSError) as e:
                print(f"Warning: Failed to load conversations: {e}")
                self._conversations = {}
    
    def _save_conversations(self):
        """保存对话历史到文件"""
        try:
            with open(self.conversations_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'conversations': self._conversations,
                    'last_updated': datetime.now().isoformat()
                }, f, ensure_ascii=False, indent=2)
        except OSError as e:
            print(f"Warning: Failed to save conversations: {e}")
    
    def create_conversation(
        self,
        question: str,
        answer: str,
        sources: List[SourceInfo] = None
    ) -> Conversation:
        """创建新对话"""
        conversation_id = str(uuid.uuid4())
        
        # 生成对话标题（取问题前30个字符）
        title = question.strip()[:30]
        if len(question) > 30:
            title += "..."
        
        # 创建对话记录
        message = ConversationMessage(
            question=question,
            answer=answer,
            sources=sources or []
        )
        
        conversation = Conversation(
            id=conversation_id,
            title=title,
            message=message,
            created_at=datetime.now(),
            pinned=False
        )
        
        # 保存到内存和文件（转换为dict，datetime会被序列化为字符串）
        conv_dict = conversation.model_dump()
        conv_dict['created_at'] = conversation.created_at.isoformat()
        self._conversations[conversation_id] = conv_dict
        self._save_conversations()
        
        return conversation
    
    def get_conversations(self, limit: int = 20) -> List[Conversation]:
        """获取对话列表（置顶+最近）"""
        conversations = []
        
        # 转换为 Conversation 对象
        for conv_data in self._conversations.values():
            try:
                # 兼容性处理：确保 created_at 是 datetime 对象
                if isinstance(conv_data.get('created_at'), str):
                    conv_data['created_at'] = datetime.fromisoformat(conv_data['created_at'])
                conversations.append(Conversation(**conv_data))
            except Exception as e:
                print(f"Warning: Failed to parse conversation: {e}")
                continue
        
        # 分离置顶和普通对话
        pinned = [c for c in conversations if c.pinned]
        regular = [c for c in conversations if not c.pinned]
        
        # 按创建时间倒序排列
        pinned.sort(key=lambda x: x.created_at, reverse=True)
        regular.sort(key=lambda x: x.created_at, reverse=True)
        
        # 限制数量：置顶优先，剩余位置给最近对话
        result = pinned[:]
        remaining = limit - len(pinned)
        if remaining > 0:
            result.extend(regular[:remaining])
        
        return result[:limit]
    
    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """根据ID获取对话"""
        conv_data = self._conversations.get(conversation_id)
        if not conv_data:
            return None
        
        try:
            if isinstance(conv_data.get('created_at'), str):
                conv_data['created_at'] = datetime.fromisoformat(conv_data['created_at'])
            return Conversation(**conv_data)
        except Exception as e:
            print(f"Warning: Failed to parse conversation {conversation_id}: {e}")
            return None
    
    def update_conversation(
        self,
        conversation_id: str,
        pinned: Optional[bool] = None
    ) -> Optional[Conversation]:
        """更新对话"""
        if conversation_id not in self._conversations:
            return None
        
        conv_data = self._conversations[conversation_id].copy()
        
        if pinned is not None:
            conv_data['pinned'] = pinned
        
        # 确保日期格式正确
        if isinstance(conv_data.get('created_at'), datetime):
            conv_data['created_at'] = conv_data['created_at'].isoformat()
        
        # 更新保存
        self._conversations[conversation_id] = conv_data
        self._save_conversations()
        
        # 返回更新后的对话
        try:
            if isinstance(conv_data.get('created_at'), str):
                conv_data['created_at'] = datetime.fromisoformat(conv_data['created_at'])
            return Conversation(**conv_data)
        except Exception as e:
            print(f"Warning: Failed to parse updated conversation: {e}")
            return None
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """删除对话"""
        if conversation_id in self._conversations:
            del self._conversations[conversation_id]
            self._save_conversations()
            return True
        return False
    
    def get_conversation_count(self) -> int:
        """获取对话总数"""
        return len(self._conversations)