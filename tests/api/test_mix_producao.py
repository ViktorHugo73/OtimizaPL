import pytest
from models.mix_producao import carregar_payload_mix


def test_mix_full_workflow(client):
    response = client.post('/api/v1/problems', json=carregar_payload_mix())
    assert response.status_code == 201
    pid = response.json()['id']
    direct = client.post(f'/api/v1/problems/{pid}/solve').json()
    assert direct['status'] == 'optimal'
    assert direct['objective_value'] == pytest.approx(36)
    base = client.post(f'/api/v1/problems/{pid}/scenarios', json={'name': 'Mix base'}).json()
    base_result = client.post(f'/api/v1/scenarios/{base["id"]}/solve').json()
    assert {v['variable_name']: v['value'] for v in base_result['variables']} == pytest.approx({'A': 2, 'B': 6, 'C': 0})
    analysis_url = f'/api/v1/executions/{base_result["execution_id"]}/resources'
    analysis = client.get(analysis_url).json()
    rows = {r['name']: r for r in analysis['resources'] if r['kind'] == 'constraint'}
    for name, lhs, rhs, slack, usage, active in [
        ('Corte', 2, 4, 2, 50, False), ('Usinagem', 12, 12, 0, 100, True),
        ('Montagem', 18, 18, 0, 100, True),
    ]:
        row = rows[name]
        assert [row['lhs'], row['rhs'], row['slack'], row['utilization_percent']] == pytest.approx([lhs, rhs, slack, usage])
        assert row['is_active'] == active and row['potential_bottleneck'] == active
    for name, rhs, expected, improvement in [('Montagem', 24, 42, 6), ('Usinagem', 15, 40.5, 4.5)]:
        created = client.post(f'/api/v1/problems/{pid}/scenarios', json={
            'name': f'{name} ampliada', 'constraint_overrides': [{'constraint_name': name, 'rhs': rhs}]})
        assert created.status_code == 201
        sid = created.json()['id']
        solved = client.post(f'/api/v1/scenarios/{sid}/solve').json()
        assert solved['objective_value'] == pytest.approx(expected)
        compared = client.get(f'/api/v1/problems/{pid}/scenarios/compare/resources', params={
            'baseline_scenario_id': base['id'], 'target_scenario_id': sid,
            'baseline_execution_id': base_result['execution_id'], 'target_execution_id': solved['execution_id']})
        assert compared.status_code == 200
        assert compared.json()['objective_improvement'] == pytest.approx(improvement)
    history = client.get(f'/api/v1/problems/{pid}/executions').json()
    assert len(history) == 4
    assert len(client.get(f'/api/v1/problems/{pid}/scenarios/compare').json()['scenarios']) == 3
    assert client.get(analysis_url).json() == analysis
    problem = client.get(f'/api/v1/problems/{pid}').json()
    assert [r['rhs'] for r in problem['constraints']] == [4, 12, 18]
