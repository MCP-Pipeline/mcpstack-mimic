from typing import Callable, Dict, List, Optional
from beartype import beartype

from MCPStack.core.tool.base import BaseTool

@beartype
class YourTool(BaseTool):
    """Template tool: start here."""
    def __init__(self, greeting: str = "Hello", targets: Optional[List[str]] = None) -> None:
        super().__init__()
        self.greeting = greeting
        self.targets = targets or ["world"]
        self.required_env_vars = {"MCP_YOUR_TOOL_NAME_PREFIX": ""}

    def actions(self) -> List[Callable]:
        return [self.say_hello, self.say_hello_all]

    def say_hello(self) -> str:
        import os
        prefix = os.getenv("MCP_YOUR_TOOL_NAME_PREFIX", "")
        base = f"{self.greeting} {self.targets[0]}"
        return f"{prefix} {base}".strip()

    def say_hello_all(self) -> str:
        import os
        prefix = os.getenv("MCP_YOUR_TOOL_NAME_PREFIX", "")
        base = f"{self.greeting} " + ", ".join(self.targets)
        return f"{prefix} {base}".strip()

    def to_dict(self) -> Dict[str, object]:
        return {"greeting": self.greeting, "targets": self.targets}

    @classmethod
    def from_dict(cls, params: Dict[str, object]):
        greeting = str(params.get("greeting", "Hello"))
        targets = params.get("targets")
        if isinstance(targets, list):
            targets = [str(x) for x in targets]
        else:
            targets = ["world"]
        return cls(greeting=greeting, targets=targets)  # type: ignore[arg-type]
