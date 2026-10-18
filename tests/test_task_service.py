"""Testes do TaskService usando um repository falso, sem banco de dados."""

import uuid
from datetime import datetime, timezone
import pytest
from app.models.db_models import TaskDB
from app.models.schemas import TaskCreate, TaskUpdate
from app.repositories.interface import ITaskRepository
from app.services.task_service import TaskNotFoundError, TaskService


class FakeTaskRepository(ITaskRepository):
    """Repository em memória, usado apenas nos testes."""

    def __init__(self) -> None:
        self.tasks: dict[uuid.UUID, TaskDB] = {}

    def create(self, data: TaskCreate) -> TaskDB:
        task = TaskDB(
            id=uuid.uuid4(),
            created_at=datetime.now(timezone.utc),
            **data.model_dump(),
        )
        self.tasks[task.id] = task
        return task

    def list_all(self, status: bool | None = None) -> list[TaskDB]:
        tasks = list(self.tasks.values())
        if status is None:
            return tasks
        return [t for t in tasks if t.status == status]

    def get(self, task_id: uuid.UUID) -> TaskDB | None:
        return self.tasks.get(task_id)

    def update(self, task: TaskDB, data: TaskUpdate) -> TaskDB:
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(task, field, value)
        return task

    def delete(self, task: TaskDB) -> None:
        self.tasks.pop(task.id, None)

@pytest.fixture
def service():
    return TaskService(FakeTaskRepository())

def test_create_and_get_task(service):
    created = service.create_task(TaskCreate(title="Estudar service"))
    assert service.get_task(created.id).title == "Estudar service"

def test_list_tasks_filters_by_status(service):
    service.create_task(TaskCreate(title="Pendente", status=False))
    service.create_task(TaskCreate(title="Concluída", status=True))
    assert [t.title for t in service.list_tasks(status=True)] == ["Concluída"]

def test_get_unknown_task_raises_not_found(service):
    with pytest.raises(TaskNotFoundError):
        service.get_task(uuid.uuid4())

def test_update_unknown_task_raises_not_found(service):
    with pytest.raises(TaskNotFoundError):
        service.update_task(uuid.uuid4(), TaskUpdate(status=True))

def test_delete_unknown_task_raises_not_found(service):
    with pytest.raises(TaskNotFoundError):
        service.delete_task(uuid.uuid4())
