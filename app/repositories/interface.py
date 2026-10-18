"""Contrato (interface) que todo repository de tarefas deve seguir."""

import uuid
from abc import ABC, abstractmethod
from app.models.db_models import TaskDB
from app.models.schemas import TaskCreate, TaskUpdate


class ITaskRepository(ABC):
    """Define as operações de acesso a dados de tarefas.

    O service depende deste contrato, e não de uma implementação concreta.
    Assim é possível trocar o banco ou usar um repository falso nos testes.
    """

    @abstractmethod
    def create(self, data: TaskCreate) -> TaskDB:
        """Cria e retorna uma nova tarefa."""

    @abstractmethod
    def list_all(self, status: bool | None = None) -> list[TaskDB]:
        """Lista as tarefas, com filtro opcional por status."""

    @abstractmethod
    def get(self, task_id: uuid.UUID) -> TaskDB | None:
        """Busca uma tarefa pelo id, ou retorna None se não existir."""

    @abstractmethod
    def update(self, task: TaskDB, data: TaskUpdate) -> TaskDB:
        """Atualiza os campos informados de uma tarefa."""

    @abstractmethod
    def delete(self, task: TaskDB) -> None:
        """Remove uma tarefa."""