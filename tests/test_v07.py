import io
import json
from skillbridge.mcp import _read_messages
from skillbridge.system_discovery import system_roots
from skillbridge.wasm import run_wasi
from skillbridge.core import SkillBridgeError

def test_mcp_framed():
    data = json.dumps({'jsonrpc':'2.0','id':1,'method':'ping'}).encode()
    stream = io.BytesIO(b'Content-Length: '+str(len(data)).encode()+b'\r\n\r\n'+data)
    assert list(_read_messages(stream))[0]['method']=='ping'

def test_mcp_legacy():
    assert list(_read_messages(io.BytesIO(b'{"id":1}\n')))==[{'id':1}]

def test_system_roots():
    assert isinstance(system_roots(),list)

def test_wasm_missing():
    try: run_wasi('/not/a/module.wasm')
    except (SkillBridgeError, FileNotFoundError): pass
    else: assert False
