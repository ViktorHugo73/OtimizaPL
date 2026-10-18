from copy import deepcopy
import pytest
from app.db_models import Problem, Execution


def payload(operator='<=', rhs=10, objective='max'):
    return dict(name='Oficina', objective_type=objective,
        variables=[dict(name='Reformas', objective_coefficient=2, lower_bound=0)],
        constraints=[dict(name='Horas', operator=operator, rhs=rhs,
                          terms=[dict(variable_name='Reformas', coefficient=1)])])


def run(client, data):
    p = client.post('/api/v1/problems', json=data).json()
    e = client.post(f"/api/v1/problems/{p['id']}/solve").json()
    return p['id'], e['execution_id']


def test_history_and_clone_use_original_snapshot(client, db_session):
    pid, eid = run(client, payload())
    before = client.get(f'/api/v1/executions/{eid}/resources').json()
    snapshot = deepcopy(db_session.get(Execution, eid).analysis_snapshot['model'])
    p = db_session.get(Problem, pid)
    p.objective_type = 'min'
    p.variables[0].name = 'Nome alterado'
    p.variables[0].objective_coefficient = 100
    p.constraints[0].rhs = 1000
    db_session.commit()
    history = client.get(f'/api/v1/problems/{pid}/executions').json()
    assert len(history) == 1
    assert history[0]['objective_type'] == 'max'
    assert history[0]['recorded_variables'] == [dict(name='Reformas', value=10)]
    assert history[0]['objective_value'] == 20
    assert client.get(f'/api/v1/executions/{eid}/resources').json() == before
    clone = client.post(f'/api/v1/problems/{pid}/scenarios', json=dict(name='Cópia histórica', source_execution_id=eid))
    assert clone.status_code == 201
    assert clone.json()['model_snapshot'] == snapshot
    assert len(client.get(f'/api/v1/problems/{pid}/executions').json()) == 1


@pytest.mark.parametrize('operator,rhs,objective,status', [('<=',10,'max','optimal'),('>=',10,'min','optimal'),('=',10,'min','optimal'),('<=',-1,'max','infeasible'),('>=',1,'max','unbounded')])
def test_context_all_statuses_and_relations(client, operator, rhs, objective, status):
    pid, eid = run(client, payload(operator, rhs, objective))
    item = client.get(f'/api/v1/problems/{pid}/executions').json()[0]
    assert item['status'] == status
    assert item['objective_type'] == objective
    assert item['snapshot_available'] is True
    assert (item['recorded_variables'] is not None) == (status == 'optimal')
    result = client.get(f'/api/v1/executions/{eid}/resources')
    if status == 'optimal':
        assert result.status_code == 200
        row = result.json()['resources'][0]
        assert row['operator'] == operator
        assert (row['utilization_percent'] is not None) == (operator == '<=')
    else:
        assert result.status_code == 409


def test_absent_snapshot_is_not_reconstructed(client, db_session):
    pid, eid = run(client, payload())
    e = db_session.get(Execution, eid); e.analysis_snapshot = None; db_session.commit()
    item = client.get(f'/api/v1/problems/{pid}/executions').json()[0]
    assert item['snapshot_available'] is False
    assert item['objective_type'] is None
    assert item['recorded_variables'] is None
    assert client.post(f'/api/v1/problems/{pid}/scenarios', json=dict(name='Sem snapshot', source_execution_id=eid)).status_code == 422


def test_cannot_copy_execution_from_other_problem(client):
    pid, eid = run(client, payload())
    other = client.post('/api/v1/problems', json=payload()).json()['id']
    assert other != pid
    assert client.post(f'/api/v1/problems/{other}/scenarios', json=dict(name='Inválido', source_execution_id=eid)).status_code == 404
