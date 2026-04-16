# liked_answers

由用户在对话中对回答「点赞」后，由后端自动生成 `.md` 语料文件（`问题:` / `回答:` 键值式正文 + YAML front matter）。  
目录位于知识库根路径下，随现有 **约 5 分钟** 的文档增量同步进入向量库；点赞接口成功后会 **立即执行一次** `sync()`。

勿手动伪造文件名：格式为 `la_{conversation_id}_{message_index}.md`，与 `data/conversations.json` 中的记录一致。
