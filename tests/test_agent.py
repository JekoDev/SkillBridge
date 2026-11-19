import json
import pytest
from skillbridge.agent import tools_for, run_turn, local_endpoint
from skillbridge.core import SkillBridgeError

MANIFEST = {'app':'Demo', '_manifest_path':'/tmp/skillbridge.json', 'skills':[{'name':'echo', 'type':'command', 'description':'Echo a value', 'inputs':{'text':'string'}, 'argv':['echo','{text}']}, {'name':'docs', 'type':'documentation', 'description':'Readme'}]}

def test_tool_discovery():
    tools = tools_for(MANIFEST)
    assert len(tools) == 1
    assert tools[0]['function']['name'] == 'echo'

def test_endpoint_validation():
    assert local_endpoint('http://localhost:1234/v1/') == 'http://localhost:1234/v1'
    with pytest.raises(SkillBridgeError):
        local_endpoint('https://example.org/v1')

def test_denied_tool_not_executed():
    replies = iter([{'role':'assistant', 'tool_calls':[{'id':'a','type':'function','function':{'name':'echo','arguments':'{"text":"hey"}'}}]}, {'role':'assistant','content':'Denied'}])
    messages = [{'role':'user','content':'Echo'}]
    result = run_turn(MANIFEST, messages, endpoint='http://localhost:1234/v1', model='test', approve=lambda *args:False, complete_fn=lambda *args, **kwargs:next(replies))
    assert result == 'Denied'
    assert 'User denied' in messages[-2]['content']

def test_unknown_tool_never_approved():
    replies = iter([{'role':'assistant', 'tool_calls':[{'id':'a','type':'function','function':{'name':'bad','arguments':'{}'}}]}, {'role':'assistant','content':'Done'}])
    messages = []
    def fail(*args):
        raise AssertionError('Should not request approval for unknown tool')
    run_turn(MANIFEST, messages, endpoint='http://localhost:1234/v1', model='test', approve=fail, complete_fn=lambda *args, **kwargs:next(replies))
    assert 'Unknown' in messages[-2]['content']
