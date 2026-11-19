"""Run after cargo build --release in native/."""
import ctypes
import json
import os
from pathlib import Path

root = Path(__file__).resolve().parents[2] / "native" / "target" / "release"
filename = "skillbridge_native.dll" if os.name == "nt" else ("libskillbridge_native.dylib" if __import__("sys").platform == "darwin" else "libskillbridge_native.so")
lib = ctypes.CDLL(str(root / filename))
lib.sb_create.restype = ctypes.c_void_p
lib.sb_destroy.argtypes = [ctypes.c_void_p]
lib.sb_string_new.argtypes = [ctypes.c_char_p]
lib.sb_string_new.restype = ctypes.c_void_p
lib.sb_string_free.argtypes = [ctypes.c_void_p]
CALLBACK = ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_char_p, ctypes.c_void_p)
lib.sb_register.argtypes = [ctypes.c_void_p, ctypes.c_char_p, CALLBACK, ctypes.c_void_p]
lib.sb_call.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p]
lib.sb_call.restype = ctypes.c_void_p
lib.sb_list.argtypes = [ctypes.c_void_p]
lib.sb_list.restype = ctypes.c_void_p

def read_and_free(pointer):
    if not pointer:
        raise RuntimeError("Native call failed")
    try:
        return ctypes.string_at(pointer).decode("utf-8")
    finally:
        lib.sb_string_free(pointer)

@CALLBACK
def echo(payload, context):
    return lib.sb_string_new(payload)

handle = lib.sb_create()
try:
    assert lib.sb_register(handle, b"echo", echo, None) == 0
    print(json.loads(read_and_free(lib.sb_list(handle))))
    print(read_and_free(lib.sb_call(handle, b"echo", b'{"hello":"Forge"}')))
finally:
    lib.sb_destroy(handle)
