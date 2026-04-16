"""对话历史管理"""

import json
import uuid
from datetime import datetime, timedelta
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
                    
                # 数据迁移：删除没有user_id的旧对话记录
                conversations_to_remove = []
                for conv_id, conv_data in self._conversations.items():
                    if 'user_id' not in conv_data:
                        conversations_to_remove.append(conv_id)
                        print(f"清理无用户ID的旧对话记录: {conv_data.get('title', conv_id)}")
                
                for conv_id in conversations_to_remove:
                    del self._conversations[conv_id]
                
                if conversations_to_remove:
                    self._save_conversations()
                    print(f"清理了 {len(conversations_to_remove)} 个无用户关联的旧对话记录")
                    
            except (json.JSONDecodeError, OSError) as e:
                print(f"Warning: Failed to load conversations: {e}")
                self._conversations = {}
    
    def _save_conversations(self):
        """保存对话历史到文件"""
        try:
            def json_serializer(obj):
                """JSON序列化器，处理datetime对象"""
                if isinstance(obj, datetime):
                    return obj.isoformat()
                raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
            
            with open(self.conversations_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'conversations': self._conversations,
                    'last_updated': datetime.now().isoformat()
                }, f, ensure_ascii=False, indent=2, default=json_serializer)
        except OSError as e:
            print(f"Warning: Failed to save conversations: {e}")
    
    def _clean_expired_conversations(self):
        """清理30天前的过期对话"""
        cutoff_date = datetime.now() - timedelta(days=30)
        expired_ids = []
        
        for conv_id, conv_data in self._conversations.items():
            created_at_value = conv_data.get('created_at')
            if isinstance(created_at_value, str) and created_at_value:
                try:
                    created_at = datetime.fromisoformat(created_at_value)
                    if created_at < cutoff_date:
                        expired_ids.append(conv_id)
                except ValueError:
                    # 如果datetime解析失败，删除这个无效记录
                    expired_ids.append(conv_id)
            elif isinstance(created_at_value, datetime):
                if created_at_value < cutoff_date:
                    expired_ids.append(conv_id)
            else:
                # 如果created_at不存在或格式不正确，删除这个记录
                expired_ids.append(conv_id)
        
        for conv_id in expired_ids:
            del self._conversations[conv_id]
        
        if expired_ids:
            self._save_conversations()
            print(f"清理了 {len(expired_ids)} 个过期对话记录")
    
    def _limit_user_conversations(self, user_id: str):
        """限制用户对话记录数量为10个（不包括置顶的）"""
        user_conversations = []
        
        # 获取用户的所有对话，按创建时间排序
        for conv_id, conv_data in self._conversations.items():
            if conv_data.get('user_id') == user_id:
                user_conversations.append((conv_id, conv_data))
        
        # 分离置顶和非置顶对话
        pinned_conversations = [(cid, cdata) for cid, cdata in user_conversations if cdata.get('pinned', False)]
        regular_conversations = [(cid, cdata) for cid, cdata in user_conversations if not cdata.get('pinned', False)]
        
        # 按创建时间倒序排序（最新的在前面）
        def get_sort_key(conv_item):
            created_at = conv_item[1].get('created_at', '')
            if isinstance(created_at, str):
                try:
                    return datetime.fromisoformat(created_at)
                except ValueError:
                    return datetime.min
            elif isinstance(created_at, datetime):
                return created_at
            else:
                return datetime.min
        
        regular_conversations.sort(key=get_sort_key, reverse=True)
        
        # 如果非置顶对话超过10个，删除最旧的
        if len(regular_conversations) > 10:
            conversations_to_delete = regular_conversations[10:]
            for conv_id, _ in conversations_to_delete:
                del self._conversations[conv_id]
            
            if conversations_to_delete:
                self._save_conversations()
                print(f"用户 {user_id} 的对话记录已限制为10个，删除了 {len(conversations_to_delete)} 个最旧的记录")
    
    def create_conversation(
        self,
        question: str,
        answer: str,
        user_id: str,
        sources: List[SourceInfo] = None
    ) -> Conversation:
        """创建新对话（不保存thinking过程，限制用户对话数量）"""
        conversation_id = str(uuid.uuid4())

        # 生成对话标题（取问题前30个字符）
        title = question.strip()[:30]
        if len(question) > 30:
            title += "..."
        
        # 清理answer中的thinking过程（移除<think>标签内容）
        import re
        clean_answer = re.sub(r'<think>.*?</think>', '', answer, flags=re.DOTALL).strip()
        
        # 创建对话记录
        message = ConversationMessage(
            question=question,
            answer=clean_answer,  # 使用清理后的答案
            sources=sources or []
        )

        conversation = Conversation(
            id=conversation_id,
            title=title,
            message=message,
            created_at=datetime.now(),
            pinned=False,
            user_id=user_id
        )
        
        # 保存到内存和文件（转换为dict，datetime会被序列化为字符串）
        conv_dict = conversation.model_dump()
        # 确保datetime被正确序列化为ISO字符串
        if isinstance(conv_dict.get('created_at'), datetime):
            conv_dict['created_at'] = conv_dict['created_at'].isoformat()
        conv_dict['user_id'] = user_id
        self._conversations[conversation_id] = conv_dict
        
        # 限制用户对话数量为10个（置顶除外）
        self._limit_user_conversations(user_id)
        
        # 保存到文件
        self._save_conversations()
        
        return conversation
    
    def get_conversations(self, user_id: Optional[str] = None, limit: int = 10) -> List[Conversation]:
        """获取对话列表（仅对登录用户可见，最多10个，自动清理30天前的记录）"""
        if not user_id:
            return []  # 未登录用户不能看到任何历史记录
        
        # 清理过期对话（30天前的）
        self._clean_expired_conversations()
        
        conversations = []

        # 转换为 Conversation 对象（只获取当前用户的对话）
        for conv_data in self._conversations.values():
            try:
                # 只返回当前用户的对话
                if conv_data.get('user_id') != user_id:
                    continue

                # 兼容性处理：确保 created_at 是 datetime 对象
                created_at_value = conv_data.get('created_at')
                if isinstance(created_at_value, str):
                    conv_data['created_at'] = datetime.fromisoformat(created_at_value)
                elif not isinstance(created_at_value, datetime):
                    # 如果不是字符串也不是datetime，使用当前时间
                    conv_data['created_at'] = datetime.now()
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
    
    def delete_conversation(self, conversation_id: str, user_id: str) -> bool:
        """删除对话"""
        # 检查对话是否存在且属于当前用户
        conv_data = self._conversations.get(conversation_id)
        if conv_data and conv_data.get('user_id') == user_id:
            del self._conversations[conversation_id]
            self._save_conversations()
            return True
        return False
    
    def get_conversation_count(self, user_id: str) -> int:
        """获取对话总数"""
        return len([c for c in self._conversations.values() if c.get('user_id') == user_id])