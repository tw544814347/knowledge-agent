"""命令行交互式问答工具"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from loguru import logger
from src.core.rag_pipeline import RAGPipeline
from src.core.llm_client import LLMError


def main():
    logger.remove()
    logger.add(sys.stderr, level="WARNING")

    pipeline = RAGPipeline()

    print("\n知识库 Agent - 命令行问答")
    print("=" * 40)
    print(f"向量库中有 {pipeline.vector_store.count} 个 chunk")
    print("输入问题进行问答，输入 'quit' 退出\n")

    while True:
        try:
            question = input("你: ").strip()
            if not question:
                continue
            if question.lower() in ("quit", "exit", "q"):
                print("再见!")
                break

            result = pipeline.query(question)
            print(f"\nAgent: {result.answer}")

            if result.sources:
                print("\n参考来源:")
                for s in result.sources:
                    line = f"  - {s.filename} [{s.category}] (相关度: {s.score:.2f})"
                    if s.related_docs:
                        line += f"  → 关联: {', '.join(s.related_docs)}"
                    print(line)
            print()

        except LLMError as e:
            print(f"\n[错误] {e}\n")
        except KeyboardInterrupt:
            print("\n再见!")
            break

    pipeline.vector_store.close()
    pipeline.llm.close()


if __name__ == "__main__":
    main()
