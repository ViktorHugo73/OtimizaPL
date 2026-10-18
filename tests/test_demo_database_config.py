import importlib.util
from pathlib import Path
import pytest

spec = importlib.util.spec_from_file_location('prepare_demo_database', Path(__file__).resolve().parents[1] / 'scripts/prepare_demo_database.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_demo_url_keeps_encoded_password_and_ssl():
    url = module.demo_url('postgresql://demo:p%40ss%25@ep-test.neon.tech/otimizapl_demo?sslmode=require')
    assert url.drivername == 'postgresql+psycopg'
    assert url.password == 'p@ss%'
    assert url.query['sslmode'] == 'require'


@pytest.mark.parametrize('url', [
    'postgresql://a:b@localhost/otimizapl_demo?sslmode=require',
    'postgresql://a:b@ep-test.neon.tech/oficina?sslmode=require',
    'postgresql://a:b@ep-test-pooler.neon.tech/otimizapl_demo?sslmode=require',
    'postgresql://a:b@ep-test.neon.tech/otimizapl_demo',
    'sqlite:///otimizapl_demo',
])
def test_demo_rejects_wrong_target(url):
    with pytest.raises(ValueError):
        module.demo_url(url)
