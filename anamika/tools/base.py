"""Base Tool Definition and Registry Engine for Artificial Anamika."""

import inspect
import subprocess
import shutil
import json
from typing import Callable, Dict, Any, List, Optional


def run_command(cmd: List[str] or str, timeout: int = 15, shell: bool = False) -> Dict[str, Any]:
    """Helper to run a shell/termux-api command safely."""
    try:
        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout,
            shell=shell
        )
        return {
            "success": proc.returncode == 0,
            "exit_code": proc.returncode,
            "stdout": proc.stdout.strip(),
            "stderr": proc.stderr.strip()
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "exit_code": -1,
            "stdout": "",
            "stderr": f"Command timed out after {timeout} seconds."
        }
    except FileNotFoundError as e:
        return {
            "success": False,
            "exit_code": 127,
            "stdout": "",
            "stderr": f"Executable not found: {e}. Is termux-api installed (pkg install termux-api)?"
        }
    except Exception as e:
        return {
            "success": False,
            "exit_code": 1,
            "stdout": "",
            "stderr": str(e)
        }


class Tool:
    """Encapsulates a callable function as an OpenAI/Claude compatible Tool."""

    def __init__(self, fn: Callable, name: str = None, description: str = None):
        self.fn = fn
        self.name = name or fn.__name__
        self.description = description or (fn.__doc__ or "").strip()
        self.schema = self._generate_schema()

    def _generate_schema(self) -> Dict[str, Any]:
        sig = inspect.signature(self.fn)
        properties = {}
        required = []

        type_map = {
            str: "string",
            int: "integer",
            float: "number",
            bool: "boolean",
            list: "array",
            dict: "object"
        }

        for param_name, param in sig.parameters.items():
            if param_name in ("self", "cls"):
                continue
            
            p_type = type_map.get(param.annotation, "string")
            param_desc = f"Parameter {param_name}"
            
            properties[param_name] = {
                "type": p_type,
                "description": param_desc
            }
            
            if param.default == inspect.Parameter.empty:
                required.append(param_name)

        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required
                }
            }
        }

    def execute(self, **kwargs) -> Any:
        """Executes the tool with keyword arguments."""
        try:
            return self.fn(**kwargs)
        except Exception as e:
            return {"error": f"Tool execution failed: {str(e)}"}


class ToolRegistry:
    """Central registry of all available Android and system tools."""

    def __init__(self):
        self._tools: Dict[str, Tool] = {}

    def register(self, fn: Callable = None, name: str = None, description: str = None):
        def decorator(f):
            tool = Tool(f, name=name, description=description)
            self._tools[tool.name] = tool
            return f

        if fn is not None:
            return decorator(fn)
        return decorator

    def get_tool(self, name: str) -> Optional[Tool]:
        return self._tools.get(name)

    def get_schemas(self) -> List[Dict[str, Any]]:
        return [tool.schema for tool in self._tools.values()]

    def execute(self, name: str, arguments: Dict[str, Any]) -> Any:
        tool = self.get_tool(name)
        if not tool:
            return {"error": f"Tool '{name}' is not registered in Anamika Tool Registry."}
        return tool.execute(**arguments)

    @property
    def tools(self) -> Dict[str, Tool]:
        return self._tools
