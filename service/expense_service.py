"""
service/expense_service.py
--------------------------
Camada de regras de negócio.
  - Valida amount, category e description.
  - Preenche date automaticamente (cliente não controla).
  - Lança erros nomeados que o handler mapeia para status HTTP.
  - Depende apenas da interface ExpenseRepository — não sabe de HTTP.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional

from domain.expense import CreateExpenseRequest, Expense, ExpenseCategory, UpdateExpenseRequest
from repository.expense_repo import ExpenseRepository


# ── Erros de domínio (nomeados) ───────────────────────────────────────────────

class ExpenseNotFoundError(Exception):
    """Lançado quando o ID solicitado não existe no banco."""
    def __init__(self, id: int):
        super().__init__(f"gasto não encontrado")
        self.id = id


class InvalidAmountError(Exception):
    """Lançado quando amount <= 0."""
    def __init__(self):
        super().__init__("amount deve ser maior que zero")


class InvalidCategoryError(Exception):
    """Lançado quando category não está na lista de valores válidos."""
    def __init__(self, value: str):
        valid = [c.value for c in ExpenseCategory]
        super().__init__(
            f"categoria inválida: '{value}'. Valores aceitos: {valid}"
        )
        self.value = value


class InvalidDescriptionError(Exception):
    """Lançado quando description tem menos de 3 caracteres."""
    def __init__(self):
        super().__init__("description deve ter no mínimo 3 caracteres")


# ── Interface do serviço ──────────────────────────────────────────────────────

class ExpenseService(ABC):
    @abstractmethod
    def create(self, req: CreateExpenseRequest) -> Expense: ...

    @abstractmethod
    def list(self, category: str = "") -> List[Expense]: ...

    @abstractmethod
    def get_by_id(self, id: int) -> Expense: ...

    @abstractmethod
    def update(self, id: int, req: UpdateExpenseRequest) -> Expense: ...

    @abstractmethod
    def delete(self, id: int) -> None: ...


# ── Implementação ─────────────────────────────────────────────────────────────

class ExpenseServiceImpl(ExpenseService):
    """
    Recebe ExpenseRepository via construtor (injeção de dependência).
    Não importa SQLAlchemy, FastAPI, nem nada de infraestrutura.
    """

    def __init__(self, repo: ExpenseRepository):
        self._repo = repo

    # ── helpers de validação ─────────────────────────────────────────────────

    def _validate_amount(self, amount: float) -> None:
        if amount <= 0:
            raise InvalidAmountError()

    def _validate_category(self, category: str) -> ExpenseCategory:
        try:
            return ExpenseCategory(category)
        except ValueError:
            raise InvalidCategoryError(category)

    def _validate_description(self, description: str) -> None:
        if not description or len(description.strip()) < 3:
            raise InvalidDescriptionError()

    # ── operações ────────────────────────────────────────────────────────────

    def create(self, req: CreateExpenseRequest) -> Expense:
        self._validate_description(req.description)
        self._validate_amount(req.amount)
        category = self._validate_category(req.category)

        now = datetime.utcnow()
        expense = Expense(
            id=0,                 # será gerado pelo banco
            description=req.description.strip(),
            amount=req.amount,
            category=category,
            date=now,             # servidor define, cliente não controla
            created_at=now,
        )
        return self._repo.create(expense)

    def list(self, category: str = "") -> List[Expense]:
        if category:
            # Valida a categoria mesmo no filtro
            self._validate_category(category)
        return self._repo.find_all(category)

    def get_by_id(self, id: int) -> Expense:
        expense = self._repo.find_by_id(id)
        if expense is None:
            raise ExpenseNotFoundError(id)
        return expense

    def update(self, id: int, req: UpdateExpenseRequest) -> Expense:
        expense = self._repo.find_by_id(id)
        if expense is None:
            raise ExpenseNotFoundError(id)

        if req.description is not None:
            self._validate_description(req.description)
            expense.description = req.description.strip()

        if req.amount is not None:
            self._validate_amount(req.amount)
            expense.amount = req.amount

        if req.category is not None:
            expense.category = self._validate_category(req.category)

        # date NUNCA é alterada aqui — regra de negócio explícita

        return self._repo.update(expense)

    def delete(self, id: int) -> None:
        expense = self._repo.find_by_id(id)
        if expense is None:
            raise ExpenseNotFoundError(id)
        self._repo.delete(id)
