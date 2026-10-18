"""Endpoints HTTP da API de tarefas."""

import uuid
from http import HTTPStatus
from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.schemas import Task, TaskCreate, TaskUpdate
from app.repositories.task_repository import TaskRepository
from app.services.task_service import TaskService
router = APIRouter(prefix="/tasks", tags=["tasks"])

def get_task_service(db: Annotated[Session, Depends(get_db)]) -> TaskService:
    """Monta o service com o repository da sessão atual."""
    return TaskService(TaskRepository(db))
ServiceDep = Annotated[TaskService, Depends(get_task_service)]

@router.post("", response_model=Task, status_code=HTTPStatus.CREATED)
def create_task(data: TaskCreate, service: ServiceDep):
    """Cria uma nova tarefa."""
    return service.create_task(data)

@router.get("", response_model=list[Task])
def list_tasks(service: ServiceDep, status: bool | None = None):
    """Lista as tarefas. Use ?status=true ou ?status=false para filtrar."""
    return service.list_tasks(status)

@router.get("/{task_id}", response_model=Task)
def get_task(task_id: uuid.UUID, service: ServiceDep):
    """Busca uma tarefa pelo id."""
    return service.get_task(task_id)

@router.put("/{task_id}", response_model=Task)
def update_task(task_id: uuid.UUID, data: TaskUpdate, service: ServiceDep):
    """Atualiza os campos informados de uma tarefa."""
    return service.update_task(task_id, data)

@router.delete("/{task_id}", status_code=HTTPStatus.NO_CONTENT)
def delete_task(task_id: uuid.UUID, service: ServiceDep):
    """Remove uma tarefa."""
    service.delete_task(task_id)
