"""Initialize only the dedicated Neon demo database. Never reads the local .env."""
import getpass
import os
from pathlib import Path
import sys

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import make_url
from sqlalchemy.pool import NullPool


def demo_url(raw):
    url = make_url(raw.strip())
    if url.drivername not in ('postgres', 'postgresql', 'postgresql+psycopg'):
        raise ValueError('Use uma conexão PostgreSQL.')
    if url.database != 'otimizapl_demo':
        raise ValueError('O banco deve se chamar otimizapl_demo.')
    if not url.host or not url.host.endswith('.neon.tech'):
        raise ValueError('Use o host fornecido pelo Neon.')
    if '-pooler.' in url.host:
        raise ValueError('Para preparar as tabelas, use a conexão direta, sem pooler.')
    if url.query.get('sslmode') not in ('require', 'verify-ca', 'verify-full'):
        raise ValueError('A conexão deve exigir SSL.')
    return url.set(drivername='postgresql+psycopg')


def main():
    root = Path(__file__).resolve().parents[1]
    os.chdir(root)
    sys.path.insert(0, str(root))
    try:
        url = demo_url(getpass.getpass('Cole a conexão direta do banco otimizapl_demo (entrada oculta): '))
    except Exception:
        print('Conexão inválida. Use PostgreSQL Neon, banco otimizapl_demo, conexão direta e sslmode=require. A URL não foi exibida nem salva.')
        return 1
    engine = create_engine(url, poolclass=NullPool, connect_args={'connect_timeout': 15})
    try:
        with engine.connect() as connection:
            if connection.scalar(text('select current_database()')) != 'otimizapl_demo':
                raise ValueError()
            # Bootstrap only: refuse an existing database to avoid accidental changes.
            if inspect(connection).get_table_names():
                print('Este banco já possui tabelas. Nenhuma migração foi aplicada. Confira o banco antes de continuar.')
                return 1
        os.environ['DATABASE_URL'] = url.render_as_string(hide_password=False)
        from alembic import command
        from alembic.config import Config
        from app.core.config import get_settings
        get_settings.cache_clear()
        command.upgrade(Config(str(root / 'alembic.ini')), 'head')
        with engine.connect() as connection:
            tables = set(inspect(connection).get_table_names())
            expected = {'problems', 'variables', 'constraints', 'constraint_coefficients', 'scenarios', 'executions', 'result_variables', 'alembic_version'}
            if not expected.issubset(tables):
                raise ValueError()
        print('Banco de demonstração preparado e tabelas verificadas. Nenhum dado da oficina foi copiado.')
        return 0
    except Exception:
        print('Não foi possível concluir a preparação. Confira disponibilidade, permissões e conexão no Neon. Credenciais e detalhes de conexão foram omitidos.')
        return 1
    finally:
        engine.dispose()
        os.environ.pop('DATABASE_URL', None)


if __name__ == '__main__':
    raise SystemExit(main())
