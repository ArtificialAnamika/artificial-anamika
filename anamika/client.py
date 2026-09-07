"""Lightweight OpenAI/Claude Compatible LLM REST Client (Zero-Dependency)."""

import os
import json
import ssl
import time
import urllib.request
import urllib.error
from typing import List, Dict, Any, Optional


class LLMResponse:
    """Represents a unified chat completion response."""

    def __init__(self, content: Optional[str] = None, tool_calls: Optional[List[Dict[str, Any]]] = None, raw: Optional[Dict[str, Any]] = None):
        self.content = content or ""
        self.tool_calls = tool_calls or []
        self.raw = raw or {}

    @property
    def has_tool_calls(self) -> bool:
        return bool(self.tool_calls)


class LLMClient:
    """REST Client for interacting with any OpenAI-compatible API endpoint."""

    def __init__(self, endpoint: str, api_key: str, model: str, timeout: int = 60):
        self.endpoint = endpoint.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.timeout = timeout

    @property
    def chat_url(self) -> str:
        if self.endpoint.endswith("/chat/completions"):
            return self.endpoint
        return f"{self.endpoint}/chat/completions"

    def chat_completion(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        tool_choice: str = "auto"
    ) -> LLMResponse:
        """Sends chat completion request to the configured LLM endpoint."""
        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = tool_choice

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "User-Agent": "ArtificialAnamika/1.0",
            "Accept": "application/json"
        }

        data_bytes = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(self.chat_url, data=data_bytes, headers=headers, method="POST")

        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        try:
            with urllib.request.urlopen(req, timeout=self.timeout, context=ctx) as resp:
                resp_text = resp.read().decode("utf-8")
                res_json = json.loads(resp_text)
                
                choices = res_json.get("choices", [])
                if not choices:
                    return LLMResponse(content="", raw=res_json)
                
                message = choices[0].get("message", {})
                content = message.get("content", "") or ""
                tool_calls = message.get("tool_calls", []) or []

                return LLMResponse(content=content, tool_calls=tool_calls, raw=res_json)

        except urllib.error.HTTPError as e:
            err_msg = e.read().decode("utf-8", errors="ignore")
            raise RuntimeError(f"LLM API HTTP Error {e.code}: {err_msg}")
        except urllib.error.URLError as e:
            raise RuntimeError(f"LLM Network Connection Error: {e.reason}")
        except Exception as e:
            raise RuntimeError(f"LLM Request Failed: {str(e)}")
