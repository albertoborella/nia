import os

os.environ["NIA_TESTING"] = "1"

import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from sqlmodel.pool import StaticPool

from app.database import get_db
from app.models.usuario import Usuario
from app.services.auth_service import hash_password, create_access_token


@pytest.fixture(name="engine")
def fixture_engine():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="db_session")
def fixture_db_session(engine):
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def fixture_client(engine):
    def override_get_db():
        with Session(engine) as session:
            yield session

    from app.main import app
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture(name="director_user")
def fixture_director_user(db_session):
    user = Usuario(
        nombre="Director Test",
        email="director@nia.com",
        password_hash=hash_password("Director123!"),
        rol="director",
        activo=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(name="colaborador_user")
def fixture_colaborador_user(db_session):
    user = Usuario(
        nombre="Colaborador Test",
        email="colab@nia.com",
        password_hash=hash_password("Colab123!"),
        rol="colaborador",
        activo=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(name="director_token")
def fixture_director_token(director_user):
    return create_access_token(str(director_user.id))


@pytest.fixture(name="colaborador_token")
def fixture_colaborador_token(colaborador_user):
    return create_access_token(str(colaborador_user.id))
