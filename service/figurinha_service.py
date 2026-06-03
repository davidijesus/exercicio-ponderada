"""
service/figurinha_service.py
----------------------------
Regras de negocio da API de figurinhas.

Esta camada valida campos obrigatorios, tipos, posicoes e existencia de IDs.
Ela nao sabe nada sobre HTTP nem sobre o banco concreto.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import UTC, datetime
from typing import List

from domain.figurinha import (
    CreateFigurinhaRequest,
    Figurinha,
    FigurinhaPosicao,
    FigurinhaTipo,
    UpdateFigurinhaRequest,
)
from repository.figurinha_repository import FigurinhaRepository


class FigurinhaNotFoundError(Exception):
    """Lancado quando a figurinha solicitada nao existe."""

    def __init__(self, id: int):
        super().__init__("figurinha não encontrado")
        self.id = id


class RequiredFieldError(Exception):
    """Lancado quando um campo obrigatorio nao foi enviado."""

    def __init__(self, field: str):
        super().__init__(f"campo obrigatorio ausente: {field}")
        self.field = field


class InvalidTipoError(Exception):
    """Lancado quando tipo nao esta na lista de valores validos."""

    def __init__(self, value: str):
        valid = [tipo.value for tipo in FigurinhaTipo]
        super().__init__(f"tipo invalido: '{value}'. Valores aceitos: {valid}")
        self.value = value


class InvalidPosicaoError(Exception):
    """Lancado quando posicao nao esta na lista de valores validos."""

    def __init__(self, value: str):
        valid = [posicao.value for posicao in FigurinhaPosicao]
        super().__init__(f"posicao invalida: '{value}'. Valores aceitos: {valid}")
        self.value = value


class FigurinhaService(ABC):
    """Interface da camada de regras de negocio."""

    @abstractmethod
    def create(self, req: CreateFigurinhaRequest) -> Figurinha:
        raise NotImplementedError

    @abstractmethod
    def list(self, tipo: str = "", posicao: str = "") -> List[Figurinha]:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, id: int) -> Figurinha:
        raise NotImplementedError

    @abstractmethod
    def update(self, id: int, req: UpdateFigurinhaRequest) -> Figurinha:
        raise NotImplementedError

    @abstractmethod
    def delete(self, id: int) -> None:
        raise NotImplementedError


class FigurinhaServiceImpl(FigurinhaService):
    """Implementacao com repositorio recebido por injecao de dependencia."""

    def __init__(self, repo: FigurinhaRepository):
        self._repo = repo

    def _require_text(self, value: str | None, field: str) -> str:
        if value is None or not str(value).strip():
            raise RequiredFieldError(field)
        return str(value).strip()

    def _validate_tipo(self, value: str | None) -> FigurinhaTipo:
        tipo = self._require_text(value, "tipo")
        try:
            return FigurinhaTipo(tipo)
        except ValueError:
            raise InvalidTipoError(tipo)

    def _validate_posicao(self, value: str | None) -> FigurinhaPosicao:
        posicao = self._require_text(value, "posicao")
        try:
            return FigurinhaPosicao(posicao)
        except ValueError:
            raise InvalidPosicaoError(posicao)

    def create(self, req: CreateFigurinhaRequest) -> Figurinha:
        numero = self._require_text(req.numero, "numero")
        tipo = self._validate_tipo(req.tipo)
        posicao = self._validate_posicao(req.posicao)

        now = datetime.now(UTC)
        figurinha = Figurinha(
            id=0,
            numero=numero,
            tipo=tipo,
            posicao=posicao,
            updated_at=now,
            created_at=now,
        )
        return self._repo.create(figurinha)

    def list(self, tipo: str = "", posicao: str = "") -> List[Figurinha]:
        tipo_filter = ""
        posicao_filter = ""

        if tipo:
            tipo_filter = self._validate_tipo(tipo).value
        if posicao:
            posicao_filter = self._validate_posicao(posicao).value

        return self._repo.find_all(tipo=tipo_filter, posicao=posicao_filter)

    def get_by_id(self, id: int) -> Figurinha:
        figurinha = self._repo.find_by_id(id)
        if figurinha is None:
            raise FigurinhaNotFoundError(id)
        return figurinha

    def update(self, id: int, req: UpdateFigurinhaRequest) -> Figurinha:
        figurinha = self._repo.find_by_id(id)
        if figurinha is None:
            raise FigurinhaNotFoundError(id)

        figurinha.numero = self._require_text(req.numero, "numero")
        figurinha.tipo = self._validate_tipo(req.tipo)
        figurinha.posicao = self._validate_posicao(req.posicao)
        figurinha.updated_at = datetime.now(UTC)

        return self._repo.update(figurinha)

    def delete(self, id: int) -> None:
        figurinha = self._repo.find_by_id(id)
        if figurinha is None:
            raise FigurinhaNotFoundError(id)
        self._repo.delete(id)
