"""Core Agent Reasoning Loop & Tool Execution Engine for Artificial Anamika."""

import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from anamika.config import Config
from anamika.client import LLMClient, LLMResponse
from anamika.memory import MemoryManager
from anamika.prompt import SYSTEM_PROMPT
from anamika.tools import ToolRegistry, default_registry

logger = logging.getLogger("anamika.agent")


class Agent:
    """Autonomous technical AI employee operating over Android / Termux."""

    def __init__(
        self,
        config: Config,
        tools: Optional[ToolRegistry] = None,
        memory: Optional[MemoryManager] = None
    ):
        self.config = config
        self.tools = tools or default_registry
        self.memory = memory or MemoryManager()
        self.client = LLMClient(
            endpoint=config.endpoint,
            api_key=config.api_key,
            model=config.model
        )

    def _build_system_message(self) -> Dict[str, Any]:
        """Constructs system prompt injected with device facts & context."""
        facts = self.memory.get_all_facts()
        extra_context = ""
        if facts:
            extra_context = "\n### 5. KNOWN DEVICE & SYSTEM FACTS\n"
            for k, v in facts.items():
                extra_context += f"- {k}: {v}\n"

        full_prompt = f"{SYSTEM_PROMPT}\n- **Device Identifier:** {self.config.device_name}{extra_context}"
        return {"role": "system", "content": full_prompt}

    def chat(
        self,
        user_input: str,
        session_id: str = "default_session",
        max_tool_iterations: int = 6
    ) -> Dict[str, Any]:
        """Processes user input through multi-turn agent reasoning and tool execution loop."""
        
        # Fetch conversation history from memory
        history = self.memory.get_history(session_id, limit=20)
        
        # Build active messages payload
        messages = [self._build_system_message()]
        messages.extend(history)
        
        # Append current user prompt
        user_msg = {"role": "user", "content": user_input}
        messages.append(user_msg)
        self.memory.add_message(session_id=session_id, role="user", content=user_input)

        executed_tools: List[Dict[str, Any]] = []
        captured_photos: List[str] = []

        for iteration in range(max_tool_iterations):
            try:
                # If approaching max iterations, do not provide more tool calls to force final answer
                is_last_step = (iteration == max_tool_iterations - 1)
                tools_to_send = None if is_last_step else self.tools.get_schemas()

                response: LLMResponse = self.client.chat_completion(
                    messages=messages,
                    tools=tools_to_send,
                    temperature=0.7
                )
            except Exception as e:
                err_text = f"Anamika Engine Error: {str(e)}"
                self.memory.add_message(session_id=session_id, role="assistant", content=err_text)
                return {
                    "content": err_text,
                    "tools_executed": executed_tools,
                    "photos": captured_photos,
                    "error": str(e)
                }

            # Check if LLM requested tool execution
            if response.has_tool_calls:
                # Add assistant message with tool calls to context
                asst_tool_msg = {
                    "role": "assistant",
                    "content": response.content or None,
                    "tool_calls": response.tool_calls
                }
                messages.append(asst_tool_msg)
                self.memory.add_message(
                    session_id=session_id,
                    role="assistant",
                    content=response.content or "",
                    tool_calls=response.tool_calls
                )

                for tc in response.tool_calls:
                    tc_id = tc.get("id", "call_1")
                    fn_info = tc.get("function", {})
                    fn_name = fn_info.get("name", "")
                    raw_args = fn_info.get("arguments", "{}")

                    try:
                        args = json.loads(raw_args) if isinstance(raw_args, str) else raw_args
                    except Exception:
                        args = {}

                    # Execute the tool
                    tool_result = self.tools.execute(fn_name, args)
                    executed_tools.append({
                        "name": fn_name,
                        "args": args,
                        "result": tool_result
                    })

                    # Track any photo captured
                    if isinstance(tool_result, dict) and "photo_path" in tool_result:
                        captured_photos.append(tool_result["photo_path"])

                    # Add tool response to message history
                    tool_msg = {
                        "role": "tool",
                        "tool_call_id": tc_id,
                        "name": fn_name,
                        "content": json.dumps(tool_result, ensure_ascii=False)
                    }
                    messages.append(tool_msg)
                    self.memory.add_message(
                        session_id=session_id,
                        role="tool",
                        content=json.dumps(tool_result, ensure_ascii=False),
                        tool_call_id=tc_id,
                        name=fn_name
                    )

                # Continue next iteration to let LLM respond to tool outputs
                continue
            else:
                # LLM provided final response
                final_content = response.content or ""
                self.memory.add_message(session_id=session_id, role="assistant", content=final_content)
                return {
                    "content": final_content,
                    "tools_executed": executed_tools,
                    "photos": captured_photos,
                    "error": None
                }

        # If loop exited without clean assistant message, force one final synthesis
        try:
            final_resp = self.client.chat_completion(messages=messages, tools=None)
            final_text = final_resp.content or "Execution completed."
        except Exception:
            final_text = "Execution completed."

        self.memory.add_message(session_id=session_id, role="assistant", content=final_text)
        return {
            "content": final_text,
            "tools_executed": executed_tools,
            "photos": captured_photos,
            "error": None
        }
