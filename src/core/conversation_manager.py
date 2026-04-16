"""对话历史管理 - 新版本，支持用户分组结构"""

import json
import uuid
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Dict, Any

from config.settings import settings
from ..models.schemas import Conversation, ConversationMessage, SourceInfo


class ConversationManager:
    """对话历史管理器 - 支持用户分组的新数据结构"""
    
    def __init__(self, data_dir: str = "./data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.conversations_file = self.data_dir / "conversations.json"
        # 新结构：{user_id: {conversations: {conv_id: conv_data}, last_updated: ...}}
        self._user_conversations: Dict[str, Dict[str, Any]] = {}
        self._load_conversations()
    
    def _load_conversations(self):
        """从文件加载对话历史"""
        if self.conversations_file.exists():
            try:
                with open(self.conversations_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # 检查数据格式，支持旧格式迁移
                    if 'conversations' in data and isinstance(data['conversations'], dict):
                        # 旧格式迁移
                        print("检测到旧格式数据，正在迁移...")
                        self._migrate_old_format(data['conversations'])
                    elif 'users' in data:
                        # 新格式
                        self._user_conversations = data.get('users', {})
                    else:
                        self._user_conversations = {}
                        
            except (json.JSONDecodeError, OSError) as e:
                print(f"Warning: Failed to load conversations: {e}")
                self._user_conversations = {}
    
    def _migrate_old_format(self, old_conversations: Dict[str, Any]):
        """迁移旧格式数据到新格式"""
        migrated_count = 0
        for conv_id, conv_data in old_conversations.items():
            user_id = conv_data.get('user_id')
            if user_id:
                # 确保用户数据结构存在
                if user_id not in self._user_conversations:
                    self._user_conversations[user_id] = {
                        'conversations': {},
                        'last_updated': datetime.now().isoformat()
                    }
                
                # 移除user_id字段（在新结构中不需要）
                clean_conv_data = {k: v for k, v in conv_data.items() if k != 'user_id'}
                self._user_conversations[user_id]['conversations'][conv_id] = clean_conv_data
                migrated_count += 1
        
        if migrated_count > 0:
            print(f"成功迁移 {migrated_count} 条对话记录到新格式")
            self._save_conversations()
    
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
                    'users': self._user_conversations,
                    'last_updated': datetime.now().isoformat()
                }, f, ensure_ascii=False, indent=2, default=json_serializer)
        except OSError as e:
            print(f"Warning: Failed to save conversations: {e}")
    
    def _clean_expired_conversations(self, user_id: str):
        """清理用户的过期对话（pin消息30天，非pin消息7天）"""
        if user_id not in self._user_conversations:
            return
            
        # pin消息30天，非pin消息7天
        pinned_cutoff_date = datetime.now() - timedelta(days=30)
        regular_cutoff_date = datetime.now() - timedelta(days=7)
        
        expired_ids = []
        user_data = self._user_conversations[user_id]
        conversations = user_data.get('conversations', {})
        
        for conv_id, conv_data in conversations.items():
            created_at_value = conv_data.get('created_at')
            is_pinned = conv_data.get('pinned', False)
            
            # 根据是否pin选择不同的过期时间
            cutoff_date = pinned_cutoff_date if is_pinned else regular_cutoff_date
            
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
        
        # 删除过期对话
        for conv_id in expired_ids:
            del conversations[conv_id]
        
        if expired_ids:
            user_data['last_updated'] = datetime.now().isoformat()
            self._save_conversations()
            print(f"用户 {user_id} 清理了 {len(expired_ids)} 个过期对话记录")
    
    def _limit_user_conversations(self, user_id: str):
        """限制用户对话记录数量为10个（不包括置顶的）"""
        if user_id not in self._user_conversations:
            return
            
        user_data = self._user_conversations[user_id]
        conversations = user_data.get('conversations', {})
        
        # 获取所有对话
        all_conversations = list(conversations.items())
        
        # 分离置顶和非置顶对话
        pinned_conversations = [(cid, cdata) for cid, cdata in all_conversations if cdata.get('pinned', False)]
        regular_conversations = [(cid, cdata) for cid, cdata in all_conversations if not cdata.get('pinned', False)]
        
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
        
        pinned_conversations.sort(key=get_sort_key, reverse=True)
        regular_conversations.sort(key=get_sort_key, reverse=True)
        
        conversations_to_delete = []
        
        # 限制置顶对话数量为3个，删除最旧的
        if len(pinned_conversations) > 3:
            conversations_to_delete.extend(pinned_conversations[3:])
        
        # 保留最新的10个非置顶对话
        if len(regular_conversations) > 10:
            conversations_to_delete.extend(regular_conversations[10:])
        
        # 执行删除
        if conversations_to_delete:
            for conv_id, _ in conversations_to_delete:
                del conversations[conv_id]
            
            user_data['last_updated'] = datetime.now().isoformat()
            self._save_conversations()
            
            pinned_deleted = sum(1 for _, cdata in conversations_to_delete if cdata.get('pinned', False))
            regular_deleted = len(conversations_to_delete) - pinned_deleted
            
            if pinned_deleted > 0:
                print(f"用户 {user_id} 删除了 {pinned_deleted} 个最旧的置顶对话（超过3个限制）")
            if regular_deleted > 0:
                print(f"用户 {user_id} 删除了 {regular_deleted} 个最旧的普通对话（超过10个限制）")
    
    def create_conversation(
        self,
        question: str,
        answer: str,
        user_id: str,
        sources: List[SourceInfo] = None,
        conversation_id: str = None
    ) -> Conversation:
        """创建新对话或在已有对话中添加消息（不保存thinking过程，限制用户对话数量）"""
        # 清理answer中的thinking过程（移除<think>标签内容）
        clean_answer = re.sub(r'<think>.*?</think>', '', answer, flags=re.DOTALL).strip()
        
        # 创建消息记录
        new_message = ConversationMessage(
            question=question,
            answer=clean_answer,  # 使用清理后的答案
            sources=sources or [],
            created_at=datetime.now()
        )
        
        # 如果提供了conversation_id，尝试添加到现有对话
        if conversation_id and user_id in self._user_conversations:
            existing_conversations = self._user_conversations[user_id]['conversations']
            if conversation_id in existing_conversations:
                # 更新现有对话
                existing_conv_data = existing_conversations[conversation_id]
                
                # 处理数据迁移：如果是旧格式(单条message)，转换为新格式(messages列表)
                if 'message' in existing_conv_data and 'messages' not in existing_conv_data:
                    old_message = existing_conv_data['message']
                    existing_conv_data['messages'] = [old_message]
                    del existing_conv_data['message']
                
                # 添加新消息到现有对话
                if 'messages' not in existing_conv_data:
                    existing_conv_data['messages'] = []
                
                existing_conv_data['messages'].append(new_message.model_dump())
                existing_conv_data['updated_at'] = datetime.now().isoformat()
                
                # 保存更新
                self._user_conversations[user_id]['last_updated'] = datetime.now().isoformat()
                self._save_conversations()
                
                # 返回更新后的对话对象
                return self._build_conversation_object(conversation_id, existing_conv_data, user_id)
        
        # 创建新对话
        if not conversation_id:
            conversation_id = str(uuid.uuid4())
        
        # 生成对话标题（取第一个问题的前30个字符）
        title = question.strip()[:30]
        if len(question) > 30:
            title += "..."
        
        conversation = Conversation(
            id=conversation_id,
            title=title,
            messages=[new_message],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            pinned=False,
            user_id=user_id  # 这个字段在新结构中不存储，但Conversation模型需要
        )
        
        # 确保用户数据结构存在
        if user_id not in self._user_conversations:
            self._user_conversations[user_id] = {
                'conversations': {},
                'last_updated': datetime.now().isoformat()
            }
        
        # 保存到用户的对话列表中（不包含user_id字段）
        conv_dict = self._serialize_conversation_dict(conversation)
        
        self._user_conversations[user_id]['conversations'][conversation_id] = conv_dict
        self._user_conversations[user_id]['last_updated'] = datetime.now().isoformat()
        
        # 限制用户对话数量为10个（置顶除外）
        self._limit_user_conversations(user_id)
        
        # 保存到文件
        self._save_conversations()
        
        return conversation
    
    def _serialize_conversation_dict(self, conversation: Conversation) -> Dict[str, Any]:
        """序列化Conversation对象为字典，处理datetime和移除user_id"""
        conv_dict = conversation.model_dump()
        
        # 确保datetime被正确序列化为ISO字符串
        if isinstance(conv_dict.get('created_at'), datetime):
            conv_dict['created_at'] = conv_dict['created_at'].isoformat()
        if isinstance(conv_dict.get('updated_at'), datetime):
            conv_dict['updated_at'] = conv_dict['updated_at'].isoformat()
            
        # 处理messages中的datetime
        if 'messages' in conv_dict:
            for msg in conv_dict['messages']:
                if isinstance(msg.get('created_at'), datetime):
                    msg['created_at'] = msg['created_at'].isoformat()
                if isinstance(msg.get('liked_at'), datetime):
                    msg['liked_at'] = msg['liked_at'].isoformat()
        
        # 移除user_id字段，因为在新结构中通过层级关系表示
        conv_dict.pop('user_id', None)
        
        return conv_dict
    
    def _build_conversation_object(self, conversation_id: str, conv_data: Dict[str, Any], user_id: str) -> Conversation:
        """从字典数据构建Conversation对象"""
        conv_data_with_uid = conv_data.copy()
        conv_data_with_uid['user_id'] = user_id
        
        # 处理datetime字段
        for field in ['created_at', 'updated_at']:
            if field in conv_data_with_uid and isinstance(conv_data_with_uid[field], str):
                conv_data_with_uid[field] = datetime.fromisoformat(conv_data_with_uid[field])
        
        # 处理messages中的datetime
        if 'messages' in conv_data_with_uid:
            for msg in conv_data_with_uid['messages']:
                if 'created_at' in msg and isinstance(msg['created_at'], str):
                    msg['created_at'] = datetime.fromisoformat(msg['created_at'])
                if msg.get('liked_at') and isinstance(msg['liked_at'], str):
                    msg['liked_at'] = datetime.fromisoformat(msg['liked_at'])
                if 'liked' not in msg:
                    msg['liked'] = False
        
        # 兼容旧格式：如果没有messages但有message，转换格式
        if 'message' in conv_data_with_uid and 'messages' not in conv_data_with_uid:
            conv_data_with_uid['messages'] = [conv_data_with_uid['message']]
            # 保留message字段用于兼容性
        
        return Conversation(**conv_data_with_uid)
    
    def get_conversations(self, user_id: Optional[str] = None, limit: int = 10) -> List[Conversation]:
        """获取用户的对话列表（仅对登录用户可见，最多10个，自动清理30天前的记录）"""
        if not user_id:
            return []  # 未登录用户不能看到任何历史记录
        
        if user_id not in self._user_conversations:
            return []
        
        # 清理过期对话（30天前的）
        self._clean_expired_conversations(user_id)
        
        conversations = []
        user_data = self._user_conversations[user_id]
        user_conversations = user_data.get('conversations', {})
        
        for conv_id, conv_data in user_conversations.items():
            try:
                conversation = self._build_conversation_object(conv_id, conv_data, user_id)
                conversations.append(conversation)
            except Exception as e:
                print(f"Warning: Failed to parse conversation {conv_id}: {e}")
                continue
        
        # 分离置顶和普通对话
        pinned = [c for c in conversations if c.pinned]
        regular = [c for c in conversations if not c.pinned]

        # 按创建时间倒序排列
        pinned.sort(key=lambda x: x.created_at, reverse=True)
        regular.sort(key=lambda x: x.created_at, reverse=True)

        # 限制数量：置顶优先，剩余位置给最近对话
        result = pinned[:]
        remaining_slots = max(0, limit - len(pinned))
        if remaining_slots > 0:
            result.extend(regular[:remaining_slots])

        return result
    
    def get_conversation(self, conversation_id: str, user_id: str) -> Optional[Conversation]:
        """获取单个对话"""
        if user_id not in self._user_conversations:
            return None
            
        user_conversations = self._user_conversations[user_id]['conversations']
        conv_data = user_conversations.get(conversation_id)
        if not conv_data:
            return None

        try:
            return self._build_conversation_object(conversation_id, conv_data, user_id)
        except Exception as e:
            print(f"Warning: Failed to parse conversation {conversation_id}: {e}")
            return None
    
    def update_conversation(self, conversation_id: str, user_id: str, **updates) -> Optional[Conversation]:
        """更新对话"""
        if user_id not in self._user_conversations:
            return None
            
        user_data = self._user_conversations[user_id]
        user_conversations = user_data['conversations']
        conv_data = user_conversations.get(conversation_id)
        if not conv_data:
            return None

        # 更新字段
        for key, value in updates.items():
            if key in ['pinned', 'title']:  # 只允许更新这些字段
                # 如果要设置为置顶，检查置顶数量限制
                if key == 'pinned' and value is True:
                    # 统计当前置顶对话数量（排除当前要更新的对话）
                    current_pinned_count = sum(
                        1 for cid, cdata in user_conversations.items() 
                        if cid != conversation_id and cdata.get('pinned', False)
                    )
                    
                    # 如果已经有3个置顶对话，取消最旧的置顶
                    if current_pinned_count >= 3:
                        # 找到所有置顶对话并按时间排序
                        pinned_convs = [
                            (cid, cdata) for cid, cdata in user_conversations.items()
                            if cid != conversation_id and cdata.get('pinned', False)
                        ]
                        
                        # 按创建时间排序（最旧的在前）
                        def get_created_time(conv_item):
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
                        
                        pinned_convs.sort(key=get_created_time)
                        
                        # 取消最旧的置顶对话的置顶状态
                        if pinned_convs:
                            oldest_conv_id, oldest_conv_data = pinned_convs[0]
                            oldest_conv_data['pinned'] = False
                            print(f"自动取消了最旧的置顶对话 {oldest_conv_id} 的置顶状态（超过3个限制）")
                
                conv_data[key] = value

        user_data['last_updated'] = datetime.now().isoformat()
        self._save_conversations()

        # 返回更新后的对话
        try:
            conv_data_with_uid = conv_data.copy()
            conv_data_with_uid['user_id'] = user_id
            
            if isinstance(conv_data_with_uid.get('created_at'), str):
                conv_data_with_uid['created_at'] = datetime.fromisoformat(conv_data_with_uid['created_at'])
            return Conversation(**conv_data_with_uid)
        except Exception as e:
            print(f"Warning: Failed to parse updated conversation: {e}")
            return None
    
    def delete_conversation(self, conversation_id: str, user_id: str) -> bool:
        """删除对话"""
        if user_id not in self._user_conversations:
            return False
            
        user_data = self._user_conversations[user_id]
        user_conversations = user_data['conversations']
        
        if conversation_id in user_conversations:
            self._delete_all_liked_exports_for_conversation(conversation_id)
            del user_conversations[conversation_id]
            user_data['last_updated'] = datetime.now().isoformat()
            self._save_conversations()
            return True
        return False

    def _liked_answers_dir(self) -> Path:
        d = Path(settings.knowledge_source_dir) / "liked_answers"
        d.mkdir(parents=True, exist_ok=True)
        return d

    def _liked_export_filename(self, conversation_id: str, message_index: int) -> str:
        safe = conversation_id.replace("/", "_").replace("\\", "_")
        return f"la_{safe}_{message_index}.md"

    def _write_liked_export(
        self,
        user_id: str,
        conversation_id: str,
        message_index: int,
        question: str,
        answer: str,
        liked_at_iso: str,
    ) -> None:
        path = self._liked_answers_dir() / self._liked_export_filename(conversation_id, message_index)
        text = (
            "---\n"
            "type: liked_qa\n"
            f"conversation_id: {conversation_id}\n"
            f"message_index: {message_index}\n"
            f"user_id: {user_id}\n"
            f"liked_at: {liked_at_iso}\n"
            "---\n\n"
            f"问题: {question}\n\n"
            f"回答: {answer}\n"
        )
        path.write_text(text, encoding="utf-8")

    def _delete_liked_export(self, conversation_id: str, message_index: int) -> None:
        path = self._liked_answers_dir() / self._liked_export_filename(conversation_id, message_index)
        if path.is_file():
            try:
                path.unlink()
            except OSError:
                pass

    def _delete_all_liked_exports_for_conversation(self, conversation_id: str) -> None:
        d = self._liked_answers_dir()
        if not d.is_dir():
            return
        safe = conversation_id.replace("/", "_").replace("\\", "_")
        for p in d.glob(f"la_{safe}_*.md"):
            try:
                p.unlink()
            except OSError:
                pass

    def set_message_liked(
        self,
        conversation_id: str,
        user_id: str,
        message_index: int,
        liked: bool,
    ) -> Optional[Conversation]:
        """点赞/取消点赞某一条多轮消息，并同步写入或删除 liked_answers 下的语料文件"""
        if user_id not in self._user_conversations:
            return None

        user_data = self._user_conversations[user_id]
        conv_data = user_data.get("conversations", {}).get(conversation_id)
        if not conv_data:
            return None

        if "messages" not in conv_data and "message" in conv_data:
            conv_data["messages"] = [conv_data["message"]]

        messages_list = conv_data.get("messages") or []
        if message_index < 0 or message_index >= len(messages_list):
            return None

        msg = messages_list[message_index]
        if not isinstance(msg, dict):
            return None

        if liked:
            liked_at = datetime.now()
            liked_at_iso = liked_at.isoformat()
            msg["liked"] = True
            msg["liked_at"] = liked_at_iso
            self._write_liked_export(
                user_id,
                conversation_id,
                message_index,
                str(msg.get("question", "")),
                str(msg.get("answer", "")),
                liked_at_iso,
            )
        else:
            msg["liked"] = False
            msg.pop("liked_at", None)
            self._delete_liked_export(conversation_id, message_index)

        conv_data["updated_at"] = datetime.now().isoformat()
        user_data["last_updated"] = datetime.now().isoformat()
        self._save_conversations()

        try:
            return self._build_conversation_object(conversation_id, conv_data, user_id)
        except Exception as e:
            print(f"Warning: Failed to rebuild conversation after like: {e}")
            return None
    
    def get_conversation_count(self, user_id: str) -> int:
        """获取用户的对话总数"""
        if user_id not in self._user_conversations:
            return 0
        return len(self._user_conversations[user_id].get('conversations', {}))