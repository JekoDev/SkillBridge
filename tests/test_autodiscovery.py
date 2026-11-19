import json
import pytest
from skillbridge.autodiscovery import connect
from skillbridge.core import SkillBridgeError

def test_connect_by_name(tmp_path):
    app = tmp_path / 'TestApp'
    app.mkdir()
    (app / 'skillbridge.json').write_text(json.dumps({'app':'TestApp','skills':[{'name':'hello','description':'hello','type':'documentation'}]}))
    result = connect('testapp', [tmp_path])
    assert result['app'] == 'TestApp'
    assert result['skills'][0]['name'] == 'hello'
    assert result['execution'] == 'disabled-by-default'

def test_missing(tmp_path):
    with pytest.raises(SkillBridgeError, match='not found'):
        connect('unknown', [tmp_path])

def test_ambiguous(tmp_path):
    for root in ('one','two'):
        app = tmp_path / root / 'TestApp'
        app.mkdir(parents=True)
        (app / 'AGENT.md').write_text('# Agent docs')
    with pytest.raises(SkillBridgeError, match='Ambiguous'):
        connect('TestApp', [tmp_path / 'one', tmp_path / 'two'])

def test_no_command_execution(tmp_path):
    app = tmp_path / 'app'
    app.mkdir()
    (app / 'skillbridge.json').write_text(json.dumps({'app':'app','skills':[{'name':'danger','description':'test','type':'command','argv':['does-not-exist']}]}))
    assert connect(str(app))['skills'][0]['name'] == 'danger'
