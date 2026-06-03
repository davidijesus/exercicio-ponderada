"""
main.py
-------
Raiz de composição: único lugar que sabe de todas as camadas.
Abre o banco → instancia repositório → instancia serviço → registra rotas.

Fluxo de dependências (apenas para baixo):
  main → handler → service → repository → domain
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from repository.expense_repo import SQLExpenseRepository, create_session_factory
from service.expense_service import ExpenseServiceImpl
from handler.expense_handler import create_expense_router

# ── Configuração do banco ─────────────────────────────────────────────────────

DATABASE_URL = "sqlite:///./gastos.db"
SessionLocal = create_session_factory(DATABASE_URL)

# ── Composição das camadas ────────────────────────────────────────────────────

def get_service() -> ExpenseServiceImpl:
    """Cria as camadas a cada request (stateless por design)."""
    session = SessionLocal()
    try:
        repo    = SQLExpenseRepository(session)
        service = ExpenseServiceImpl(repo)
        yield service
    finally:
        session.close()

# ── Aplicação FastAPI ─────────────────────────────────────────────────────────

app = FastAPI(
    title="Registro de Gastos Pessoais",
    description="API RESTful com arquitetura em camadas (Domain / Repository / Service / Handler)",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Registra rotas ────────────────────────────────────────────────────────────
# Instanciamos o serviço uma vez para o router.
# (Para produção, use FastAPI Depends para injeção por request.)

from sqlalchemy.orm import Session

def _make_router():
    session = SessionLocal()
    repo    = SQLExpenseRepository(session)
    service = ExpenseServiceImpl(repo)
    return create_expense_router(service)

app.include_router(_make_router())


# ── Ponto de entrada ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
