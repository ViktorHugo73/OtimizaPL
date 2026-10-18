from copy import deepcopy
import pytest
from sqlalchemy import select
from app.db_models import Scenario, Execution, Variable, Constraint, ConstraintCoefficient, ResultVariable
from tests.api.payloads import ARTIGO_V1_PAYLOAD


def setup(client):
    pid = client.post('/api/v1/problems', json=deepcopy(ARTIGO_V1_PAYLOAD)).json()['id']
    scenario = client.post(f'/api/v1/problems/{pid}/scenarios', json={'name': 'Base'}).json()
    return pid, scenario


def test_listing_and_metadata_preserve_math(client):
    pid, scenario = setup(client)
    before = client.get(f'/api/v1/problems/{pid}').json()
    assert client.get('/api/v1/problems').json()[0]['id'] == pid
    assert client.patch(f'/api/v1/problems/{pid}', json={'name': ' Novo ', 'description': None}).status_code == 200
    after = client.get(f'/api/v1/problems/{pid}').json()
    assert after['name'] == 'Novo'
    assert after['variables'] == before['variables'] and after['constraints'] == before['constraints']
    sid = scenario['id']
    eid = client.post(f'/api/v1/scenarios/{sid}/solve').json()['execution_id']
    resources = client.get(f'/api/v1/executions/{eid}/resources').json()
    response = client.patch(f'/api/v1/scenarios/{sid}', json={'description': 'Revisado'})
    assert response.status_code == 200
    assert response.json()['model_snapshot'] == scenario['model_snapshot']
    assert client.get(f'/api/v1/executions/{eid}/resources').json() == resources


@pytest.mark.parametrize('payload', [{'name': '  '}, {'name': None}, {'model_snapshot': {}}, {'objective_type': 'max'}])
def test_protected_payloads(client, payload):
    pid, scenario = setup(client)
    for path in [f'problems/{pid}', f'scenarios/{scenario["id"]}']:
        assert client.patch(f'/api/v1/{path}', json=payload).status_code == 422


def test_duplicate_has_no_executions_and_independent_snapshot(client, db_session):
    pid, source = setup(client)
    client.post(f'/api/v1/scenarios/{source["id"]}/solve')
    response = client.post(f'/api/v1/scenarios/{source["id"]}/duplicate', json={'name': 'Cópia'})
    assert response.status_code == 201
    copy = response.json()
    assert copy['id'] != source['id'] and copy['model_snapshot'] == source['model_snapshot']
    assert client.get(f'/api/v1/scenarios/{copy["id"]}/resources').status_code == 409
    db_copy = db_session.get(Scenario, copy['id'])
    modified = deepcopy(db_copy.model_snapshot)
    modified['constraints'][0]['rhs'] = 999
    db_copy.model_snapshot = modified
    db_session.commit()
    assert db_session.get(Scenario, source['id']).model_snapshot == source['model_snapshot']


def test_deletion_confirmation_and_cascade(client, db_session):
    pid, scenario = setup(client)
    assert client.delete(f'/api/v1/problems/{pid}').status_code == 400
    assert client.delete(f'/api/v1/scenarios/{scenario["id"]}').status_code == 400
    assert client.delete(f'/api/v1/problems/{pid}?confirm=true').status_code == 204
    assert client.get(f'/api/v1/problems/{pid}').status_code == 404
    for model in [Scenario, Variable, Constraint, ConstraintCoefficient, Execution]:
        assert list(db_session.scalars(select(model))) == []


def test_delete_executed_scenario_preserves_other_executions(client, db_session):
    pid, scenario = setup(client)
    sid = scenario['id']
    eid = client.post(f'/api/v1/scenarios/{sid}/solve').json()['execution_id']
    base = client.post(f'/api/v1/problems/{pid}/solve').json()['execution_id']
    other = client.post(f'/api/v1/problems/{pid}/scenarios', json={'name': 'Outro'}).json()['id']
    kept = client.post(f'/api/v1/scenarios/{other}/solve').json()['execution_id']
    assert client.delete(f'/api/v1/scenarios/{sid}').status_code == 400
    assert client.delete(f'/api/v1/scenarios/{sid}?confirm=true').status_code == 204
    assert client.get(f'/api/v1/executions/{eid}/resources').status_code == 404
    assert list(db_session.scalars(select(ResultVariable).where(ResultVariable.execution_id == eid))) == []
    for identifier in [base, kept]:
        assert client.get(f'/api/v1/executions/{identifier}/resources').status_code == 200
    assert client.get(f'/api/v1/problems/{pid}').status_code == 200


def test_delete_executed_problem_removes_all_dependents(client, db_session):
    pid, scenario = setup(client)
    eid = client.post(f'/api/v1/scenarios/{scenario["id"]}/solve').json()['execution_id']
    client.post(f'/api/v1/problems/{pid}/solve')
    assert client.delete(f'/api/v1/problems/{pid}?confirm=false').status_code == 400
    assert client.get(f'/api/v1/executions/{eid}/resources').status_code == 200
    assert client.delete(f'/api/v1/problems/{pid}?confirm=true').status_code == 204
    assert client.get(f'/api/v1/problems/{pid}').status_code == 404
    for model in [Scenario, Execution, ResultVariable, Variable, Constraint, ConstraintCoefficient]:
        assert list(db_session.scalars(select(model))) == []


def test_delete_empty_scenario_and_missing_records(client):
    pid, scenario = setup(client)
    assert client.delete(f'/api/v1/scenarios/{scenario["id"]}?confirm=true').status_code == 204
    assert client.get(f'/api/v1/problems/{pid}').status_code == 200
    for kind in ['problems', 'scenarios']:
        assert client.patch(f'/api/v1/{kind}/999', json={'name': 'Novo'}).status_code == 404
        assert client.delete(f'/api/v1/{kind}/999?confirm=true').status_code == 404
    assert client.post('/api/v1/scenarios/999/duplicate', json={'name': 'Cópia'}).status_code == 404
