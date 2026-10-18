from types import SimpleNamespace
import pytest
from experiments.experimentos_finais import evaluate, generate_cases, measure
from experiments.gerador import ProblemaGerado, gerar_inviavel, gerar_ilimitado


def test_design_and_actual_sizes():
    cases = generate_cases()
    assert len(cases) == 152
    assert len({p.id for _, p in cases}) == 152
    assert all(len(p.b) == p.n_restricoes for _, p in cases)
    assert {len(p.b) for g, p in cases if g == 'escala'} == {15, 30, 60, 150, 300}


def test_zero_reference_has_no_conventional_relative_error():
    p = ProblemaGerado('ZERO', 'factivel_limitado', [[1]], [1], [0], ['<='], 'min', 0, 1, 1)
    result, samples = measure(p, 2)
    assert result['aprovado'] and len(samples) == 2
    assert result['erro_relativo'] is None
    assert result['erro_normalizado'] == 0
    assert samples[0]['ordem'] != samples[1]['ordem']


@pytest.mark.parametrize('generator,status', [(gerar_inviavel, 'infeasible'), (gerar_ilimitado, 'unbounded')])
def test_nonoptimal_classification_and_absent_errors(generator, status):
    result, _ = measure(generator('X', 3, 123), 1)
    assert result['aprovado'] and result['status_proprio'] == status
    assert result['erro_relativo'] is None and result['objetivo_proprio'] is None


def test_matching_errors_never_pass():
    problem = gerar_inviavel('X', 3, 123)
    error = SimpleNamespace(status='numerical_error')
    assert not evaluate(problem, error, error)['aprovado']


@pytest.mark.parametrize('own_x,own_z', [([2.0], 1.0), ([1.0], 1.01), ([float('nan')], 1.0)])
def test_optimal_label_does_not_hide_invalid_solution(own_x, own_z):
    problem = ProblemaGerado('X', 'factivel_limitado', [[1]], [1], [1], ['<='], 'max', 0, 1, 1)
    own = SimpleNamespace(status='optimal', x=own_x, valor_objetivo=own_z)
    reference = SimpleNamespace(status='optimal', x=[1.0], valor_objetivo=1.0)
    assert not evaluate(problem, own, reference)['aprovado']
