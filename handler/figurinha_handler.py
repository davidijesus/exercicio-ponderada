"""
handler/figurinha_handler.py
----------------------------
Traducao HTTP pro domínio.
"""

from __future__ import annotations

from typing import Callable, Optional

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel

from domain.figurinha import CreateFigurinhaRequest, UpdateFigurinhaRequest
from service.figurinha_service import (
    FigurinhaNotFoundError,
    FigurinhaService,
    InvalidPosicaoError,
    InvalidTipoError,
    RequiredFieldError,
)


class CreateFigurinhaBody(BaseModel):
    numero: Optional[str] = None
    tipo: Optional[str] = None
    posicao: Optional[str] = None


class UpdateFigurinhaBody(BaseModel):
    numero: Optional[str] = None
    tipo: Optional[str] = None
    posicao: Optional[str] = None


def create_figurinha_router(
    get_service: Callable[[], FigurinhaService],
) -> APIRouter:
    router = APIRouter(prefix="/figurinha", tags=["figurinha"])

    def error_response(status_code: int, error: Exception) -> JSONResponse:
        return JSONResponse(status_code=status_code, content={"error": str(error)})

    def bad_request(error: Exception) -> JSONResponse:
        return error_response(400, error)

    def not_found(error: Exception) -> JSONResponse:
        return error_response(404, error)

    @router.post("", status_code=201)
    def create_figurinha(
        body: Optional[CreateFigurinhaBody] = None,
        service: FigurinhaService = Depends(get_service),
    ):
        req = CreateFigurinhaRequest(
            numero=body.numero if body else None,
            tipo=body.tipo if body else None,
            posicao=body.posicao if body else None,
        )
        try:
            figurinha = service.create(req)
        except (RequiredFieldError, InvalidTipoError, InvalidPosicaoError) as error:
            return bad_request(error)
        return figurinha.to_dict()

    @router.get("")
    def list_figurinhas(
        tipo: str = Query(default=""),
        posicao: str = Query(default=""),
        service: FigurinhaService = Depends(get_service),
    ):
        try:
            figurinhas = service.list(tipo=tipo, posicao=posicao)
        except (InvalidTipoError, InvalidPosicaoError) as error:
            return bad_request(error)
        return [figurinha.to_dict() for figurinha in figurinhas]

    @router.get("/{id}")
    def get_figurinha(
        id: int,
        service: FigurinhaService = Depends(get_service),
    ):
        try:
            figurinha = service.get_by_id(id)
        except FigurinhaNotFoundError as error:
            return not_found(error)
        return figurinha.to_dict()

    @router.put("/{id}")
    def update_figurinha(
        id: int,
        body: Optional[UpdateFigurinhaBody] = None,
        service: FigurinhaService = Depends(get_service),
    ):
        req = UpdateFigurinhaRequest(
            numero=body.numero if body else None,
            tipo=body.tipo if body else None,
            posicao=body.posicao if body else None,
        )
        try:
            figurinha = service.update(id, req)
        except FigurinhaNotFoundError as error:
            return not_found(error)
        except (RequiredFieldError, InvalidTipoError, InvalidPosicaoError) as error:
            return bad_request(error)
        return figurinha.to_dict()

    @router.delete("/{id}", status_code=204)
    def delete_figurinha(
        id: int,
        service: FigurinhaService = Depends(get_service),
    ):
        try:
            service.delete(id)
        except FigurinhaNotFoundError as error:
            return not_found(error)
        return Response(status_code=204)

    return router
