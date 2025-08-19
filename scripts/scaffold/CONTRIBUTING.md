# How to add new stuff to MCPStack-Tool?

Hey there! Appreciated your venue here! Want to build stuff on top of MCPStack-Tool?

## Prerequisites

- Python 3.9+
- [uv](https://docs.astral.sh/uv/) (preferred package/dependency manager)
- `pre-commit` and `ruff`
- Git (with your GitHub SSH set up if you push to a fork)

## Setup

Clone the repository and sync dependencies:

```bash
git clone git@github.com:<you>/mcpstack-tool.git
cd mcpstack-tool
uv sync --all-extras
pre-commit install

# uv automatically installs in editable mode.
# To manage dependencies:

uv add <package>      # add a package
uv remove <package>   # remove a package
uv lock               # update lockfile
```

See the uv documentation for installation instructions.

Branches & Commits
* Branch from main: feat/<slug>, fix/<slug>, chore/<slug>. 
* Keep commits focused and descriptive. Conventional commits are welcome: feat:, fix:, chore:, docs:.

Code Style
* Ruff is the source of truth for linting and formatting (ruff + ruff format).
* Line length: 100 (pyproject.toml).
* Prefer readable code over clever code. Add comments if intent isn’t obvious.

Tests
* Add tests for behavior changes. Minimal repro-style tests are acceptable.
* Keep test data lightweight and local.

Running Checks

```bash
pre-commit run --all-files
python -m mcpstack_tool.cli --health
```

PR Expectations
* Fill out the PR template (if present).
* Link to the issue you’re fixing.
* Include logs or minimal repros when relevant.
* Keep diffs reviewable. Split large changes into smaller PRs.

Security
* Never commit secrets or datasets.
* Do not upload datasets to GitHub issues or pull requests. Use synthetic or anonymized examples when reporting bugs.
* Report vulnerabilities privately first when possible.

Thanks for contributing!
