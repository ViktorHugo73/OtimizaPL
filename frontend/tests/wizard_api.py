"""API real com banco SQLite isolado para conferência do formulário. Nunca usa o banco configurado."""
import os
from pathlib import Path
import sys
import uvicorn
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

project = Path(os.environ.get('TCC_PROJECT', Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(project))
from app.main import app
from app.database.base import Base
from app.database.session import get_db

path = Path(os.environ['WIZARD_TEST_DB']).resolve()
engine = create_engine(f'sqlite:///{path.as_posix()}', connect_args={'check_same_thread': False})
Base.metadata.create_all(engine)
sessions = sessionmaker(bind=engine, expire_on_commit=False)
def isolated_db():
    with sessions() as session:
        yield session
app.dependency_overrides[get_db] = isolated_db
if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8011)
