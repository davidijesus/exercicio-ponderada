"""
domain/expense.py
-----------------
Vocabulário central da aplicação.
Esta camada NÃO importa nenhuma outra camada interna.

Por que ExpenseCategory é um tipo nomeado?
  - Em vez de qualquer string passar despercebida, o sistema de tipos deixa
    claro que apenas valores do enum são aceitos.
  - O compilador/runtime rejeita valores arbitrários antes mesmo de chegar
    nas regras de negócio.

Por que o DTO de criação é separado da entidade?
  - Impede que o cliente envie campos gerados pelo servidor (id, date,
    created_at), eliminando uma classe inteira de bugs e vulnerabilidades.
"""

from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Optional


# ── Tipo nomeado para categoria ──────────────────────────────────────────────

class ExpenseCategory(str, Enum):
    """Categorias válidas. Usar str como base permite comparar com strings
    comuns e serializar/desserializar sem conversão extra."""
    FOOD      = "alimentacao"
    TRANSPORT = "transporte"
    HEALTH    = "saude"
    EDUCATION = "educacao"
    OTHER     = "outro"


# ── Entidade principal ────────────────────────────────────────────────────────

class Expense:
    """Representa um gasto no domínio. Independente de banco ou framework."""

    def __init__(
        self,
        id: int,
        description: str,
        amount: float,
        category: ExpenseCategory,
        date: datetime,
        created_at: datetime,
    ):
        self.id = id
        self.description = description
        self.amount = amount
        self.category = category
        self.date = date
        self.created_at = created_at

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "description": self.description,
            "amount": self.amount,
            "category": self.category.value,
            "date": self.date.isoformat(),
            "created_at": self.created_at.isoformat(),
        }


# ── DTOs de entrada ───────────────────────────────────────────────────────────

class CreateExpenseRequest:
    """
    Dados que o cliente envia ao criar um gasto.
    Separado de Expense: o cliente NÃO escolhe id, date nem created_at.
    """

    def __init__(self, description: str, amount: float, category: str):
        self.description = description
        self.amount = amount
        self.category = category

    @classmethod
    def from_dict(cls, data: dict) -> "CreateExpenseRequest":
        return cls(
            description=data.get("description", ""),
            amount=data.get("amount", 0),
            category=data.get("category", ""),
        )


class UpdateExpenseRequest:
    """
    Dados que o cliente envia ao atualizar um gasto.
    Campos opcionais (Optional) distinguem 'não enviado' de 'enviado como vazio'.
    date NÃO está aqui — o cliente jamais pode alterar a data.
    """

    def __init__(
        self,
        description: Optional[str] = None,
        amount: Optional[float] = None,
        category: Optional[str] = None,
    ):
        self.description = description
        self.amount = amount
        self.category = category

    @classmethod
    def from_dict(cls, data: dict) -> "UpdateExpenseRequest":
        return cls(
            description=data.get("description"),
            amount=data.get("amount"),
            category=data.get("category"),
        )
