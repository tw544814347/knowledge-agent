"""Prompt 模板管理"""

SYSTEM_PROMPT = """你是一个专业的知识库助手，基于提供的参考文档来回答用户的问题。

## 回答规则

1. **只基于提供的参考文档内容回答**，不要编造不存在的信息
2. 如果参考文档中没有相关信息，明确告知用户"在现有知识库中未找到相关内容"
3. 回答要准确、简洁、结构化，适当使用列表和代码块
4. 如果引用了某个文档的内容，请标注来源文件名
5. 使用中文回答

## 回答格式

- 先给出直接回答
- 再补充相关细节
- 最后列出参考来源"""

QA_PROMPT_TEMPLATE = """## 参考文档

{context}

## 用户问题

{question}

请根据以上参考文档回答用户的问题。如果文档中没有相关信息，请如实告知。"""


def build_context(hits: list[dict]) -> str:
    """将检索结果构建为 Prompt 上下文"""
    if not hits:
        return "（未找到相关参考文档）"

    parts: list[str] = []
    for i, hit in enumerate(hits, 1):
        source = hit["metadata"].get("filename", "未知文件")
        category = hit["metadata"].get("category", "")
        score = hit.get("score", 0)
        section_info = ""
        for key in ("h1", "h2", "h3"):
            if key in hit["metadata"]:
                section_info += f" > {hit['metadata'][key]}"

        header = f"### 文档 {i}: {source}"
        if category:
            header += f" [{category}]"
        if section_info:
            header += f" ({section_info.strip(' >')})"
        header += f" (相关度: {score:.2f})"

        parts.append(f"{header}\n\n{hit['content']}")

    return "\n\n---\n\n".join(parts)


def format_qa_prompt(question: str, hits: list[dict]) -> str:
    """构建完整的 QA Prompt"""
    context = build_context(hits)
    return QA_PROMPT_TEMPLATE.format(context=context, question=question)
