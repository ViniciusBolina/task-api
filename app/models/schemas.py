"""Modelos Pydantic de entrada e saída da API de tarefas."""

import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class TaskBase(BaseModel):
    """Campos comuns a criação e leitura de tarefas."""
    title: str = Field(
        ..., min_length=3, max_length=100, description="Título da tarefa"
    )
    description: str | None = Field(
        None, description="Descrição detalhada da tarefa"
    )
    status: bool = Field(False, description="True se a tarefa estiver concluída")

class TaskCreate(TaskBase):
    """Modelo recebido na criação de uma nova tarefa."""

class TaskUpdate(BaseModel):
    """Modelo recebido na atualização; todos os campos são opcionais."""
    title: str | None = Field(
        None, min_length=3, max_length=100, description="Novo título"
    )
    description: str | None = Field(None, description="Nova descrição")
    status: bool | None = Field(None, description="Novo status de conclusão")

class Task(TaskBase):
    """Modelo devolvido pela API, com os campos gerados pelo sistema."""
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID = Field(..., description="Identificador único da tarefa")
    created_at: datetime = Field(..., description="Data e hora de criação")