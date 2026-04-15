"""LLM 客户端：通过 Ollama REST API 调用 DeepSeek R1 7B"""

import time

import httpx
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from config.settings import settings


class LLMError(Exception):
    """LLM 调用异常"""
    pass


class LLMClient:
    """Ollama LLM 推理客户端"""

    def __init__(
        self,
        base_url: str = settings.ollama_base_url,
        model: str = settings.llm_model,
        temperature: float = settings.llm_temperature,
        top_p: float = settings.llm_top_p,
        max_tokens: int = settings.llm_max_tokens,
    ):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.temperature = temperature
        self.top_p = top_p
        self.max_tokens = max_tokens
        self._client = httpx.Client(timeout=120.0)

    def _build_payload(self, prompt: str, system_prompt: str) -> dict:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        return {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": self.temperature,
                "top_p": self.top_p,
                "num_predict": self.max_tokens,
            },
        }

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.ConnectError)),
        reraise=True,
    )
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        """同步生成回答，含重试机制"""
        start = time.time()
        try:
            resp = self._client.post(
                f"{self.base_url}/api/chat",
                json=self._build_payload(prompt, system_prompt),
            )
            resp.raise_for_status()
            data = resp.json()
            content = data["message"]["content"]
            elapsed = time.time() - start
            logger.info(
                f"LLM 生成完成: model={self.model}, "
                f"elapsed={elapsed:.1f}s, response_len={len(content)}"
            )
            return content
        except httpx.TimeoutException:
            logger.error(f"LLM 调用超时: model={self.model}")
            raise LLMError("模型推理超时，请稍后重试")
        except httpx.ConnectError:
            logger.error("无法连接 Ollama 服务，请确认 Ollama 已启动")
            raise LLMError("无法连接 Ollama 服务")
        except Exception as e:
            logger.error(f"LLM 调用失败: {e}")
            raise LLMError(f"生成回答时出错: {e}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.ConnectError)),
        reraise=True,
    )
    async def agenerate(self, prompt: str, system_prompt: str = "") -> str:
        """异步生成回答，含重试机制"""
        start = time.time()
        async with httpx.AsyncClient(timeout=120.0) as aclient:
            try:
                resp = await aclient.post(
                    f"{self.base_url}/api/chat",
                    json=self._build_payload(prompt, system_prompt),
                )
                resp.raise_for_status()
                data = resp.json()
                content = data["message"]["content"]
                elapsed = time.time() - start
                logger.info(
                    f"LLM 异步生成完成: model={self.model}, "
                    f"elapsed={elapsed:.1f}s, response_len={len(content)}"
                )
                return content
            except httpx.TimeoutException:
                logger.error(f"LLM 异步调用超时: model={self.model}")
                raise LLMError("模型推理超时，请稍后重试")
            except httpx.ConnectError:
                logger.error("无法连接 Ollama 服务")
                raise LLMError("无法连接 Ollama 服务")
            except Exception as e:
                logger.error(f"LLM 异步调用失败: {e}")
                raise LLMError(f"生成回答时出错: {e}")

    def close(self) -> None:
        self._client.close()
