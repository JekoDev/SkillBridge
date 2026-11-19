# SkillBridge native core (experimental)

Build with Rust stable:

```bash
cd native
cargo test
cargo build --release
```

Outputs: `skillbridge_native.dll` (Windows), `libskillbridge_native.so` (Linux), or `libskillbridge_native.dylib` (macOS). Public ABI: `include/skillbridge.h`.

The native core is an **in-process capability registry**, not an automatic MCP discovery server, sandbox, or agent runtime. It stores callback pointers, lists names as JSON, and invokes callbacks with JSON strings. JSON payloads are passed through, **not validated**. Embedder controls authorization and validation. `sb_call` returns NULL on errors or unknown names.

Memory rules: results from `sb_call` and `sb_list` must be freed with `sb_string_free`; callbacks must return a string allocated via `sb_string_new`. Keep callbacks and contexts alive until no calls can be running. Do not destroy a registry while other threads are using it. Never allow exceptions or panics to unwind across FFI boundaries. Untrusted plugins should execute out-of-process with explicit permissions.

See `examples/native` for Python ctypes, C++, Go/cgo, Rust and Node/Koffi examples. No compiled binaries are shipped in the source archive; build for your OS and CPU.
