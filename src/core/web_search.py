"""联网检索：知识库无命中时由 DuckDuckGo 文本搜索补充上下文（无需 API Key）"""

from __future__ import annotations

from loguru import logger

from config.settings import settings


def fetch_web_snippets(query: str) -> list[dict]:
    """
    返回若干条 {title, url, snippet}，供拼入 Prompt。
    失败或不可用时返回空列表。
    """
    q = (query or "").strip()
    if not q:
        return []
    try:
        from duckduckgo_search import DDGS
    except ImportError:
        logger.warning("未安装 duckduckgo-search，跳过联网检索")
        return []

    max_n = settings.web_search_max_results
    timeout = settings.web_search_timeout_seconds
    items: list[dict] = []
    try:
        with DDGS(timeout=timeout) as ddgs:
            for r in ddgs.text(q, max_results=max_n):
                title = (r.get("title") or "").strip() or "（无标题）"
                url = (r.get("href") or "").strip()
                body = (r.get("body") or "").strip()
                if not body and not url:
                    continue
                items.append(
                    {
                        "title": title[:200],
                        "url": url[:500],
                        "snippet": body[:2000],
                    }
                )
                if len(items) >= max_n:
                    break
    except Exception as e:
        logger.warning(f"DuckDuckGo 检索失败: {e}")
        return []

    logger.info(f"联网检索返回 {len(items)} 条结果")
    return items
