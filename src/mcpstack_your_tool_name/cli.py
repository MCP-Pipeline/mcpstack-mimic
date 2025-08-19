import json
from typing import Annotated, Optional
import typer
from beartype import beartype
from rich.console import Console
from rich.panel import Panel

from MCPStack.core.tool.cli.base import BaseToolCLI, ToolConfig

console = Console()

@beartype
class YourToolCLI(BaseToolCLI):
    @classmethod
    def get_app(cls) -> typer.Typer:
        app = typer.Typer(
            help="your_tool_name CLI",
            add_completion=False,
            pretty_exceptions_show_locals=False,
            rich_markup_mode="markdown",
        )
        app.command(help="Quick init (sets a default prefix).")(cls.init)
        app.command(help="Configure your_tool_name (env + params).")(cls.configure)
        app.command(help="Show current your_tool_name status.")(cls.status)
        return app

    @classmethod
    def init(
        cls,
        prefix: Annotated[Optional[str], typer.Option("--prefix", "-p", help="Greeting prefix emoji/text.")] = "🎯",
    ) -> None:
        console.print(f"[green]✅ Set default prefix to '{prefix}'[/green]")
        console.print("Export and run:")
        console.print(f"    export MCP_YOUR_TOOL_NAME_PREFIX='{prefix}'\n")

    @classmethod
    def configure(
        cls,
        greeting: Annotated[Optional[str], typer.Option("--greeting", "-g", help="Greeting word.")] = None,
        targets: Annotated[Optional[str], typer.Option("--targets", "-t", help="Comma-separated targets.")] = None,
        prefix: Annotated[Optional[str], typer.Option("--prefix", "-p", help="Prefix emoji/text.")] = None,
        output: Annotated[Optional[str], typer.Option("--output", "-o", help="Where to save config JSON.")] = None,
        verbose: Annotated[bool, typer.Option("--verbose", "-v", help="Print config.")] = False,
    ) -> ToolConfig:
        env_vars = {}
        tool_params = {}

        if prefix is None:
            prefix = typer.prompt("Prefix (emoji/text)", default="")
        env_vars["MCP_YOUR_TOOL_NAME_PREFIX"] = prefix

        if greeting is None:
            greeting = typer.prompt("Greeting", default="Hello")
        tool_params["greeting"] = greeting

        if targets:
            tool_params["targets"] = [s.strip() for s in targets.split(",") if s.strip()]

        cfg: ToolConfig = {"env_vars": env_vars, "tool_params": tool_params}

        path = output or "your_tool_name_config.json"
        with open(path, "w") as f:
            json.dump(cfg, f, indent=2)

        console.print(f"[green]✅ Saved your_tool_name config to {path}[/green]")
        if verbose:
            console.print(Panel.fit(json.dumps(cfg, indent=2), title="[bold green]Configuration[/bold green]"))
        return cfg

    @classmethod
    def status(cls, verbose: bool = False) -> None:
        import os
        prefix = os.getenv("MCP_YOUR_TOOL_NAME_PREFIX", "")
        msg = f"Prefix: '{prefix or '[none]'}'"
        console.print(Panel.fit(msg, title="[bold green]your_tool_name status[/bold green]"))
