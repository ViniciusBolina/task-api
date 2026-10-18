"""Regras de negócio das tarefas."""

import uuid
from app.models.db_models import TaskDB
from app.models.schemas import TaskCreate, TaskUpdate
from app.repositories.interface import ITaskRepository

class TaskNotFoundError(Exception):
    """Lançada quando uma tarefa não existe."""

    def __init__(self, task_id: uuid.UUID) -> None:
        super().__init__(f"Tarefa {task_id} não encontrada.")
        self.task_id = task_id

class TaskService:
    """Coordena as operações de tarefas entre a API e o repository."""

    def __init__(self, repository: ITaskRepository) -> None:
        self.repository = repository

    def create_task(self, data: TaskCreate) -> TaskDB:
        """Cria uma nova tarefa."""
        return self.repository.create(data)

    def list_tasks(self, status: bool | None = None) -> list[TaskDB]:
        """Lista as tarefas, com filtro opcional por status."""
        return self.repository.list_all(status)

    def get_task(self, task_id: uuid.UUID) -> TaskDB:
        """Busca uma tarefa ou lança TaskNotFoundError se ela não existir."""
        task = self.repository.get(task_id)
        if task is None:
            raise TaskNotFoundError(task_id)
        return task

    def update_task(self, task_id: uuid.UUID, data: TaskUpdate) -> TaskDB:
        """Atualiza uma tarefa existente."""
        task = self.get_task(task_id)
        return self.repository.update(task, data)

    def delete_task(self, task_id: uuid.UUID) -> None:
        """Remove uma tarefa existente."""
        task = self.get_task(task_id)
        self.repository.delete(task)
