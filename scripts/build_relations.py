"""文档关系图构建脚本：扫描知识文档，提取引用关系，生成关系映射和可视化图"""

import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config.settings import settings
from loguru import logger

EXCLUDE_DIRS = {".specstory", ".vscode", ".cursor", ".git", "__pycache__", "node_modules"}
CONFLUENCE_PAGE_RE = re.compile(r"confluence\.shopee\.io/pages/viewpage\.action\?pageId=(\d+)")
CONFLUENCE_IMG_RE = re.compile(r"(https://confluence\.shopee\.io/download/attachments/[^\s\)\"]+)")
URL_RE = re.compile(r"(https?://[^\s\)>\]\"\|]+)")


def scan_markdown_files(source_dir: Path) -> list[Path]:
    """递归扫描目录下所有 Markdown 文件"""
    files = []
    for f in source_dir.rglob("*.md"):
        if any(part in EXCLUDE_DIRS for part in f.parts):
            continue
        files.append(f)
    return sorted(files)


def extract_self_page_id(content: str) -> str | None:
    """从文件头部提取本文档的 Confluence pageId"""
    for line in content.split("\n")[:10]:
        if "**URL**" in line or "**Page ID**" in line:
            m = re.search(r"pageId=(\d+)", line)
            if m:
                return m.group(1)
            m2 = re.search(r"Page ID\*\*:\s*(\d+)", line)
            if m2:
                return m2.group(1)
    return None


def extract_links(content: str, skip_header_lines: int = 5) -> tuple[list[str], list[str], list[dict]]:
    """
    从文档正文中提取：
    - Confluence 交叉引用 pageIds
    - Confluence 图片附件 URLs
    - 外部链接 URLs
    """
    cross_ref_pids: list[str] = []
    image_urls: list[str] = []
    external_urls: list[dict] = []

    lines = content.split("\n")
    self_pid = extract_self_page_id(content)

    for i, line in enumerate(lines):
        if i < skip_header_lines and ("**URL**" in line or "**Page ID**" in line):
            continue

        for pid in CONFLUENCE_PAGE_RE.findall(line):
            if pid != self_pid:
                cross_ref_pids.append(pid)

        for img_url in CONFLUENCE_IMG_RE.findall(line):
            image_urls.append(img_url.rstrip(".)"))

        for url in URL_RE.findall(line):
            url = url.rstrip(".)>,;")
            if "confluence.shopee.io" in url:
                continue
            parsed = urlparse(url)
            if parsed.scheme in ("http", "https") and parsed.netloc:
                is_image = any(url.lower().endswith(ext) for ext in (".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp"))
                if not is_image:
                    external_urls.append({
                        "url": url,
                        "domain": parsed.netloc,
                        "status": "pending",
                    })

    return cross_ref_pids, list(set(image_urls)), external_urls


def build_relations(source_dir: str) -> dict:
    """构建完整的文档关系映射"""
    src = Path(source_dir)
    files = scan_markdown_files(src)
    logger.info(f"扫描到 {len(files)} 个 Markdown 文件")

    # 第一遍：建立 pageId → 本地路径 映射
    pid_to_path: dict[str, str] = {}
    doc_entries: list[dict] = []

    for f in files:
        content = f.read_text(encoding="utf-8")
        try:
            rel = str(f.relative_to(src))
        except ValueError:
            rel = f.name
        parts = rel.split("/")
        category = parts[0] if len(parts) > 1 else "uncategorized"
        pid = extract_self_page_id(content)

        if pid:
            pid_to_path[pid] = rel

        cross_pids, images, ext_links = extract_links(content)

        doc_entries.append({
            "filename": f.name,
            "path": rel,
            "category": category,
            "pageId": pid,
            "cross_ref_pids": cross_pids,
            "references_to": [],
            "referenced_by": [],
            "external_links": ext_links,
            "images": [{"url": u, "status": "auth_required"} for u in images],
        })

    # 第二遍：解析交叉引用为本地路径，构建双向关系
    graph_edges: list[dict] = []
    seen_edges: set[tuple[str, str]] = set()

    for doc in doc_entries:
        resolved_refs = []
        for pid in doc["cross_ref_pids"]:
            target_path = pid_to_path.get(pid)
            if target_path and target_path != doc["path"]:
                resolved_refs.append(target_path)
                edge_key = (doc["path"], target_path)
                if edge_key not in seen_edges:
                    seen_edges.add(edge_key)
                    graph_edges.append({
                        "from": doc["path"],
                        "to": target_path,
                        "type": "cross_reference",
                        "pageId": pid,
                    })
        doc["references_to"] = list(set(resolved_refs))

    # 构建 referenced_by（反向引用）
    for edge in graph_edges:
        for doc in doc_entries:
            if doc["path"] == edge["to"]:
                if edge["from"] not in doc["referenced_by"]:
                    doc["referenced_by"].append(edge["from"])

    # 清理临时字段
    for doc in doc_entries:
        del doc["cross_ref_pids"]

    # 去重 external_links
    for doc in doc_entries:
        seen = set()
        deduped = []
        for link in doc["external_links"]:
            if link["url"] not in seen:
                seen.add(link["url"])
                deduped.append(link)
        doc["external_links"] = deduped

    total_ext = sum(len(d["external_links"]) for d in doc_entries)
    total_imgs = sum(len(d["images"]) for d in doc_entries)

    result = {
        "source_dir": str(src),
        "stats": {
            "total_docs": len(doc_entries),
            "cross_refs": len(graph_edges),
            "external_links": total_ext,
            "images": total_imgs,
            "categories": list(set(d["category"] for d in doc_entries)),
        },
        "documents": sorted(doc_entries, key=lambda d: (d["category"], d["filename"])),
        "graph_edges": graph_edges,
    }

    return result


def generate_mermaid_graph(relations: dict) -> str:
    """根据关系数据生成 Mermaid 关系图"""
    docs = relations["documents"]
    edges = relations["graph_edges"]
    categories = relations["stats"]["categories"]

    lines = ["# 文档关系图", "", "```mermaid", "flowchart LR"]

    # 按分类建子图
    cat_docs = defaultdict(list)
    for doc in docs:
        cat_docs[doc["category"]].append(doc)

    node_id_map = {}
    idx = 0
    for cat in sorted(categories):
        safe_cat = cat.replace(" ", "_").replace("+", "Plus").replace("-", "_")
        lines.append(f"    subgraph {safe_cat} [{cat}]")
        for doc in cat_docs[cat]:
            nid = f"n{idx}"
            node_id_map[doc["path"]] = nid
            label = doc["filename"].replace(".md", "").replace('"', "'")
            lines.append(f'        {nid}["{label}"]')
            idx += 1
        lines.append("    end")

    # 添加引用边
    for edge in edges:
        from_id = node_id_map.get(edge["from"])
        to_id = node_id_map.get(edge["to"])
        if from_id and to_id:
            lines.append(f"    {from_id} -->|引用| {to_id}")

    lines.append("```")

    # 添加统计信息
    stats = relations["stats"]
    lines.extend([
        "",
        "## 统计",
        "",
        f"| 指标 | 数值 |",
        f"|------|------|",
        f"| 文档总数 | {stats['total_docs']} |",
        f"| 文档间交叉引用 | {stats['cross_refs']} |",
        f"| 外部链接 | {stats['external_links']} |",
        f"| Confluence 图片 | {stats['images']} |",
        f"| 分类数 | {len(stats['categories'])} |",
        "",
        "## 交叉引用详情",
        "",
    ])

    if edges:
        lines.append("| 来源文档 | 引用目标 |")
        lines.append("|----------|----------|")
        for edge in edges:
            lines.append(f"| {edge['from']} | {edge['to']} |")
    else:
        lines.append("暂无文档间交叉引用。")

    return "\n".join(lines)


def main():
    source_dir = settings.knowledge_source_dir
    output_dir = Path(__file__).resolve().parent.parent / "docs"
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info("=" * 50)
    logger.info("文档关系图构建")
    logger.info("=" * 50)

    relations = build_relations(source_dir)

    json_path = output_dir / "doc_relations.json"
    json_path.write_text(
        json.dumps(relations, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    logger.info(f"关系映射已保存: {json_path}")

    graph_md = generate_mermaid_graph(relations)
    graph_path = output_dir / "doc_graph.md"
    graph_path.write_text(graph_md, encoding="utf-8")
    logger.info(f"可视化关系图已保存: {graph_path}")

    stats = relations["stats"]
    logger.info(f"文档: {stats['total_docs']} | 交叉引用: {stats['cross_refs']} | "
                f"外部链接: {stats['external_links']} | 图片: {stats['images']}")


if __name__ == "__main__":
    main()
