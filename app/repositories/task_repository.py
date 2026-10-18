"""Implementação do repository de tarefas com SQLAlchemy."""

import uuid
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.db_models import TaskDB
from app.models.schemas import TaskCreate, TaskUpdate
from app.repositories.interface import ITaskRepository


class TaskRepository(ITaskRepository):
    """Executa as operações de CRUD da tabela `tasks`."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, data: TaskCreate) -> TaskDB:
        """Cria uma nova tarefa e a retorna já com id e data de criação."""
        task = TaskDB(**data.model_dump())
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def list_all(self, status: bool | None = None) -> list[TaskDB]:
        """Lista as tarefas por ordem de criação, com filtro opcional por status."""
        query = select(TaskDB).order_by(TaskDB.created_at)
        if status is not None:
            query = query.where(TaskDB.status == status)
        return list(self.db.scalars(query).all())

    def get(self, task_id: uuid.UUID) -> TaskDB | None:
        """Busca uma tarefa pelo id. Retorna None se ela não existir."""
        return self.db.get(TaskDB, task_id)

    def update(self, task: TaskDB, data: TaskUpdate) -> TaskDB:
        """Atualiza apenas os campos informados (os que não forem None)."""
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(task, field, value)
        self.db.commit()
        self.db.refresh(task)
        return task

    def delete(self, task: TaskDB) -> None:
        """Remove uma tarefa do banco."""
        self.db.delete(task)
        self.db.commit()