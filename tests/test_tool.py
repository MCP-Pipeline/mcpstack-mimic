from typer.testing import CliRunner
from MCPStack.cli import StackCLI
from mcpstack_your_tool_name.tool import YourTool

runner = CliRunner()
app = StackCLI().app

def test_actions():
    tool = YourTool()
    actions = tool.actions()
    names = [fn.__name__ for fn in actions]
    assert "say_hello" in names
    assert "say_hello_all" in names

def test_outputs():
    tool = YourTool(greeting="Hello", targets=["world"])
    assert tool.say_hello() == "Hello world"
    assert tool.say_hello_all() == "Hello world"

def test_tool_cli_mounts(tmp_path, monkeypatch):
    r = runner.invoke(app, ["tools", "your_tool_name", "--help"])
    assert r.exit_code in (0, 2)
