"""Configuração da conexão com o banco de dados SQLite."""

from collections.abc import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

DATABASE_URL = "sqlite:///./tasks.db"

# check_same_thread=False é necessário no SQLite porque o FastAPI
# pode atender uma mesma requisição em threads diferentes.
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False)
class Base(DeclarativeBase):
    """Classe base para os modelos do SQLAlchemy."""
    
def get_db() -> Generator[Session, None, None]:
    """Fornece uma sessão do banco e garante que ela seja fechada ao final."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()