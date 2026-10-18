from copy import deepcopy

import pytest

from app.services.resource_analysis_service import analyze_resources


def snapshot(op='<=', rhs=10, coefficient=1):
    return {'variables': [{'name': 'x', 'lower_bound': 0, 'upper_bound': 20}],
            'constraints': [{'name': 'resource', 'operator': op, 'rhs': rhs,
                             'coefficients': {'x': coefficient}}]}


@pytest.mark.parametrize('op,rhs,x,slack,excess,active,feasible,percent', [
    ('<=', 10, 4, 6, None, False, True, 40),
    ('<=', 10, 10, 0, None, True, True, 100),
    ('<=', 10, 11, -1, None, False, False, 110),
    ('>=', 10, 12, None, 2, False, True, None),
    ('>=', 10, 9, None, -1, False, False, None),
    ('=', 10, 10, None, None, True, True, None),
    ('=', 10, 11, None, None, False, False, None),
    ('<=', 0, 0, 0, None, True, True, None),
    ('<=', -1, 0, -1, None, False, False, None),
])
def test_constraint_semantics(op, rhs, x, slack, excess, active, feasible, percent):
    row = analyze_resources(snapshot(op, rhs), {'x': x})[0]
    assert (row.lhs, row.rhs, row.slack, row.excess) == (x, rhs, slack, excess)
    assert (row.is_active, row.is_feasible) == (active, feasible)
    assert row.utilization_percent == (pytest.approx(percent) if percent is not None else None)
    assert row.potential_bottleneck == (percent == 100)


def test_tolerance_preserves_raw_values():
    row = analyze_resources(snapshot(), {'x': 10 + 1e-8})[0]
    assert row.is_active and row.is_feasible
    assert row.slack < 0  # No rounding inside decisions or stored results.
    assert not analyze_resources(snapshot(), {'x': 10 + 1e-4})[0].is_feasible


def test_negative_coefficients_no_utilization():
    assert analyze_resources(snapshot(coefficient=-1), {'x': 3})[0].utilization_percent is None


def test_variable_bounds_and_no_mutation():
    model = snapshot()
    original = deepcopy(model)
    rows = analyze_resources(model, {'x': 0})
    assert rows[1].kind == 'lower_bound' and rows[1].is_active
    assert rows[2].slack == 20
    assert model == original


@pytest.mark.parametrize('values', [{}, {'x': float('nan')}, {'x': float('inf')}, {'x': 1, 'y': 0}])
def test_invalid_solution_rejected(values):
    with pytest.raises(ValueError):
        analyze_resources(snapshot(), values)


def test_infeasible_bound_suppresses_bottleneck():
    model = snapshot()
    model['variables'][0]['upper_bound'] = 9
    rows = analyze_resources(model, {'x': 10})
    assert not any(row.potential_bottleneck for row in rows)


def test_sparse_coefficients():
    model = snapshot()
    model['variables'].append({'name': 'y'})
    assert analyze_resources(model, {'x': 4, 'y': 100})[0].lhs == 4
