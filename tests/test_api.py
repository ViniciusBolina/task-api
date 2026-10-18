"""Testes dos endpoints da API usando um banco SQLite em memória."""

import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.database import Base, get_db
from app.main import app

@pytest.fixture
def client():
    """Cliente de teste ligado a um banco em memória, limpo a cada teste."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    testing_session = sessionmaker(bind=engine, autoflush=False)

    def override_get_db():
        db = testing_session()
        try:
            yield db
        finally:
            db.close()
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
    engine.dispose()

def create(client, title="Estudar FastAPI", **extra):
    """Cria uma tarefa pela API e devolve a resposta."""
    return client.post("/tasks", json={"title": title, **extra})

def test_create_task_returns_201(client):
    response = create(client, description="Ler a documentação")
    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Estudar FastAPI"
    assert body["description"] == "Ler a documentação"
    assert body["status"] is False
    assert "id" in body
    assert "created_at" in body

def test_create_task_with_short_title_returns_422(client):
    response = create(client, title="ab")
    assert response.status_code == 422

def test_list_tasks_returns_created_tasks(client):
    create(client, title="Tarefa um")
    create(client, title="Tarefa dois")
    response = client.get("/tasks")
    assert response.status_code == 200
    assert len(response.json()) == 2

def test_list_tasks_filters_by_status(client):
    create(client, title="Pendente", status=False)
    create(client, title="Concluída", status=True)
    done = client.get("/tasks", params={"status": True}).json()
    pending = client.get("/tasks", params={"status": False}).json()
    assert [t["title"] for t in done] == ["Concluída"]
    assert [t["title"] for t in pending] == ["Pendente"]

def test_get_task_returns_task(client):
    task_id = create(client).json()["id"]
    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 200
    assert response.json()["id"] == task_id

def test_get_unknown_task_returns_404(client):
    response = client.get(f"/tasks/{uuid.uuid4()}")
    assert response.status_code == 404

def test_get_with_invalid_id_returns_422(client):
    response = client.get("/tasks/nao-e-um-uuid")
    assert response.status_code == 422

def test_update_task_changes_only_given_fields(client):
    task_id = create(client, title="Título antigo", description="Detalhe").json()["id"]
    response = client.put(f"/tasks/{task_id}", json={"status": True})
    assert response.status_code == 200
    body = response.json()
    assert body["status"] is True
    assert body["title"] == "Título antigo"
    assert body["description"] == "Detalhe"

def test_update_unknown_task_returns_404(client):
    response = client.put(f"/tasks/{uuid.uuid4()}", json={"status": True})
    assert response.status_code == 404

def test_delete_task_returns_204_and_removes_it(client):
    task_id = create(client).json()["id"]
    response = client.delete(f"/tasks/{task_id}")
    assert response.status_code == 204
    assert client.get(f"/tasks/{task_id}").status_code == 404
