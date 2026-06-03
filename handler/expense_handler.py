"""
handler/expense_handler.py
--------------------------
Tradução HTTP ↔ domínio.
  - Lê parâmetros da requisição (path, query, body).
  - Chama o service com objetos de domínio.
  - Mapeia erros de domínio → status HTTP corretos.
  - NÃO contém regras de negócio.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional

from domain.expense import CreateExpenseRequest, UpdateExpenseRequest
from service.expense_service import (
    ExpenseNotFoundError,
    ExpenseService,
    InvalidAmountError,
    InvalidCategoryError,
    InvalidDescriptionError,
)


# ── Schemas Pydantic (validação/serialização do FastAPI) ──────────────────────

class CreateExpenseBody(BaseModel):
    description: str = Field(..., min_length=3)
    amount: float    = Field(..., gt=0)
    category: str    = Field(...)


class UpdateExpenseBody(BaseModel):
    description: Optional[str]  = None
    amount: Optional[float]     = None
    category: Optional[str]     = None


# ── Router factory (recebe service via injeção de dependência) ─────────────────

def create_expense_router(service: ExpenseService) -> APIRouter:
    router = APIRouter(prefix="/expenses", tags=["expenses"])

    # ── helper: mapeia erros de domínio → HTTP ────────────────────────────────
    def domain_error_to_http(err: Exception) -> HTTPException:
        if isinstance(err, ExpenseNotFoundError):
            return HTTPException(status_code=404, detail={"error": str(err)})
        if isinstance(err, (InvalidAmountError, InvalidCategoryError, InvalidDescriptionError)):
            return HTTPException(status_code=400, detail={"error": str(err)})
        return HTTPException(status_code=500, detail={"error": "erro interno"})

    # ── POST /expenses ────────────────────────────────────────────────────────
    @router.post("/", status_code=201)
    def create_expense(body: CreateExpenseBody):
        req = CreateExpenseRequest(
            description=body.description,
            amount=body.amount,
            category=body.category,
        )
        try:
            expense = service.create(req)
        except (InvalidAmountError, InvalidCategoryError, InvalidDescriptionError) as e:
            raise domain_error_to_http(e)
        return expense.to_dict()

    # ── GET /expenses ─────────────────────────────────────────────────────────
    @router.get("/")
    def list_expenses(category: str = Query(default="")):
        try:
            expenses = service.list(category)
        except InvalidCategoryError as e:
            raise domain_error_to_http(e)
        return [e.to_dict() for e in expenses]

    # ── GET /expenses/:id ─────────────────────────────────────────────────────
    @router.get("/{id}")
    def get_expense(id: int):
        try:
            expense = service.get_by_id(id)
        except ExpenseNotFoundError as e:
            raise domain_error_to_http(e)
        return expense.to_dict()

    # ── PATCH /expenses/:id ───────────────────────────────────────────────────
    @router.patch("/{id}")
    def update_expense(id: int, body: UpdateExpenseBody):
        req = UpdateExpenseRequest(
            description=body.description,
            amount=body.amount,
            category=body.category,
        )
        try:
            expense = service.update(id, req)
        except ExpenseNotFoundError as e:
            raise domain_error_to_http(e)
        except (InvalidAmountError, InvalidCategoryError, InvalidDescriptionError) as e:
            raise domain_error_to_http(e)
        return expense.to_dict()

    # ── DELETE /expenses/:id ──────────────────────────────────────────────────
    @router.delete("/{id}", status_code=204)
    def delete_expense(id: int):
        try:
            service.delete(id)
        except ExpenseNotFoundError as e:
            raise domain_error_to_http(e)
        return None

    return router
