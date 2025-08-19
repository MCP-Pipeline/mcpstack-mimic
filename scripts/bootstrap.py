from __future__ import annotations

import json
import os
import re
import shutil
import sys
from pathlib import Path
from typing import Optional

import typer
import rich.box as box
from rich.cells import cell_len
from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.prompt import Confirm
from rich.prompt import Prompt
from rich_pyfiglet import RichFiglet

console = Console()


def _display_banner() -> None:
    """Render the MCPStack banner when help is requested.

    The banner is shown only if ``--help`` or ``-h`` is present in ``sys.argv``.
    It uses RichFiglet for the headline and aligns a metadata panel identical
    to the MCPStack banner.

    Returns:
        None
    """
    if not any(arg in sys.argv for arg in ["--help", "-h"]):
        return

    rich_fig = RichFiglet(
        "MCPStack",
        font="ansi_shadow",
        colors=["#0ea5e9", "#0ea5e9", "#0ea5e9", "#FFFFFF", "#FFFFFF"],
        horizontal=True,
        remove_blank_lines=True,
    )

    try:
        from mcpstack_your_tool_name import __version__  # type: ignore
        version = __version__
    except Exception:
        version = "0.0.0"

    entries = [
        ("🏗️", " Project", "MCPStack Tool Template — Tool Template Builder"),
        ("🏎️", " Version", version),
    ]
    max_label_len = max(cell_len(emoji + " " + key + ":") for emoji, key, _ in entries)

    group_items: list[Text | Group] = [
        Text(""),
        Text(""),
        rich_fig,
        Text(""),
        Text("Composable MCP pipelines.", style="default"),
        Text(""),
    ]

    for i, (emoji, key, value) in enumerate(entries):
        label_plain = emoji + " " + key + ":"
        label_len = cell_len(label_plain)
        spaces = " " * (max_label_len - label_len + 2)
        line = f"[turquoise4]{label_plain}[/turquoise4]{spaces}{value}"
        group_items.append(Text.from_markup(line))
        if i == 0:
            group_items.append(Text(""))

    group_items += [Text(""), Text("")]

    console.print(
        Panel(
            Group(*group_items),
            title="MCPStack CLI",
            width=80,
            title_align="left",
            expand=False,
            box=box.ROUNDED,
            padding=(1, 5),
        )
    )


_display_banner()


app = typer.Typer(
    help="🧰 MCPStack Tool Bootstrap — init config, preview changes, apply replacements, validate, reset.",
    add_completion=False,
    pretty_exceptions_show_locals=False,
    rich_markup_mode="markdown",
)


def _find_repo_root(start: Path) -> Path:
    """Locate the repository root by walking upward for ``pyproject.toml``.

    Args:
        start: Starting path, typically the current file location.

    Returns:
        The nearest ancestor directory containing ``pyproject.toml`` or the
        original ``start`` if none is found.
    """
    p = start
    while p != p.parent:
        if (p / "pyproject.toml").exists():
            return p
        p = p.parent
    return start


TEMPLATE_ROOT = _find_repo_root(Path(__file__).resolve())
SRC = TEMPLATE_ROOT / "src"
SCAFFOLD_DIR = TEMPLATE_ROOT / "scripts" / "scaffold"
CONFIG_PATH = TEMPLATE_ROOT / ".mcpstack-tool.json"

PLACEHOLDERS = {
    "tool_slug": "mimic",
    "class_name": "Mimic",
    "package_name": "mcpstack_mimic",
    "dist_name": "mcpstack-mimic",
    "env_prefix": "MCP_MIMIC",
}

FILE_GLOBS = ("**/*.py", "**/*.md", "**/*.toml", "**/*.yaml", "**/*.yml")


def derive_names(
    tool_slug: str,
    class_name: str,
    package_name: Optional[str] = None,
    dist_name: Optional[str] = None,
    env_prefix: Optional[str] = None,
):
    """Derive canonical naming variants for the tool.

    Args:
        tool_slug: Snake_case identifier for the tool.
        class_name: PascalCase class name.
        package_name: Optional explicit Python package name.
        dist_name: Optional explicit distribution (kebab-case) name.
        env_prefix: Optional explicit upper-snake environment variable prefix.

    Returns:
        A mapping containing ``tool_slug``, ``class_name``, ``package_name``,
        ``dist_name``, and ``env_prefix``.
    """
    slug_snake = tool_slug.lower().replace("-", "_")
    pkg = package_name or f"mcpstack_{slug_snake}"
    dist = dist_name or f"mcpstack-{tool_slug.lower().replace('_','-')}"
    env = env_prefix or f"MCP_{slug_snake.upper()}"
    return {
        "tool_slug": slug_snake,
        "class_name": class_name,
        "package_name": pkg,
        "dist_name": dist,
        "env_prefix": env,
    }


def is_valid_names(names: dict) -> tuple[bool, list[str]]:
    """Validate naming fields against allowed patterns.

    Args:
        names: Mapping produced by :func:`derive_names`.

    Returns:
        A pair ``(ok, errors)`` where ``ok`` indicates success and
        ``errors`` contains human-readable validation messages.
    """
    errs = []
    import re as _re
    if not _re.fullmatch(r"[a-z][a-z0-9_]*", names["tool_slug"]):
        errs.append("tool-slug must be snake_case: [a-z][a-z0-9_]*")
    if not _re.fullmatch(r"[A-Z][A-Za-z0-9_]*", names["class_name"]):
        errs.append("class-name must be PascalCase: [A-Z][A-Za-z0-9_]*")
    if not _re.fullmatch(r"[a-z][a-z0-9_]*", names["package_name"]):
        errs.append("package-name must be a valid module name: [a-z][a-z0-9_]*")
    if not _re.fullmatch(r"[a-z0-9][a-z0-9\-]*", names["dist_name"]):
        errs.append("dist-name must be kebab-case: [a-z0-9][a-z0-9-]*")
    if not _re.fullmatch(r"[A-Z0-9_]+", names["env_prefix"]):
        errs.append("env-prefix must be upper snake: [A-Z0-9_]+")
    return (len(errs) == 0, errs)


def replace_in_text(text: str, mapping: dict) -> str:
    """Apply placeholder replacements to a text blob.

    Args:
        text: The input text.
        mapping: Replacement mapping with keys used in project templates.

    Returns:
        The transformed text with placeholders replaced.
    """
    import re as _re
    patterns = [
        (r"\bmcpstack_your_tool_name\b", mapping["package_name"]),
        (r"\bmcpstack-your-tool-name\b", mapping["dist_name"]),
        (r"\bYourTool(?=[A-Z_])", mapping["class_name"]),
        (r"\bYourTool\b", mapping["class_name"]),
        (r"\byour_tool_name\b", mapping["tool_slug"]),
        (r"\bMCP_YOUR_TOOL_NAME(?=[A-Z0-9_])", mapping["env_prefix"]),
        (r"\bMCP_YOUR_TOOL_NAME\b", mapping["env_prefix"]),
    ]
    for pat, repl in patterns:
        text = _re.sub(pat, repl, text)
    return text


IGNORED_PARTS = {
    ".venv", ".git", "__pycache__", ".mypy_cache", ".pytest_cache",
    ".ruff_cache", "node_modules"
}
IGNORED_SUFFIXES = {".pyc", ".pyo", ".DS_Store"}

TEMPLATE_ROOT = Path(__file__).resolve().parents[1]
SRC = TEMPLATE_ROOT / "src"
TESTS = TEMPLATE_ROOT / "tests"

def _skip_path(p: Path) -> bool:
    """Determine whether a path should be excluded from processing.

    Args:
        p: Filesystem path to evaluate.

    Returns:
        True if the path should be skipped, otherwise False.
    """
    if any(part in IGNORED_PARTS for part in p.parts):
        return True
    if p.suffix in IGNORED_SUFFIXES:
        return True
    return False


def iter_files() -> "iter[Path]":
    """Yield file paths to be considered for replacement and checks.

    Yields:
        Paths inside ``src/`` recursively and the repository root
        ``pyproject.toml`` if present.
    """
    if SRC.exists() and TESTS.exists():
        files = list(SRC.rglob("*")) + list(TESTS.rglob("*"))
        for p in files:
            if not p.is_file():
                continue
            if _skip_path(p):
                continue
            yield p

    pyproj = TEMPLATE_ROOT / "pyproject.toml"
    if pyproj.exists() and pyproj.is_file():
        yield pyproj


def _save_config(cfg: dict) -> None:
    """Persist configuration to ``.mcpstack-tool.json``.

    Args:
        cfg: Configuration mapping to save.

    Returns:
        None
    """
    CONFIG_PATH.write_text(json.dumps(cfg, indent=2), encoding="utf-8")


def _load_config() -> Optional[dict]:
    """Load configuration from ``.mcpstack-tool.json`` if available.

    Returns:
        The parsed configuration mapping or ``None`` if missing or unreadable.
    """
    if CONFIG_PATH.exists():
        try:
            return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        except Exception:
            return None
    return None


def _ensure_names_from_sources(
    tool_slug: Optional[str],
    class_name: Optional[str],
    package_name: Optional[str],
    dist_name: Optional[str],
    env_prefix: Optional[str],
    prefer_config: bool = True,
) -> dict:
    """Resolve names from CLI flags, saved config, or placeholders.

    Args:
        tool_slug: Optional tool slug override.
        class_name: Optional class name override.
        package_name: Optional package name override.
        dist_name: Optional distribution name override.
        env_prefix: Optional environment prefix override.
        prefer_config: Whether to consult saved configuration first.

    Returns:
        A validated mapping of resolved names.

    Raises:
        typer.BadParameter: If validation fails.
    """
    cfg = _load_config() if prefer_config else None
    source = cfg.get("names", {}) if cfg else {}
    names = derive_names(
        tool_slug or source.get("tool_slug", PLACEHOLDERS["tool_slug"]),
        class_name or source.get("class_name", PLACEHOLDERS["class_name"]),
        package_name or source.get("package_name"),
        dist_name or source.get("dist_name"),
        env_prefix or source.get("env_prefix"),
    )
    ok, errs = is_valid_names(names)
    if not ok:
        raise typer.BadParameter("\n".join(errs))
    return names


@app.command(help="Create a config via an interactive wizard (no file changes).")
def init(
    tool_slug: Optional[str] = typer.Option(None, "--tool-slug", "-s", help="snake_case tool name (e.g. mimic_tool)"),
    class_name: Optional[str] = typer.Option(None, "--class-name", "-c", help="PascalCase tool class (e.g. MimicTool)"),
    package_name: Optional[str] = typer.Option(None, "--package-name", "-p", help="Python package name (e.g. mcpstack_mimic_tool)"),
    dist_name: Optional[str] = typer.Option(None, "--dist-name", "-d", help="Distribution/PyPI name (e.g. mcpstack-mimic-tool)"),
    env_prefix: Optional[str] = typer.Option(None, "--env-prefix", "-e", help="ENV prefix (UPPER_SNAKE, e.g. MCP_MIMIC_TOOL)"),
    non_interactive: bool = typer.Option(False, "--non-interactive", help="Don't prompt; use only provided flags or defaults"),
) -> None:
    """Create and save the bootstrap configuration.

    Builds ``.mcpstack-tool.json`` with the resolved names. Optionally
    proceeds to preview and apply steps based on user confirmation.

    Args:
        tool_slug: Optional tool slug override.
        class_name: Optional class name override.
        package_name: Optional package name override.
        dist_name: Optional distribution name override.
        env_prefix: Optional environment prefix override.
        non_interactive: Disable prompts and rely on provided values.
    """
    cfg_existing = _load_config() or {}
    existing = cfg_existing.get("names", {})

    def _ask(default: str, prompt: str) -> str:
        return Prompt.ask(prompt, default=default)

    if not non_interactive:
        ts_default = tool_slug or existing.get("tool_slug") or PLACEHOLDERS["tool_slug"]
        tool_slug = _ask(ts_default, "🔧 Tool slug (snake_case)")

        cls_default = class_name or existing.get("class_name") or " ".join(
            part.capitalize() for part in ts_default.split("_")
        ).replace(" ", "")
        class_name = _ask(cls_default, "🏷️  Class name (PascalCase)")

        pkg_default = package_name or existing.get("package_name") or f"mcpstack_{(tool_slug or ts_default)}"
        package_name = _ask(pkg_default, "📦 Package name (module)")

        dist_default = dist_name or existing.get("dist_name") or f"mcpstack-{(tool_slug or ts_default).replace('_','-')}"
        dist_name = _ask(dist_default, "📦 Distribution name (PyPI, kebab-case)")

        env_default = env_prefix or existing.get("env_prefix") or f"MCP_{(tool_slug or ts_default).upper()}"
        env_prefix = _ask(env_default, "🔑 ENV prefix (UPPER_SNAKE)")

    names = derive_names(
        tool_slug or existing.get("tool_slug", PLACEHOLDERS["tool_slug"]),
        class_name or existing.get("class_name", PLACEHOLDERS["class_name"]),
        package_name or existing.get("package_name"),
        dist_name or existing.get("dist_name"),
        env_prefix or existing.get("env_prefix"),
    )

    ok, errs = is_valid_names(names)
    if not ok:
        console.print(Panel.fit("\n".join(errs), title="[red]Invalid names[/red]", border_style="red"))
        raise typer.Exit(code=1)

    cfg = {"names": names}
    _save_config(cfg)
    console.print(Panel.fit(json.dumps(cfg, indent=2), title="[bold green]Saved .mcpstack-tool.json[/bold green]"))

    if Confirm.ask("👀 Run a preview now?", default=True):
        _do_preview(names)
    if Confirm.ask("🚀 Apply changes now?", default=False):
        _do_apply(names)


@app.command(help="Show replacements and an example diff using saved config (or flags).")
def preview(
    tool_slug: Optional[str] = typer.Option(None, "--tool-slug", "-s"),
    class_name: Optional[str] = typer.Option(None, "--class-name", "-c"),
    package_name: Optional[str] = typer.Option(None, "--package-name", "-p"),
    dist_name: Optional[str] = typer.Option(None, "--dist-name", "-d"),
    env_prefix: Optional[str] = typer.Option(None, "--env-prefix", "-e"),
    use_config: bool = typer.Option(True, "--use-config/--no-config", help="Prefer saved .mcpstack-tool.json"),
) -> None:
    """Preview derived names and show a sample transformed file.

    Args:
        tool_slug: Optional tool slug override.
        class_name: Optional class name override.
        package_name: Optional package name override.
        dist_name: Optional distribution name override.
        env_prefix: Optional environment prefix override.
        use_config: Prefer values from the saved configuration.

    Returns:
        None
    """
    names = _ensure_names_from_sources(tool_slug, class_name, package_name, dist_name, env_prefix, prefer_config=use_config)
    _do_preview(names)


def _do_preview(names: dict) -> None:
    """Render a preview of the derived names and sample replacement output.

    Args:
        names: Resolved naming mapping.

    Returns:
        None
    """
    console.print(Panel.fit(json.dumps(names, indent=2), title="[bold green]Derived Names[/bold green]"))
    sample_path = SRC / "mcpstack_your_tool_name" / "tool.py"
    if sample_path.exists():
        sample = sample_path.read_text(encoding="utf-8")
        preview_text = replace_in_text(sample, names)
        console.rule("Example: src/*/tool.py (after)")
        console.print(preview_text)
    else:
        console.print("[yellow]Example file not found; showing only names.[/yellow]")


@app.command(help="Apply replacements & move the package directory (uses saved config by default).")
def apply(
    tool_slug: Optional[str] = typer.Option(None, "--tool-slug", "-s"),
    class_name: Optional[str] = typer.Option(None, "--class-name", "-c"),
    package_name: Optional[str] = typer.Option(None, "--package-name", "-p"),
    dist_name: Optional[str] = typer.Option(None, "--dist-name", "-d"),
    env_prefix: Optional[str] = typer.Option(None, "--env-prefix", "-e"),
    use_config: bool = typer.Option(True, "--use-config/--no-config", help="Prefer saved .mcpstack-tool.json"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Proceed without confirmation"),
) -> None:
    """Execute replacements across files and relocate the package directory.

    Args:
        tool_slug: Optional tool slug override.
        class_name: Optional class name override.
        package_name: Optional package name override.
        dist_name: Optional distribution name override.
        env_prefix: Optional environment prefix override.
        use_config: Prefer values from the saved configuration.
        yes: Skip the confirmation prompt.
    """
    names = _ensure_names_from_sources(tool_slug, class_name, package_name, dist_name, env_prefix, prefer_config=use_config)
    _do_apply(names, yes=yes)


def _do_apply(names: dict, yes: bool = False) -> None:
    """Apply text replacements and move the template package directory.

    Args:
        names: Resolved naming mapping.
        yes: If True, proceed without confirmation.

    Returns:
        None
    """
    if not yes and not Confirm.ask("This will modify files. Continue?", default=False):
        raise typer.Exit()

    changes = 0
    for p in iter_files():
        txt = p.read_text(encoding="utf-8")
        new_txt = replace_in_text(txt, names)
        if new_txt != txt:
            p.write_text(new_txt, encoding="utf-8")
            changes += 1

    old_pkg_dir = SRC / "mcpstack_your_tool_name"
    new_pkg_dir = SRC / names["package_name"]
    moved = False
    if old_pkg_dir.exists() and old_pkg_dir != new_pkg_dir:
        new_pkg_dir.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(old_pkg_dir), str(new_pkg_dir))
        moved = True

    msg = f"Replacements applied in {changes} files."
    if moved:
        msg += f" Moved package dir to: {new_pkg_dir}"
    console.print(Panel.fit(msg, title="[green]Success[/green]"))
    console.print("- uv lock && uv sync\n- uv run pytest -q\n- uv run mcpstack list-tools")


@app.command(help="Validate current repository state and placeholder presence.")
def validate() -> None:
    """Validate presence of core placeholders across the repository.

    Returns:
        None
    """
    missing = []
    for _, val in PLACEHOLDERS.items():
        found = False
        for p in iter_files():
            if val in p.read_text(encoding="utf-8"):
                found = True
                break
        if not found:
            missing.append(val)
    if missing:
        console.print(Panel.fit("\n".join(missing), title="[yellow]Some placeholders not found[/yellow]"))
    else:
        console.print(Panel.fit("All core placeholders present.", title="[green]OK[/green]"))


@app.command(help="Reset files from scaffold.")
def reset(
    hard: bool = typer.Option(False, "--hard", help="Overwrite with pristine scaffold")
) -> None:
    """Restore files from the scaffold directory.

    Replaces ``src/`` and ``tests/`` entirely and force-overwrites
    ``pyproject.toml`` and ``README`` from the scaffold.

    Args:
        hard: If True, perform a destructive reset.

    Raises:
        typer.Exit: If scaffold is missing or operation is aborted.
    """
    if not hard:
        console.print("Tip: use git restore/clean or run with --hard (to overwrite everything — To Your Own Risk!)")
        raise typer.Exit()

    if not SCAFFOLD_DIR.exists():
        console.print(Panel.fit("scaffold/ not found.", title="[red]Missing scaffold[/red]"))
        raise typer.Exit(code=1)

    scaffold_src = SCAFFOLD_DIR / "src"
    scaffold_tests = SCAFFOLD_DIR / "tests"
    scaffold_pyproject = SCAFFOLD_DIR / "pyproject.toml"
    scaffold_readme = (
        SCAFFOLD_DIR / "README.md" if (SCAFFOLD_DIR / "README.md").exists()
        else SCAFFOLD_DIR / "README.rst"
    )

    if SRC.exists():
        shutil.rmtree(SRC)
    if scaffold_src.exists():
        shutil.copytree(scaffold_src, SRC)
    else:
        console.print(Panel.fit("scaffold/src not found — skipped.", title="[yellow]Warning[/yellow]"))

    TESTS = TEMPLATE_ROOT / "tests"
    if TESTS.exists():
        shutil.rmtree(TESTS)
    if scaffold_tests.exists():
        shutil.copytree(scaffold_tests, TESTS)
    else:
        console.print(Panel.fit("scaffold/tests not found — skipped.", title="[yellow]Warning[/yellow]"))

    if scaffold_pyproject.exists():
        shutil.copy2(scaffold_pyproject, TEMPLATE_ROOT / "pyproject.toml")
    else:
        console.print(Panel.fit("scaffold/pyproject.toml not found — skipped.", title="[yellow]Warning[/yellow]"))

    if scaffold_readme.exists():
        dest_name = scaffold_readme.name
        shutil.copy2(scaffold_readme, TEMPLATE_ROOT / dest_name)
    else:
        console.print(Panel.fit("scaffold/README not found — skipped.", title="[yellow]Warning[/yellow]"))

    console.print(Panel.fit(
        "src/, tests/, pyproject.toml and README restored from scaffold.",
        title="[green]Reset complete[/green]"
    ))


@app.command(help="Health-check: entry points, package dir, placeholders, and CI files.")
def doctor() -> None:
    """Show a simple health report for the repository state.

    Returns:
        None
    """
    rows = []
    pkg_dirs = [p for p in (SRC).glob("mcpstack_*") if p.is_dir()]
    rows.append(("Package dirs", ", ".join(p.name for p in pkg_dirs) or "(none)"))
    pt = (TEMPLATE_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    ep_ok = '[project.entry-points."mcpstack.tools"]' in pt
    rows.append(("Entry point", "present" if ep_ok else "missing"))
    ph = [f"{k} → `{v}`" for k, v in PLACEHOLDERS.items()]
    rows.append(("Placeholders", "; ".join(ph)))

    t = Table(box=box.SIMPLE, show_header=True)
    t.add_column("Check", style="cyan")
    t.add_column("Result", style="green")
    for k, v in rows:
        t.add_row(k, v)
    console.print(t)


if __name__ == "__main__":
    app()
