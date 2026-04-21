"""Prompt 模板管理"""

SYSTEM_PROMPT = """你是一个专业的知识库助手，基于提供的参考文档来回答用户的问题。

## 回答规则

1. **以提供的参考文档为主**；若同时给出「网络检索摘要」，可引用其中内容但须明确标注来自网络并附链接，不要编造上下文中不存在的事实
2. 若参考文档与网络摘要均无相关信息，明确告知用户未找到相关内容
3. 回答要准确、简洁、结构化，适当使用列表和代码块
4. 如果引用了某个文档的内容，请标注来源文件名
5. 如果文档标注了"关联文档"，在回答末尾提示用户可以进一步查阅
6. 使用中文回答
7. 若上下文中包含「网络检索摘要」，须在回答中标注来源为网络并给出链接（Markdown），提醒用户自行甄别

## 回答格式

- 先给出直接回答
- 再补充相关细节
- 最后列出参考来源和关联文档"""

QA_PROMPT_TEMPLATE = """## 参考文档

{context}

## 用户问题

{question}

请根据以上参考文档回答用户的问题。如果文档中没有相关信息，请如实告知。"""

WEB_CONTEXT_HEADER = (
    "## 网络检索摘要（知识库未命中时由系统自动补充；可能与事实不符，请结合链接自行甄别）\n\n"
)


def build_web_context(web_snippets: list[dict]) -> str:
    """将联网检索结果拼成 Markdown 段落"""
    if not web_snippets:
        return ""
    parts: list[str] = []
    for i, w in enumerate(web_snippets, 1):
        title = w.get("title", "（无标题）")
        url = w.get("url", "")
        snippet = w.get("snippet", "")
        line = f"### 网页 {i}: {title}\n"
        if url:
            line += f"链接: {url}\n"
        line += f"\n{snippet}"
        parts.append(line)
    return "\n\n---\n\n".join(parts)


def build_context(hits: list[dict]) -> str:
    """将检索结果构建为 Prompt 上下文，包含文档关联关系"""
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
            header += f" ({section_info.lstrip(' >')})"
        header += f" (相关度: {score:.2f})"

        refs_to = hit["metadata"].get("references_to", "")
        refs_by = hit["metadata"].get("referenced_by", "")
        relation_hint = ""
        if refs_to:
            names = [r.strip().rsplit("/", 1)[-1] for r in refs_to.split(",") if r.strip()]
            relation_hint += f"\n> 本文引用了: {', '.join(names)}"
        if refs_by:
            names = [r.strip().rsplit("/", 1)[-1] for r in refs_by.split(",") if r.strip()]
            relation_hint += f"\n> 本文被引用于: {', '.join(names)}"

        parts.append(f"{header}{relation_hint}\n\n{hit['content']}")

    return "\n\n---\n\n".join(parts)


def format_qa_prompt(
    question: str,
    hits: list[dict],
    web_snippets: list[dict] | None = None,
) -> str:
    """构建完整的 QA Prompt；web_snippets 非空时拼在知识库上下文之后"""
    kb = build_context(hits)
    if web_snippets:
        wc = build_web_context(web_snippets)
        context = f"{kb}\n\n{WEB_CONTEXT_HEADER}{wc}"
    else:
        context = kb
    return QA_PROMPT_TEMPLATE.format(context=context, question=question)
