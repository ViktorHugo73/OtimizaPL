import pytest

from fastapi.testclient import (
    TestClient
)

from sqlalchemy import create_engine

from sqlalchemy.orm import sessionmaker

from sqlalchemy.pool import StaticPool


from app.database.base import Base

from app.database.session import get_db

from app.main import app


# ============================================================
# BANCO SQLITE SOMENTE PARA TESTES
# ============================================================

TEST_DATABASE_URL = (
    "sqlite+pysqlite:///:memory:"
)


engine_test = create_engine(

    TEST_DATABASE_URL,

    connect_args={
        "check_same_thread":
            False
    },

    poolclass=StaticPool,
)


TestingSessionLocal = sessionmaker(

    bind=engine_test,

    autocommit=False,

    autoflush=False,

    expire_on_commit=False,
)


# ============================================================
# OVERRIDE DO BANCO DA API
# ============================================================

def override_get_db():

    db = TestingSessionLocal()

    try:
        yield db

    finally:
        db.close()


app.dependency_overrides[
    get_db
] = override_get_db


# ============================================================
# FIXTURE DO BANCO
# ============================================================

@pytest.fixture(
    autouse=True
)
def reset_database():

    Base.metadata.drop_all(
        bind=engine_test
    )

    Base.metadata.create_all(
        bind=engine_test
    )

    yield

    Base.metadata.drop_all(
        bind=engine_test
    )


# ============================================================
# CLIENT HTTP
# ============================================================

@pytest.fixture
def client():

    with TestClient(
        app
    ) as test_client:

        yield test_client

@pytest.fixture
def db_session():
    with TestingSessionLocal() as db:
        yield db
