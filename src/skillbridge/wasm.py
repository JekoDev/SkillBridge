"""Optional WASI execution with explicit filesystem isolation (Wasmtime CLI)."""
import json
import shutil
import subprocess
from pathlib import Path
from .core import SkillBridgeError

def run_wasi(module, *, timeout=10, fuel=None):
    """Run a WASI module with no preopened host directories; no host functions supplied.

    Requires the external wasmtime CLI. Not a guarantee against runtime vulnerabilities.
    """
    exe = shutil.which('wasmtime')
    if not exe:
        raise SkillBridgeError('wasmtime CLI is required for WASI execution')
    path = Path(module).expanduser().resolve(strict=True)
    if not path.is_file() or path.suffix != '.wasm':
        raise SkillBridgeError('Expected a .wasm file')
    try:
        result = subprocess.run([exe, 'run', str(path)], input='', capture_output=True, text=True, timeout=min(max(timeout, 1), 30), check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise SkillBridgeError(str(exc)) from exc
    return {'exit_code':result.returncode,'stdout':result.stdout[:65536],'stderr':result.stderr[:65536]}
