
![SkillBridge banner](assets/banner.svg)

# SkillBridge v0.8.0

**Any app. Any language. Any agent.** A local-first toolkit for discovering and integrating app capabilities with AI agents.

[![PyPI](https://img.shields.io/pypi/v/skillbridge-ai)](https://pypi.org/project/skillbridge-ai/) [![MIT](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

**v0.8.0 is published on [PyPI](https://pypi.org/project/skillbridge-ai/0.8.0/).** Install the Python package with `pip install skillbridge-ai`. The Rust native library and npm wrapper are separate source components; the Python wheel does not bundle a compiled Rust library, and the npm wrapper is not published to npm.

## Install and quickstart

```bash
python -m pip install --upgrade skillbridge-ai
python -m skillbridge.cli roots --add examples/autodiscovery
python -m skillbridge.cli connect TestApp
python -m skillbridge.cli auto TestApp
python -m skillbridge.cli agent TestApp --model YOUR_LM_STUDIO_MODEL
```

The example commands assume you have cloned this repository so the `examples/` directory exists. The agent command requires an OpenAI-compatible local server at `127.0.0.1:1234/v1` and a model with tool-calling support. Commands require confirmation before execution.

For development from a checkout:

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
```

## Capabilities

| Feature | Scope |
|---|---|
| JSON / Markdown skill discovery | Discover declared capabilities; Markdown is documentation, not executable code |
| Local app-name discovery | Searches explicitly registered directories |
| Transport selection | Local manifests and local OpenAPI JSON; no remote endpoint probing |
| MCP stdio | JSON-RPC `tools/list` and `tools/call`; newline-delimited output; compatible with older Content-Length input frames |
| Local LM Studio agent | Tool-calling prototype with per-invocation confirmation |
| Forge integration | Framework-neutral adapter example; actual integration requires Forge tool registration |
| Rust C ABI | Native source for building shared libraries on supported operating systems |
| C++ / Go / Node / Rust / Python | Example integrations; native examples require a compiled library |
| npm / npx wrapper | Local source wrapper requiring Python; not published to npm |
| WASI runner | Uses an externally installed Wasmtime CLI; not a comprehensive security sandbox |
| Signed manifests / granular permissions | Not implemented |

## Discover apps by name

```bash
skillbridge roots --add ./examples/autodiscovery
skillbridge connect TestApp
skillbridge auto TestApp
```

The registry is stored in `~/.config/skillbridge/registry.json` by default. Override this with `SKILLBRIDGE_CONFIG`. Discovery does not blindly crawl the filesystem, scan the network, or install packages.

To inspect OS-specific candidate application directories and opt in to searching them:

```bash
skillbridge system-roots
skillbridge system-connect AppName
```

This does not probe running processes or network endpoints.

## MCP stdio

```bash
skillbridge mcp examples/manifests
```

For an MCP client, configure the command `python` with arguments:

```text
-m skillbridge.cli mcp /absolute/path/to/examples/manifests
```

**MCP tool execution is denied by default.** `--allow-execute` enables execution of all command skills in the selected manifest directory. Use it only with manifests you trust. MCP stdio emits one JSON-RPC message per line on stdout, without diagnostic logs on stdout, and accepts older Content-Length input frames for compatibility.

## Local AI agent and Forge adapter

The local agent can connect to an OpenAI-compatible model server such as LM Studio. Tool calls require user confirmation.

`examples/forge/adapter.py` demonstrates framework-neutral tool registration. It is not a drop-in plugin for every Forge installation; connect it to your Forge build's actual tool interface.

## Native Rust C ABI

```bash
cargo test --manifest-path native/Cargo.toml
cargo build --release --manifest-path native/Cargo.toml
```

The build produces a `.dll` on Windows, `.so` on Linux, or `.dylib` on macOS. See `native/README.md` and `examples/native/`. Native callbacks run in-process, without isolation. The PyPI wheel does **not** contain these compiled native libraries.

## Local npm wrapper

The `npm/` directory contains an **unpublished** Node CLI wrapper that invokes the Python runtime. Install `skillbridge-ai` first.

```bash
python -m pip install skillbridge-ai
cd npm
npm pack
npm link
skillbridge --help
```

`npx @jekodev/skillbridge` requires a separate npm publication and should not be treated as publicly available yet.

## WASI runner

```bash
skillbridge wasm path/to/module.wasm
```

This invokes an **externally installed** Wasmtime CLI without preopened host directories. It is not a comprehensive sandbox and does not guarantee OS-level network isolation. Do not run untrusted modules without additional isolation.

## Security model

Discovery is read-only. Approved command execution uses `subprocess.run(..., shell=False)` with a timeout, **not a sandbox**. Approved commands run with the current user's privileges and can access resources that user can access. Use trusted manifests and exercise caution when enabling MCP execution. Signed manifests and granular permissions are not implemented.

## Testing and CI

```bash
python -m unittest discover -s tests -v
cargo test --manifest-path native/Cargo.toml
```

The repository includes GitHub Actions checks for Python, Rust and the npm package across supported environments. The v0.8.0 release workflow built the Python wheel and source distribution and published them to PyPI.

## What's new in v0.8.0

- MCP stdio writes newline-delimited JSON-RPC messages and keeps diagnostic output off stdout.
- Compatibility with older Content-Length input frames.
- Default-deny execution behavior for MCP command tools.
- Automated build and verification workflows for Python, native Rust and npm packaging.
- Python v0.8.0 wheel and source distribution released on PyPI.

## Release process

For a new PyPI release, update `pyproject.toml`, commit the changes, create a new version tag/release, and use the GitHub Actions trusted-publishing workflow. Published PyPI distributions are immutable: to update the description shown on PyPI, publish a new package version rather than trying to overwrite v0.8.0.

## License

[MIT](LICENSE)
