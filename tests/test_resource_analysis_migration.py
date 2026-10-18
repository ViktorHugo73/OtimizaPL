import importlib.util
from pathlib import Path

from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import create_engine, inspect, text


def test_upgrade_preserves_legacy_execution_and_downgrade():
    path = Path(__file__).resolve().parents[1] / 'alembic/versions/e71c9a04b632_execution_analysis_snapshot.py'
    spec = importlib.util.spec_from_file_location('analysis_migration', path)
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    engine = create_engine('sqlite://')
    with engine.begin() as connection:
        connection.execute(text('CREATE TABLE executions (id INTEGER PRIMARY KEY)'))
        connection.execute(text('INSERT INTO executions (id) VALUES (1)'))
        migration.op = Operations(MigrationContext.configure(connection))
        migration.upgrade()
        assert connection.execute(text('SELECT id, analysis_snapshot FROM executions')).one() == (1, None)
        migration.downgrade()
        assert [c['name'] for c in inspect(connection).get_columns('executions')] == ['id']
        assert connection.execute(text('SELECT id FROM executions')).scalar_one() == 1
    engine.dispose()
