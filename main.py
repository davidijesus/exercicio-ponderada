"""
main.py
-------
Raiz de composicao da aplicacao.

Este é o unico arquivo que conhece todas as camadas: 

Ele abre o banco, 
Cria o repositorio, injeta no service e registra as rotas HTTP.
"""

from os import getenv

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from handler.figurinha_handler import create_figurinha_router
from repository.figurinha_repo import SQLFigurinhaRepository, create_session_factory
from service.figurinha_service import FigurinhaServiceImpl


DATABASE_URL = getenv("DATABASE_URL", "sqlite:///./figurinhas.db")
SessionLocal = create_session_factory(DATABASE_URL)


def get_service():
    """Cria uma pilha repo -> service por request e fecha a sessao depois."""

    session = SessionLocal()
    try:
        repo = SQLFigurinhaRepository(session)
        yield FigurinhaServiceImpl(repo)
    finally:
        session.close()


app = FastAPI(
    title="Album de Figurinhas da Copa 2026",
    description="API RESTful em camadas: Domain, Repository, Service e Handler",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(create_figurinha_router(get_service))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
