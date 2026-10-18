"""Ponto de entrada da aplicação FastAPI."""

from contextlib import asynccontextmanager
from http import HTTPStatus
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.api.routes import router
from app.database import Base, engine
from app.models import db_models  # noqa: F401  (registra a tabela no Base)
from app.services.task_service import TaskNotFoundError

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Cria as tabelas do banco ao iniciar a aplicação."""
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(
    title="Task API",
    description="Micro-API de gerenciamento de tarefas.",
    version="0.1.0",
    lifespan=lifespan,
)
app.include_router(router)

@app.exception_handler(TaskNotFoundError)
async def task_not_found_handler(request: Request, exc: TaskNotFoundError):
    """Converte TaskNotFoundError em uma resposta 404."""
    return JSONResponse(status_code=HTTPStatus.NOT_FOUND, content={"detail": str(exc)})
