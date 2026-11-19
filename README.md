# SkillBridge

**Any app. Any language. Any agent.**

SkillBridge is a local-first, open-source toolkit that helps AI agents discover and use capabilities exposed by applications. Describe tools through manifests, connect them to an agent, and keep execution under your control.

[![PyPI](https://img.shields.io/pypi/v/skillbridge-ai)](https://pypi.org/project/skillbridge-ai/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

**Current release: v0.8.0** · [PyPI](https://pypi.org/project/skillbridge-ai/0.8.0/) · [GitHub](https://github.com/JekoDev/SkillBridge)

## Why SkillBridge?

Applications expose useful actions in different ways. SkillBridge provides a common starting point for discovering those actions and presenting them as tools to AI agents, without requiring every integration to be hardcoded into the agent itself.

- **Discover capabilities:** Load JSON-based manifests and documented skills from explicitly registered directories.
- **Connect by app name:** Register search roots, then find and connect supported applications.
- **Work with existing interfaces:** Integrate local OpenAPI descriptions and MCP stdio tools.
- **Build local AI workflows:** Use an OpenAI-compatible local model server, such as LM Studio.
- **Extend across languages:** Explore a Rust native C ABI and examples for Python, Node.js, C++, Go, and Rust.
- **Stay in control:** Discovery is read-only; agent command execution requires confirmation.

## Installation

Requires Python 3.10 or newer.

```bash
python -m pip install --upgrade skillbridge-ai
```

For development and the included examples:

```bash
git clone https://github.com/JekoDev/SkillBridge.git
cd SkillBridge
python -m pip install -e .
```

## Quick start

From a cloned repository, register the included example directory and discover an application:

```bash
python -m skillbridge.cli roots --add examples/autodiscovery
python -m skillbridge.cli connect TestApp
python -m skillbridge.cli auto TestApp
```

To try the local AI agent, start an OpenAI-compatible model server at `127.0.0.1:1234/v1` (for example, LM Studio) with a tool-capable model, then run:

```bash
python -m skillbridge.cli agent TestApp --model YOUR_LM_STUDIO_MODEL
```

The `examples/` directory is part of the GitHub repository, not the PyPI installation. Agent command execution requires user confirmation.

## Core features

### Application discovery

Register the directories you want SkillBridge to search, then connect an application by name. SkillBridge uses explicit discovery roots rather than silently scanning your entire computer.

```bash
python -m skillbridge.cli system-roots
python -m skillbridge.cli system-connect AppName
```

### MCP integration

Expose manifest-backed tools to MCP clients over stdio:

```bash
python -m skillbridge.cli mcp examples/manifests
```

For clients that accept a command and arguments, use `python` with:

```text
-m skillbridge.cli mcp /absolute/path/to/examples/manifests
```

MCP uses newline-delimited JSON-RPC output and accepts legacy Content-Length input frames. Command-tool execution is disabled by default; `--allow-execute` enables it for the selected manifest directory. Only enable execution for manifests you trust.

### Local AI agents

SkillBridge includes a prototype agent that can call discovered tools through an OpenAI-compatible local model endpoint. The included Forge adapter example shows how to connect SkillBridge capabilities to a separate agent application; adapt its registration to your own Forge setup.

### Native Rust integration

The native component exposes a C ABI for integration with other languages. Build it from source:

```bash
cargo test --manifest-path native/Cargo.toml
cargo build --release --manifest-path native/Cargo.toml
```

See `native/README.md` and `examples/native/` for integration examples. The Python package does not include a precompiled native library.

### Node.js wrapper

The repository includes a local Node.js CLI wrapper around the Python runtime:

```bash
python -m pip install skillbridge-ai
cd npm
npm pack
npm link
skillbridge --help
```

The wrapper is provided in the repository; it is not currently a separately published npm package.

### WASI support

Run a WASI module through an externally installed Wasmtime CLI:

```bash
python -m skillbridge.cli wasm path/to/module.wasm
```

Wasmtime must be installed separately. This integration is not a complete security sandbox.

## Security and execution

SkillBridge separates capability discovery from execution. Discovery is read-only, and the local agent requests confirmation before running commands. Approved commands execute with the permissions of the current operating-system user; they are not isolated in a sandbox. Review manifests before enabling command execution, especially in MCP mode.

## Development and tests

```bash
python -m unittest discover -s tests -v
cargo test --manifest-path native/Cargo.toml
```

The repository includes automated verification workflows for Python and native components, along with package-building checks.

## What's new in v0.8.0

- Improved MCP stdio interoperability with newline-delimited JSON-RPC output and legacy Content-Length input compatibility.
- Default-deny behavior for MCP command execution.
- Automated verification and release packaging for the Python distribution.
- Published Python wheel and source distribution on PyPI.

## Contributing

Issues, ideas, and pull requests are welcome. Explore the examples, run the tests, and open an issue to discuss changes or report a problem.

## License

SkillBridge is released under the [MIT License](LICENSE).
