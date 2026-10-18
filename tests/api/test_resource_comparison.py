from copy import deepcopy

import pytest
from app.db_models import Execution
from tests.api.payloads import ARTIGO_V1_PAYLOAD


def setup_pair(client):
    pid = client.post('/api/v1/problems', json=deepcopy(ARTIGO_V1_PAYLOAD)).json()['id']
    ids, executions = [], []
    for name, overrides in [('Base', []), ('Forno +25%', [{'constraint_name': 'Capacidade do forno', 'rhs': 10}])]:
        response = client.post(f'/api/v1/problems/{pid}/scenarios', json={'name': name, 'constraint_overrides': overrides})
        assert response.status_code == 201
        sid = response.json()['id']
        result = client.post(f'/api/v1/scenarios/{sid}/solve')
        assert result.status_code == 200
        ids.append(sid)
        executions.append(result.json()['execution_id'])
    return pid, ids, executions


def request(client, pid, ids, **extra):
    return client.get(f'/api/v1/problems/{pid}/scenarios/compare/resources', params={
        'baseline_scenario_id': ids[0], 'target_scenario_id': ids[1], **extra})


def test_furnace_experiment(client):
    pid, ids, executions = setup_pair(client)
    response = request(client, pid, ids)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data['baseline']['execution_id'] == executions[0]
    assert data['target']['execution_id'] == executions[1]
    assert data['objective_delta'] == pytest.approx(-700)
    assert data['objective_improvement'] == pytest.approx(700)
    assert data['objective_delta_percent'] == pytest.approx(-700 / 13200 * 100)
    rows = {r['name']: r for r in data['resources'] if r['kind'] == 'constraint'}
    assert rows['Capacidade do forno']['rhs_delta'] == 2
    assert rows['Capacidade do forno']['lhs_delta'] == pytest.approx(2)
    assert rows['Capacidade do forno']['utilization_delta_pp'] == pytest.approx(0)
    assert rows['Horas']['slack_delta'] == pytest.approx(-3)
    assert rows['Demanda']['utilization_delta_pp'] is None
    assert request(client, pid, ids, baseline_execution_id=executions[0], target_execution_id=executions[1]).json() == data
    assert client.get(f'/api/v1/problems/{pid}/scenarios/compare').status_code == 200


def test_latest_failure_and_explicit_history(client, db_session):
    pid, ids, executions = setup_pair(client)
    newest = client.post(f'/api/v1/scenarios/{ids[1]}/solve').json()['execution_id']
    execution = db_session.get(Execution, newest)
    execution.created_at = db_session.get(Execution, executions[1]).created_at
    execution.status = 'infeasible'
    db_session.commit()
    assert request(client, pid, ids).status_code == 409
    assert request(client, pid, ids, target_execution_id=executions[1]).status_code == 200


def test_ownership_and_missing(client):
    pid, ids, executions = setup_pair(client)
    other_pid, other_ids, other_executions = setup_pair(client)
    assert request(client, 99999, ids).status_code == 404
    assert request(client, pid, [ids[0], other_ids[1]]).status_code == 404
    assert request(client, pid, ids, target_execution_id=other_executions[1]).status_code == 404
    assert request(client, pid, ids, target_execution_id=executions[0]).status_code == 404
    sid = client.post(f'/api/v1/problems/{pid}/scenarios', json={'name': 'Unsolved'}).json()['id']
    assert request(client, pid, [ids[0], sid]).status_code == 409
    assert request(client, pid, [0, ids[1]]).status_code == 422


@pytest.mark.parametrize('change', ['objective', 'operator', 'missing', 'duplicate', 'legacy'])
def test_changed_models(client, db_session, change):
    pid, ids, executions = setup_pair(client)
    execution = db_session.get(Execution, executions[1])
    snapshot = deepcopy(execution.analysis_snapshot)
    if change == 'objective':
        snapshot['model']['variables'][0]['objective_coefficient'] = 999
    elif change == 'operator':
        snapshot['model']['constraints'][-1]['operator'] = '='
    elif change == 'missing':
        snapshot['model']['constraints'].pop()
    elif change == 'duplicate':
        snapshot['model']['constraints'].append(deepcopy(snapshot['model']['constraints'][0]))
    execution.analysis_snapshot = None if change == 'legacy' else snapshot
    db_session.commit()
    response = request(client, pid, ids)
    if change in ('duplicate', 'legacy'):
        assert response.status_code == 409
    else:
        assert response.status_code == 200, response.text
        data = response.json()
        if change == 'objective':
            assert not data['objective_comparable']
            assert data['objective_improvement'] is None
        else:
            row = next(r for r in data['resources'] if r['name'] == 'Capacidade do forno')
            assert not row['comparable'] and row['slack_delta'] is None


@pytest.mark.parametrize('sense,base,target,improvement,percent', [
    ('min', 0, -1, 1, None), ('max', 10, 12, 2, 20), ('min', -10, -12, 2, -20)])
def test_objective_signs(client, db_session, sense, base, target, improvement, percent):
    pid, ids, executions = setup_pair(client)
    for eid, value in zip(executions, [base, target]):
        execution = db_session.get(Execution, eid)
        snapshot = deepcopy(execution.analysis_snapshot)
        snapshot['model']['objective_type'] = sense
        execution.analysis_snapshot = snapshot
        execution.objective_value = value
    db_session.commit()
    data = request(client, pid, ids).json()
    assert data['objective_improvement'] == improvement
    assert data['objective_delta_percent'] == percent
