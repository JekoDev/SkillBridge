![SkillBridge banner](assets/banner.svg)

# SkillBridge v0.6.0 (source preview)

**Any app. Any language. Any agent.** A local-first discovery and integration toolkit for agent-accessible app capabilities.

[![PyPI](https://img.shields.io/pypi/v/skillbridge-ai)](https://pypi.org/project/skillbridge-ai/) [![MIT](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

> **Publishing note:** v0.6.0 is a source preview. PyPI's latest version may be older. Install from this checkout to test these features.

## Quickstart

```bash
python -m pip install -e .
python -m skillbridge.cli roots --add examples/autodiscovery
python -m skillbridge.cli connect TestApp
python -m skillbridge.cli auto TestApp
python -m skillbridge.cli agent TestApp --model YOUR_LM_STUDIO_MODEL
```

The agent command requires an OpenAI-compatible local server on `127.0.0.1:1234/v1` and an LLM with tool-calling support. It requests confirmation before executing commands.

## Interfaces

| Feature | Status | Notes |
|---|---|---|
| JSON / Markdown skill discovery | Working | Markdown is documentation, not executable code |
| Local app-name discovery | Working | Explicit configured roots only, no OS-wide blind scan |
| Automatic transport selection | Partial | Local manifest or local OpenAPI JSON; not remote probing |
| MCP stdio | Prototype | JSON-RPC tools/list and tools/call |
| Local LM Studio agent | Prototype | Tool calling with per-invocation confirmation |
| Forge integration | Adapter/example | Requires registration in Forge's actual tool interface |
| Rust C-ABI core | Source available | Build on target OS with Cargo; not included in Python wheel |
| C++/Go/Node/Rust/Python examples | Source available | Native examples require a compiled shared library |
| npm/npx wrapper | Source available | Requires Python runtime; npm package not published |
| OpenAPI | Discovery only | Does not execute remote endpoints |
| WASM sandbox | Not implemented | Never run untrusted skills |
| Signed manifests / granular permissions | Not implemented | No cryptographic trust model |

## Discovery by name

```bash
skillbridge roots --add ./examples/autodiscovery
skillbridge connect TestApp
skillbridge auto TestApp
```

Registry is stored in `~/.config/skillbridge/registry.json` by default; override with `SKILLBRIDGE_CONFIG`. You must explicitly register directories. No arbitrary filesystem crawling, network scanning or package installation occurs.

## MCP / Forge

```bash
skillbridge mcp examples/manifests
```

Configure your MCP client with command `python`, args `['-m','skillbridge.cli','mcp','/absolute/path/to/examples/manifests']`. By default tool calls are **denied**; `--allow-execute` grants the server process permission to execute trusted commands, so only use it in a tightly controlled local setup.

`examples/forge/adapter.py` shows a generic tool registration adapter. **It is not a plug-in for a specific Forge build**: the actual Forge integration requires its tool registration interface.

## Native C ABI

```bash
cd native
cargo test
cargo build --release
```

Build produces `.dll` on Windows, `.so` on Linux, or `.dylib` on macOS. See `native/README.md` and `examples/native/`. Native callbacks run in-process, with no isolation.

## npm / npx

The `npm/` directory contains an **unpublished** Node CLI wrapper. It calls the Python runtime, so install Python first.

```bash
python -m pip install -e .
cd npm
npm link
skillbridge --help
```

After independently publishing the npm package, `npx @jekodev/skillbridge` would become possible. Do not advertise this command as available before publication.

## Security

Discovery is read-only. Command execution requires explicit approval and uses `subprocess.run(..., shell=False)` with a timeout, **not a sandbox**. An approved command can still access everything your user can. Do not load untrusted manifests or run arbitrary shell tools. A real sandbox and signed manifest verification remain future work.

## Test

```bash
python -m unittest discover -s tests -v
```

## Release

To publish to PyPI, update `pyproject.toml`, commit and tag a new version, then run the GitHub Actions trusted-publishing workflow. Never overwrite a published version. See [MIT license](LICENSE).


## v0.7.0 additions (source release)

- MCP stdio supports `Content-Length` JSON-RPC frames and legacy newline-delimited messages.
- `skillbridge system-roots` shows OS-specific candidate app folders. `skillbridge system-connect AppName` opts in to searching those folders. No processes or network endpoints are probed.
- `skillbridge wasm path/to/module.wasm` runs a WASI module using an **externally installed** `wasmtime` CLI without preopened host directories. Runtime security depends on Wasmtime and host configuration; this is not a comprehensive sandbox for arbitrary code.
- `npm/` contains a Node CLI wrapper, but `npx @jekodev/skillbridge` requires separate npm publication and an installed Python `skillbridge-ai` runtime.
- Forge adapter is framework-neutral; direct Forge application integration requires adapting Forge's actual plugin/tool interface.
- Rust C-ABI source is included, but Rust compilation and cross-platform binary testing remain necessary.

### Publishing

This source version is **not yet published** to PyPI or npm. Run tests and build in your environment before tagging `v0.7.0`.


## v0.8: verified MCP stdio and automated build checks

`skillbridge mcp examples/manifests` now writes **one JSON-RPC message per line**
to stdout, as required by MCP stdio. It continues accepting older Content-Length
input frames for compatibility. No logs are printed to stdout. Executable tools
are denied by default; `--allow-execute` is a deliberate trust decision and
allows **all** command skills in the chosen manifest. Only use trusted manifests.

`/.github/workflows/ci.yml` tests Python on Linux, Windows and macOS, builds
the Rust C-ABI library on all three operating systems, and checks the npm
package. CI execution on GitHub must be confirmed after pushing.

### Native build

```bash
cargo test --manifest-path native/Cargo.toml
cargo build --release --manifest-path native/Cargo.toml
```

### Local npm wrapper (no publication required)

```bash
cd npm
npm pack
# npm exec --package ./jekodev-skillbridge-0.8.0.tgz -- skillbridge --help
```

The npm wrapper **requires** an installed Python `skillbridge-ai` package.
Publishing to npm and PyPI is a separate maintainer action, not automated here.

### Security scope

The WASI runner invokes the external Wasmtime CLI without preopened directories.
This is not a comprehensive sandbox, does not impose OS-level network isolation,
and should not be used for untrusted workloads without an external isolation
boundary. The command runner executes with the current user's privileges.
