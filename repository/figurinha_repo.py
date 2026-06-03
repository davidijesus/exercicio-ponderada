"""
repository/figurinha_repo.py
----------------------------
Contrato de persistência e implementacao SQLAlchemy.

O service em si depende apenas da interface FigurinhaRepository. 
"""

from __future__ import annotations

from typing import List, Optional

from sqlalchemy import Column, DateTime, Integer, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from domain.figurinha import Figurinha, FigurinhaPosicao, FigurinhaTipo
from repository.figurinha_repository import FigurinhaRepository


class Base(DeclarativeBase):
    pass


class FigurinhaModel(Base):
    __tablename__ = "figurinhas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    numero = Column(String, nullable=False)
    tipo = Column(String, nullable=False)
    posicao = Column(String, nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)

    def to_domain(self) -> Figurinha:
        return Figurinha(
            id=self.id,
            numero=self.numero,
            tipo=FigurinhaTipo(self.tipo),
            posicao=FigurinhaPosicao(self.posicao),
            updated_at=self.updated_at,
            created_at=self.created_at,
        )


class SQLFigurinhaRepository(FigurinhaRepository):
    """Implementacao concreta usando uma Session injetada no construtor."""

    def __init__(self, session: Session):
        self._session = session

    def create(self, figurinha: Figurinha) -> Figurinha:
        model = FigurinhaModel(
            numero=figurinha.numero,
            tipo=figurinha.tipo.value,
            posicao=figurinha.posicao.value,
            updated_at=figurinha.updated_at,
            created_at=figurinha.created_at,
        )
        self._session.add(model)
        self._session.commit()
        self._session.refresh(model)
        return model.to_domain()

    def find_all(self, tipo: str = "", posicao: str = "") -> List[Figurinha]:
        query = self._session.query(FigurinhaModel)
        if tipo:
            query = query.filter(FigurinhaModel.tipo == tipo)
        if posicao:
            query = query.filter(FigurinhaModel.posicao == posicao)
        query = query.order_by(FigurinhaModel.created_at.desc())
        return [model.to_domain() for model in query.all()]

    def find_by_id(self, id: int) -> Optional[Figurinha]:
        model = self._session.get(FigurinhaModel, id)
        return model.to_domain() if model else None

    def update(self, figurinha: Figurinha) -> Figurinha:
        model = self._session.get(FigurinhaModel, figurinha.id)
        model.numero = figurinha.numero
        model.tipo = figurinha.tipo.value
        model.posicao = figurinha.posicao.value
        model.updated_at = figurinha.updated_at
        self._session.commit()
        self._session.refresh(model)
        return model.to_domain()

    def delete(self, id: int) -> None:
        model = self._session.get(FigurinhaModel, id)
        self._session.delete(model)
        self._session.commit()


def create_session_factory(database_url: str):
    connect_args = {}
    if database_url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}

    engine = create_engine(database_url, connect_args=connect_args)
    Base.metadata.create_all(engine)
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)
