"""
tests/test_service.py
---------------------
Testes unitários da camada Service.
Usam um repositório em memória (FakeExpenseRepository) — sem banco real.
Isso só é possível porque o service depende da INTERFACE, não da implementação.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import datetime
from typing import Dict, List, Optional

from domain.expense import CreateExpenseRequest, Expense, ExpenseCategory, UpdateExpenseRequest
from repository.expense_repo import ExpenseRepository
from service.expense_service import (
    ExpenseNotFoundError,
    ExpenseServiceImpl,
    InvalidAmountError,
    InvalidCategoryError,
    InvalidDescriptionError,
)


# ── Repositório falso em memória ──────────────────────────────────────────────

class FakeExpenseRepository(ExpenseRepository):
    def __init__(self):
        self._store: Dict[int, Expense] = {}
        self._next_id = 1

    def create(self, expense: Expense) -> Expense:
        expense.id = self._next_id
        self._next_id += 1
        self._store[expense.id] = expense
        return expense

    def find_all(self, category: str = "") -> List[Expense]:
        results = list(self._store.values())
        if category:
            results = [e for e in results if e.category.value == category]
        return sorted(results, key=lambda e: e.created_at, reverse=True)

    def find_by_id(self, id: int) -> Optional[Expense]:
        return self._store.get(id)

    def update(self, expense: Expense) -> Expense:
        self._store[expense.id] = expense
        return expense

    def delete(self, id: int) -> None:
        del self._store[id]


# ── Helpers ────────────────────────────────────────────────────────────────────

def make_service() -> ExpenseServiceImpl:
    return ExpenseServiceImpl(FakeExpenseRepository())

def valid_create_req(**kwargs) -> CreateExpenseRequest:
    defaults = {"description": "Almoço", "amount": 35.50, "category": "alimentacao"}
    defaults.update(kwargs)
    return CreateExpenseRequest(**defaults)


# ── Testes de criação ─────────────────────────────────────────────────────────

def test_create_returns_expense_with_id():
    svc = make_service()
    expense = svc.create(valid_create_req())
    assert expense.id == 1
    assert expense.description == "Almoço"
    assert expense.amount == 35.50
    assert expense.category == ExpenseCategory.FOOD

def test_create_fills_date_automatically():
    svc = make_service()
    before = datetime.utcnow()
    expense = svc.create(valid_create_req())
    after = datetime.utcnow()
    assert before <= expense.date <= after

def test_create_invalid_amount_raises():
    svc = make_service()
    try:
        svc.create(valid_create_req(amount=0))
        assert False, "deveria ter lançado"
    except InvalidAmountError:
        pass

def test_create_negative_amount_raises():
    svc = make_service()
    try:
        svc.create(valid_create_req(amount=-10))
        assert False, "deveria ter lançado"
    except InvalidAmountError:
        pass

def test_create_invalid_category_raises():
    svc = make_service()
    try:
        svc.create(valid_create_req(category="lazer"))
        assert False, "deveria ter lançado"
    except InvalidCategoryError as e:
        assert "lazer" in str(e)

def test_create_short_description_raises():
    svc = make_service()
    try:
        svc.create(valid_create_req(description="ab"))
        assert False, "deveria ter lançado"
    except InvalidDescriptionError:
        pass


# ── Testes de listagem ────────────────────────────────────────────────────────

def test_list_all_expenses():
    svc = make_service()
    svc.create(valid_create_req(description="Almoço"))
    svc.create(valid_create_req(description="Uber", category="transporte"))
    assert len(svc.list()) == 2

def test_list_filter_by_category():
    svc = make_service()
    svc.create(valid_create_req(description="Almoço", category="alimentacao"))
    svc.create(valid_create_req(description="Uber",   category="transporte"))
    result = svc.list("alimentacao")
    assert len(result) == 1
    assert result[0].description == "Almoço"

def test_list_invalid_category_raises():
    svc = make_service()
    try:
        svc.list("lazer")
        assert False
    except InvalidCategoryError:
        pass


# ── Testes de busca por ID ────────────────────────────────────────────────────

def test_get_by_id_existing():
    svc = make_service()
    created = svc.create(valid_create_req())
    found = svc.get_by_id(created.id)
    assert found.id == created.id

def test_get_by_id_not_found():
    svc = make_service()
    try:
        svc.get_by_id(999)
        assert False
    except ExpenseNotFoundError:
        pass


# ── Testes de update ──────────────────────────────────────────────────────────

def test_update_description():
    svc = make_service()
    expense = svc.create(valid_create_req())
    original_date = expense.date
    updated = svc.update(expense.id, UpdateExpenseRequest(description="Jantar"))
    assert updated.description == "Jantar"
    assert updated.date == original_date  # date NÃO muda

def test_update_preserves_unset_fields():
    svc = make_service()
    expense = svc.create(valid_create_req(amount=50.0))
    updated = svc.update(expense.id, UpdateExpenseRequest(description="Outro"))
    assert updated.amount == 50.0  # amount não foi alterado

def test_update_not_found():
    svc = make_service()
    try:
        svc.update(999, UpdateExpenseRequest(description="X"))
        assert False
    except ExpenseNotFoundError:
        pass


# ── Testes de delete ──────────────────────────────────────────────────────────

def test_delete_existing():
    svc = make_service()
    expense = svc.create(valid_create_req())
    svc.delete(expense.id)
    assert len(svc.list()) == 0

def test_delete_not_found():
    svc = make_service()
    try:
        svc.delete(999)
        assert False
    except ExpenseNotFoundError:
        pass


# ── Runner simples ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    tests = [v for k, v in list(globals().items()) if k.startswith("test_")]
    passed = failed = 0
    for t in tests:
        try:
            t()
            print(f"  ✓  {t.__name__}")
            passed += 1
        except Exception as e:
            print(f"  ✗  {t.__name__}: {e}")
            failed += 1
    print(f"\n{passed} passou, {failed} falhou")
