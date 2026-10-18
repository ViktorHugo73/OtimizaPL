import json
import pytest
from pathlib import Path


def test_example_feixe_molas_payload_and_optimum(client):
    data=json.loads((Path(__file__).resolve().parents[2]/'examples/feixe_molas_custo.json').read_text(encoding='utf-8'))
    assert data['objective_type']=='min'
    assert [(v['name'],v['objective_coefficient']) for v in data['variables']]==[('XR',450),('XS',800)]
    assert [c['rhs'] for c in data['constraints']]==[20,80,40,25,0,8]
    assert [c['operator'] for c in data['constraints']]==['>=','<=','<=','<=','>=','<=']
    assert [[t['coefficient'] for t in c['terms']] for c in data['constraints']]==[[1,1],[3,1.5],[2,1],[0,1],[7,-3],[1,0]]
    created=client.post('/api/v1/problems',json=data)
    assert created.status_code==201
    result=client.post(f"/api/v1/problems/{created.json()['id']}/solve")
    assert result.status_code==200
    assert result.json()['status']=='optimal'
    assert result.json()['objective_value']==pytest.approx(13200)
    values={v['variable_name']:v['value'] for v in result.json()['variables']}
    assert values==pytest.approx({'XR':8,'XS':12})
    resources=client.get(f"/api/v1/executions/{result.json()['execution_id']}/resources").json()
    assert resources['is_feasible'] is True
    active={row['name'] for row in resources['resources'] if row['kind']=='constraint' and row['is_active']}
    assert active=={'Demanda mínima','Capacidade do forno'}
