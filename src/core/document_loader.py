"""文档加载模块：从知识文档目录加载 Markdown / TXT 文件"""

import hashlib
from dataclasses import dataclass, field
from pathlib import Path

from loguru import logger

EXCLUDE_DIRS = {".specstory", ".vscode", ".cursor", ".git", "__pycache__", "node_modules"}

SUPPORTED_EXTENSIONS = {".md", ".txt"}


@dataclass
class Document:
    """统一文档数据结构"""
    content: str
    metadata: dict = field(default_factory=dict)

    @property
    def doc_id(self) -> str:
        """基于来源路径生成唯一 ID"""
        source = self.metadata.get("source", "")
        return hashlib.md5(source.encode()).hexdigest()[:12]


class DocumentLoader:
    """知识文档加载器：递归扫描目录下的文本文件"""

    def __init__(self, source_dir: str):
        self.source_dir = Path(source_dir)

    def load_all(self) -> list[Document]:
        """加载目录下所有支持格式的文档"""
        if not self.source_dir.exists():
            logger.error(f"知识文档目录不存在: {self.source_dir}")
            return []

        documents: list[Document] = []
        files = self._scan_files()

        if not files:
            logger.warning(f"目录 {self.source_dir} 中未找到文档")
            return []

        logger.info(f"发现 {len(files)} 个文档待加载")
        for file_path in files:
            doc = self._load_single(file_path)
            if doc:
                documents.append(doc)

        logger.info(f"成功加载 {len(documents)} 个文档")
        return documents

    def load_file(self, file_path: str) -> Document | None:
        """加载指定的单个文件"""
        return self._load_single(Path(file_path))

    def get_file_checksums(self) -> dict[str, str]:
        """获取所有文件的 MD5 校验和，用于增量同步"""
        checksums: dict[str, str] = {}
        for file_path in self._scan_files():
            try:
                content = file_path.read_bytes()
                md5 = hashlib.md5(content).hexdigest()
                checksums[str(file_path)] = md5
            except Exception as e:
                logger.warning(f"计算校验和失败: {file_path} - {e}")
        return checksums

    def _scan_files(self) -> list[Path]:
        """递归扫描目录，排除隐藏目录"""
        files: list[Path] = []
        for f in self.source_dir.rglob("*"):
            if any(part in EXCLUDE_DIRS for part in f.parts):
                continue
            if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS:
                files.append(f)
        return sorted(files)

    def _load_single(self, file_path: Path) -> Document | None:
        """加载单个文本文件"""
        try:
            content = file_path.read_text(encoding="utf-8")
            if not content.strip():
                return None

            try:
                rel_path = file_path.relative_to(self.source_dir)
                category = rel_path.parts[0] if len(rel_path.parts) > 1 else "uncategorized"
            except ValueError:
                category = "uncategorized"

            metadata = {
                "source": str(file_path),
                "filename": file_path.name,
                "category": category,
                "extension": file_path.suffix.lower(),
                "size": len(content),
            }
            return Document(content=content, metadata=metadata)

        except UnicodeDecodeError:
            logger.warning(f"非 UTF-8 编码，跳过: {file_path.name}")
            return None
        except Exception as e:
            logger.error(f"加载失败 [{file_path.name}]: {e}")
            return None
