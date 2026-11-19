"""End-to-end MCP stdio tests against the real Python process."""
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'examples' / 'manifests'

def test_stdio_json_lines():
    env = os.environ.copy()
    env['PYTHONPATH'] = str(ROOT / 'src')
    messages = [
        {'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2025-06-18','capabilities':{},'clientInfo':{'name':'test','version':'1'}}},
        {'jsonrpc':'2.0','method':'notifications/initialized'},
        {'jsonrpc':'2.0','id':2,'method':'tools/list'},
        {'jsonrpc':'2.0','id':3,'method':'ping'},
    ]
    proc = subprocess.run([sys.executable,'-m','skillbridge.cli','mcp',str(MANIFEST)],
        input='\n'.join(json.dumps(x) for x in messages)+'\n',
        capture_output=True,text=True,env=env,timeout=10)
    assert proc.returncode == 0, proc.stderr
    replies = [json.loads(x) for x in proc.stdout.splitlines()]
    assert [x['id'] for x in replies] == [1,2,3]
    assert replies[0]['result']['capabilities']['tools'] is not None
    assert isinstance(replies[1]['result']['tools'], list)
    assert replies[2]['result'] == {}

def test_mcp_execution_denied_by_default():
    env=os.environ.copy(); env['PYTHONPATH']=str(ROOT/'src')
    message={'jsonrpc':'2.0','id':1,'method':'tools/call','params':{'name':'echo','arguments':{'message':'hello'}}}
    proc=subprocess.run([sys.executable,'-m','skillbridge.cli','mcp',str(MANIFEST)],
        input=json.dumps(message)+'\n',capture_output=True,text=True,env=env,timeout=10)
    assert proc.returncode == 0
    result=json.loads(proc.stdout.strip())
    assert 'error' in result or result.get('result',{}).get('isError') is True
