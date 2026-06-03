"""
repository/expense_repo.py
--------------------------
Define o contrato (interface) e a implementação com SQLAlchemy.

Se amanhã trocar SQLite por PostgreSQL, apenas este arquivo muda:
  - A string de conexão em main.py muda (1 linha).
  - O model ORM pode precisar de ajustes de tipo (ex.: JSONB, UUID).
  - Nenhuma camada acima (service, handler) precisa saber disso.

Isso é possível porque service depende da INTERFACE, não da implementação.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional

from sqlalchemy import Column, DateTime, Float, Integer, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from domain.expense import Expense, ExpenseCategory


# ── ORM model (detalhe de infraestrutura, não vaza para o domínio) ────────────

class Base(DeclarativeBase):
    pass


class ExpenseModel(Base):
    __tablename__ = "expenses"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    description = Column(String, nullable=False)
    amount      = Column(Float, nullable=False)
    category    = Column(String, nullable=False)
    date        = Column(DateTime, nullable=False)
    created_at  = Column(DateTime, nullable=False)

    def to_domain(self) -> Expense:
        return Expense(
            id=self.id,
            description=self.description,
            amount=self.amount,
            category=ExpenseCategory(self.category),
            date=self.date,
            created_at=self.created_at,
        )


# ── Interface (contrato) ──────────────────────────────────────────────────────

class ExpenseRepository(ABC):
    """Contrato que o Service usa. Não sabe se o banco é SQLite ou Postgres."""

    @abstractmethod
    def create(self, expense: Expense) -> Expense: ...

    @abstractmethod
    def find_all(self, category: str = "") -> List[Expense]: ...

    @abstractmethod
    def find_by_id(self, id: int) -> Optional[Expense]: ...

    @abstractmethod
    def update(self, expense: Expense) -> Expense: ...

    @abstractmethod
    def delete(self, id: int) -> None: ...


# ── Implementação com SQLAlchemy ──────────────────────────────────────────────

class SQLExpenseRepository(ExpenseRepository):
    """
    Implementação concreta. Recebe a Session via construtor (injeção de
    dependência) — nunca acessa variáveis globais.
    """

    def __init__(self, session: Session):
        self._session = session

    def create(self, expense: Expense) -> Expense:
        model = ExpenseModel(
            description=expense.description,
            amount=expense.amount,
            category=expense.category.value,
            date=expense.date,
            created_at=expense.created_at,
        )
        self._session.add(model)
        self._session.commit()
        self._session.refresh(model)
        return model.to_domain()

    def find_all(self, category: str = "") -> List[Expense]:
        query = self._session.query(ExpenseModel)
        if category:
            query = query.filter(ExpenseModel.category == category)
        # Mais recente primeiro
        query = query.order_by(ExpenseModel.created_at.desc())
        return [m.to_domain() for m in query.all()]

    def find_by_id(self, id: int) -> Optional[Expense]:
        model = self._session.get(ExpenseModel, id)
        return model.to_domain() if model else None

    def update(self, expense: Expense) -> Expense:
        model = self._session.get(ExpenseModel, expense.id)
        model.description = expense.description
        model.amount      = expense.amount
        model.category    = expense.category.value
        self._session.commit()
        self._session.refresh(model)
        return model.to_domain()

    def delete(self, id: int) -> None:
        model = self._session.get(ExpenseModel, id)
        self._session.delete(model)
        self._session.commit()


# ── Factory de engine/session (usado em main.py) ─────────────────────────────

def create_session_factory(database_url: str):
    engine = create_engine(database_url, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)
