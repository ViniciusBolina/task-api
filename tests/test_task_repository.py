"""Testes do TaskRepository usando um banco SQLite em memória."""

import uuid
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.database import Base
from app.models.schemas import TaskCreate, TaskUpdate
from app.repositories.task_repository import TaskRepository

@pytest.fixture
def repo():
    """Cria um banco limpo em memória para cada teste."""
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield TaskRepository(session)
    engine.dispose()

def test_create_generates_id_and_defaults(repo):
    task = repo.create(TaskCreate(title="Estudar pytest"))
    assert isinstance(task.id, uuid.UUID)
    assert task.title == "Estudar pytest"
    assert task.description is None
    assert task.status is False
    assert task.created_at is not None


def test_get_returns_task_when_it_exists(repo):
    created = repo.create(TaskCreate(title="Estudar pytest"))
    found = repo.get(created.id)
    assert found is not None
    assert found.id == created.id

def test_get_returns_none_for_unknown_id(repo):
    assert repo.get(uuid.uuid4()) is None

def test_list_returns_all_tasks(repo):
    repo.create(TaskCreate(title="Tarefa um"))
    repo.create(TaskCreate(title="Tarefa dois"))
    assert len(repo.list()) == 2

def test_list_filters_by_status(repo):
    repo.create(TaskCreate(title="Pendente", status=False))
    repo.create(TaskCreate(title="Concluída", status=True))
    done = repo.list(status=True)
    pending = repo.list(status=False)
    assert [t.title for t in done] == ["Concluída"]
    assert [t.title for t in pending] == ["Pendente"]

def test_update_changes_only_given_fields(repo):
    task = repo.create(TaskCreate(title="Título antigo", description="Detalhe"))
    updated = repo.update(task, TaskUpdate(status=True))
    assert updated.status is True
    assert updated.title == "Título antigo"
    assert updated.description == "Detalhe"

def test_delete_removes_task(repo):
    task = repo.create(TaskCreate(title="Apagar depois"))
    repo.delete(task)
    assert repo.get(task.id) is None
    assert repo.list() == []