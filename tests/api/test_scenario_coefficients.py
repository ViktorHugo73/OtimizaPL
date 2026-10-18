from copy import deepcopy
import pytest
from tests.api.payloads import ARTIGO_V1_PAYLOAD


def test_coefficient_override_preserves_base_and_previous_execution(client):
    pid = client.post('/api/v1/problems', json=deepcopy(ARTIGO_V1_PAYLOAD)).json()['id']
    original = client.post(f'/api/v1/problems/{pid}/scenarios', json={'name': 'Original'}).json()
    eid = client.post(f'/api/v1/scenarios/{original["id"]}/solve').json()['execution_id']
    analysis = client.get(f'/api/v1/executions/{eid}/resources').json()
    changed = client.post(f'/api/v1/problems/{pid}/scenarios', json={
        'name': 'Coeficientes alterados', 'constraint_overrides': [
            {'constraint_name': 'Capacidade do forno', 'coefficients': {'XR': 0.5, 'XS': 0}},
            {'constraint_name': 'Percentual mínimo de reformas', 'coefficients': {'XR': 0.7, 'XS': -0.2}},
        ]})
    assert changed.status_code == 201
    scenario = changed.json()
    furnace = next(c for c in scenario['model_snapshot']['constraints'] if c['name'] == 'Capacidade do forno')
    assert furnace['coefficients'] == {'XR': 0.5, 'XS': 0}
    result = client.post(f'/api/v1/scenarios/{scenario["id"]}/solve').json()
    assert result['status'] == 'optimal'
    assert result['objective_value'] == pytest.approx(10400)
    current = client.get(f'/api/v1/executions/{result["execution_id"]}/resources').json()
    row = next(r for r in current['resources'] if r['name'] == 'Capacidade do forno')
    assert row['lhs'] == pytest.approx(8)
    assert row['slack'] == pytest.approx(0)
    assert client.get(f'/api/v1/executions/{eid}/resources').json() == analysis
    assert client.get(f'/api/v1/scenarios/{original["id"]}').json()['model_snapshot'] == original['model_snapshot']
    base = client.get(f'/api/v1/problems/{pid}').json()
    assert next(c for c in base['constraints'] if c['name'] == 'Capacidade do forno')['terms'][0]['coefficient'] == 1


def test_unknown_coefficient_variable_rejected(client):
    pid = client.post('/api/v1/problems', json=deepcopy(ARTIGO_V1_PAYLOAD)).json()['id']
    response = client.post(f'/api/v1/problems/{pid}/scenarios', json={
        'name': 'Inválido', 'constraint_overrides': [
            {'constraint_name': 'Horas', 'coefficients': {'inexistente': 2}}]})
    assert response.status_code == 422
