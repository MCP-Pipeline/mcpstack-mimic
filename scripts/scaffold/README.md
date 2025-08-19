<!--suppress HtmlDeprecatedAttribute -->
<div align="center">
  <h1 align="center">
    <br>
    <a href="#"><img src="assets/COVER.png" alt="MCPStack Tool" width="100%"></a>
    <br>
    MCPStack Tool Builder
    <br>
  </h1>
  <h4 align="center">A Template To Fasten The Creation of MCP-Stack MCP Tools</h4>
</div>

<div align="center">

<a href="https://pre-commit.com/">
  <img alt="pre-commit" src="https://img.shields.io/badge/pre--commit-enabled-1f6feb?style=for-the-badge&logo=pre-commit">
</a>
<img alt="ruff" src="https://img.shields.io/badge/Ruff-lint%2Fformat-9C27B0?style=for-the-badge&logo=ruff&logoColor=white">
<img alt="python" src="https://img.shields.io/badge/Python-3.9%2B-3776AB?style=for-the-badge&logo=python&logoColor=white">
<img alt="license" src="https://img.shields.io/badge/License-MIT-success?style=for-the-badge">

</div>

> [!IMPORTANT]
> If you have not been across the MCPStack main orchestrator repository, please start
> there: [View Org](https://github.com/MCP-Pipeline)

## <a id="about-the-project"></a>💡 About The Project

`MCPStack Tool Builder` is a template repository designed to streamline the creation of `MCPStack` MCP Tools.
As in, you are using the `MCPStack` main orchestrator repository and wish to create a new MCP tool to pipeline with.
You can always start from scratch, but certainly, our `MCPStack Tool Builder` will help you get started quickly with a
solid foundational skeleton builder.

**Wait, what is a Model Context Protocol (MCP) & `MCPStack` — In layman's terms ?**

The Model Context Protocol (MCP) standardises interactions with machine learning (Large Language) models, 
enabling tools and libraries to communicate successfully with a uniform workflow. 

On the other hand, `MCPStack` is a framework that implements the protocol, and most importantly, allowing
developers to create pipelines by stacking MCP tools of interest and launching them all in Claude Desktop. 
This allows the LLM to use all the tools stacked, and of course, if a tool is not of interest, do not include it in the
pipeline and the LLM won't have access to it.

## Installation

> [!NOTE]
> As this repository is a template, you can always create a new repository from this template. Use 
> the "Use this template" button on the top right of the GitHub UI to create a new repository based on this template.

Meanwhile, you may alos clone this repository and install it locally to start building your own `MStack` MCP tool.

### Clone the repository

```bash
git clone https://github.com/MCP-Pipeline/MCPStack-Tool-Builder.git
cd MCPStack-Tool-Builder
```

### Install dependencies

Using `UV` (recommended —— See official [UV documentation for installation of UV](https://uv.dev/docs/)):

```bash
uv sync
```

Using `pip`:

```bash
pip install -e .[dev]
```

### Install pre-commit hooks

Via `UV`:

```bash
uv run pre-commit install
```

Via `pip`:

```bash
pre-commit install
```

## Create Your Tool's Skeleton

Once dependencies are installed, you can use the `mcpstack_tool` CLI to bootstrap and customise your tool’s skeleton.  
Every commands is run with `uv run mcpstack_tool.py` or `python mcpstack_tool.py` if you are not using `UV`, followed by the command you want to run; as follows:

<img src="assets/readme/help.gif" width="61.8%" align="left" style="border-radius: 10px;"/>

### `Help` Banner

Run with `--help` or `-h` to display the banner and see all available commands.

```bash
uv run mcpstack_tool.py --help
```

<br clear="left">

<br />

<img src="assets/readme/init.gif" width="61.8%" align="right" style="border-radius: 10px;"/>

### `Init`

init starts an interactive prompt command-line-based process to generate your tool configuration.
It will ask you for values like `tool_slug`, `class_name`, and `env_prefix`.


<br clear="right">

<br />

<img src="assets/readme/preview.gif" width="61.8%" align="left" style="border-radius: 10px;"/>

### `Preview`

preview shows you the replacements that would be applied across the codebase and displays an example diff.
Note this could be also run from the `init`.

<br clear="left">

<br />

<img src="assets/readme/apply.gif" width="61.8%" align="right" style="border-radius: 10px;"/>

### `Apply`

Once happy, use apply to perform replacements and rename the package directory. Note this could be also run from the `init`.

<br clear="right">

<br />

<img src="assets/readme/validate.gif" width="61.8%" align="left" style="border-radius: 10px;"/>

### `Validate`

Run validate to ensure placeholders were replaced correctly (or to check if any remain).

<br clear="left">

<br />

<img src="assets/readme/reset.gif" width="61.8%" align="right" style="border-radius: 10px;"/>

### `Reset` (Optional)

Need to start fresh? Restore everything back from the scaffold with reset.

> [!CAUTION]
> ⚠️ Use --hard to overwrite files directly.

<br clear="right">

<br />

<img src="assets/readme/doctor.gif" width="61.8%" align="left" style="border-radius: 10px;"/>

### `Doctor`

Finally, check the health of your repository with doctor.
It reports `package dirs`, `entry points`, and `placeholder` status.

<br />
<br />
<br />

Here you go! 🎉 You now have a working `MCPStack` tool skeleton ready to customise.
From here, edit `src/mcpstack_<your_tool_name>/tool.py` with the actions your MCP is aimed to be doing,
and `cli.py` to implement your configurability logic. Remove a couple of files and folders not necessary as per the template
and you may be good to go to submit this to the org or to play with it yourself!

Refer to the `MCPStack` documentation for more details on how to implement your tool logic.

## 🔐 License

MIT — see **[LICENSE](LICENSE)**.
