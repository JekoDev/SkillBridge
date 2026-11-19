![SkillBridge banner](assets/banner.svg)

# SkillBridge

**Any app. Any language. Any agent.** Discover application capabilities without requiring every application to implement an agent protocol. A small, language-neutral, local-first proof of concept.

[![PyPI](https://img.shields.io/pypi/v/skillbridge-ai)](https://pypi.org/project/skillbridge-ai/) [![Python](https://img.shields.io/pypi/pyversions/skillbridge-ai)](https://pypi.org/project/skillbridge-ai/) [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE) [![GitHub](https://img.shields.io/badge/GitHub-JekoDev%2FSkillBridge-181717?logo=github)](https://github.com/JekoDev/SkillBridge)

> **Status: v0.1.0 MVP.** The working features are local Markdown/JSON discovery, permission-gated command execution, and an optional token-protected Python HTTP bridge. **Not yet implemented:** automatic scanning of installed apps, MCP/OpenAPI adapters, native Rust core/DLL, npx installer, sandboxed execution, or automatic LLM integration. This is not an MCP implementation.

## Install in seconds

**Published on [PyPI as `skillbridge-ai`](https://pypi.org/project/skillbridge-ai/).** Requires Python 3.10+.

```bash
python -m pip install --upgrade skillbridge-ai
```

Then discover capabilities in an app folder:

```bash
skillbridge discover ./my-app
skillbridge inspect ./my-app
```

**Windows PATH note:** If `skillbridge` is not recognized, add your Python user Scripts directory to PATH (for example, `%APPDATA%\Python\Python311\Scripts` for Python 3.11) and open a new terminal. Alternatively, run the executable using its full path.

To try the included sample manifests, clone the repository:

```bash
git clone https://github.com/JekoDev/SkillBridge.git
cd SkillBridge
skillbridge discover examples/manifests
skillbridge inspect examples/manifests
```

To contribute or install an editable development copy:

```bash
python -m pip install -e .
```

**Naming:** The distribution is `skillbridge-ai`; the Python import and CLI command remain `skillbridge`.

## Zero-server discovery

Create `skillbridge.json` in any application folder:

```json
{
  "app": "TestApp",
  "skills": [
    {
      "name": "greet",
      "description": "Say hello to a user",
      "type": "command",
      "inputs": {"name": "string"},
      "argv": ["python", "hello.py", "{name}"]
    }
  ]
}
```

A compatible agent or tool runner can discover it with:

```bash
skillbridge discover ./testapp
```

Alternatively, create `SKILL.md` or `AGENT.md`. SkillBridge will read it as **documentation only**, not silently execute commands mentioned in Markdown.

### Call a command (requires explicit approval)

```bash
skillbridge call examples/manifests greet --args '{"name":"Forge"}' --allow-execute
```

On PowerShell, quoting JSON varies by shell. The CLI deliberately refuses execution without `--allow-execute`. Commands use argv arrays and `shell=False`, but this **does not sandbox** programs. Only run manifests you trust.

## Python: expose real functions

```python
from skillbridge import Bridge

bridge = Bridge("TestApp")
bridge.expose("greet", "Say hello", lambda name: f"Hi {name}", {"name": "string"})
bridge.serve()  # 127.0.0.1:8765, prints generated bearer token
```

Run `python examples/python/app.py`. A client with the token can then request:

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" http://127.0.0.1:8765/manifest
curl -X POST http://127.0.0.1:8765/call -H "Authorization: Bearer YOUR_TOKEN" -H "Content-Type: application/json" -d '{"skill":"greet","args":{"name":"Forge"}}'
```

**Keep the token private.** The HTTP bridge is loopback-only, not production-hardened, and functions run with your application's permissions. Do not expose it to untrusted users.

## Examples in five languages

The same `skillbridge discover` JSON output can be consumed by any language. The examples demonstrate **CLI interoperability**, not native bindings or direct function exposure for every language.

| Language | Example | Run from directory |
| --- | --- | --- |
| Python | [`examples/python/app.py`](examples/python/app.py) | `python app.py` |
| TypeScript / Node.js | [`examples/typescript/demo.mjs`](examples/typescript/demo.mjs) | `node demo.mjs` |
| Go | [`examples/go/main.go`](examples/go/main.go) | `go run main.go` |
| Rust | [`examples/rust/main.rs`](examples/rust/main.rs) | `rustc main.rs -o demo && ./demo` |
| C++ | [`examples/cpp/main.cpp`](examples/cpp/main.cpp) | `g++ main.cpp -o demo && ./demo` |

Run the cross-language examples from their own folders after installing the CLI.

## Architecture

```text
Existing app -> skillbridge.json / SKILL.md
                          |
Agent / SDK -> discovery CLI -> JSON capabilities
                          |
                   explicit approval
                          |
                    argv execution

Python app -> Bridge.expose() -> local HTTP /manifest + /call
```

**Design direction:** add pluggable adapters for MCP, OpenAPI, HTTP and native ABI while retaining one capability schema. Discovery is read-only; execution is separately authorized. No LLM is required to test the bridge.

## Security boundaries

- Local discovery never runs a command.
- Commands require `--allow-execute` each invocation.
- Command inputs are type-checked; arguments are passed without a shell.
- The optional HTTP server binds to loopback and requires a bearer token.
- **No process isolation or sandbox exists in this MVP.** A malicious approved manifest can execute arbitrary programs. Inspect manifests before approving.
- Avoid exposing arbitrary SQL or filesystem operations. Design narrow, least-privilege skills.

## Test

```bash
python -m unittest discover -s tests -v
python -m build  # optional: first pip install build
```

## Distribution and releases

SkillBridge v0.1.0 is available on [PyPI](https://pypi.org/project/skillbridge-ai/):

```bash
pip install skillbridge-ai
```

Source code: [JekoDev/SkillBridge](https://github.com/JekoDev/SkillBridge). Releases: [GitHub Releases](https://github.com/JekoDev/SkillBridge/releases).

Maintainers publish new versions using GitHub Actions and PyPI Trusted Publishing. Update the version in `pyproject.toml`, commit the change, then trigger the configured publishing workflow. A version already uploaded to PyPI cannot be overwritten.

## Roadmap

- [x] Local JSON/Markdown discovery
- [x] CLI read-only inspection and opt-in execution
- [x] Python HTTP bridge with token auth
- [x] Cross-language CLI examples
- [ ] MCP/OpenAPI discovery adapters
- [ ] Signed manifests and explicit permission scopes
- [ ] Sandboxed execution via isolated processes / WASM
- [ ] Native Rust core with C ABI (.dll/.so/.dylib)
- [ ] npm/npx convenience CLI
- [ ] Auto-discovery and Forge integration

## Contributing

Issues and pull requests welcome. Please include a reproducible example and tests for behavior changes. See [LICENSE](LICENSE) (MIT).
