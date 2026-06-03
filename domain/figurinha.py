"""
domain/figurinha.py
-------------------
Vocabulario central da API de figurinhas.

Esta camada nao conhece HTTP, banco de dados, FastAPI ou SQLAlchemy. Ela
concentra os tipos que as outras camadas usam para conversar sem misturar
responsabilidades.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional


class FigurinhaTipo(str, Enum):
    """Tipos validos de figurinha no album."""

    COMUM = "comum"
    BRILHANTE = "brilhante"
    LEGENDS_OURO = "legends_ouro"
    LEGENDS_BRONZE = "legends_bronze"


class FigurinhaPosicao(str, Enum):
    """Posicoes validas para figurinhas de jogadores."""

    GOLEIRO = "Goleiro"
    ZAGUEIRO = "Zagueiro"
    MEIO_CAMPISTA = "Meio-campista"
    ATACANTE = "Atacante"


class Figurinha:
    """Entidade de dominio retornada pela API."""

    def __init__(
        self,
        id: int,
        numero: str,
        tipo: FigurinhaTipo,
        posicao: FigurinhaPosicao,
        updated_at: datetime,
        created_at: datetime,
    ):
        self.id = id
        self.numero = numero
        self.tipo = tipo
        self.posicao = posicao
        self.updated_at = updated_at
        self.created_at = created_at

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "numero": self.numero,
            "tipo": self.tipo.value,
            "posicao": self.posicao.value,
            "updated_at": self.updated_at.isoformat(),
            "created_at": self.created_at.isoformat(),
        }


class CreateFigurinhaRequest:
    """
    Dados aceitos na criacao de uma figurinha.

    Campos gerados pelo servidor, como id, updated_at e created_at, nao entram
    neste DTO para impedir que o cliente controle dados de auditoria.
    """

    def __init__(
        self,
        numero: Optional[str],
        tipo: Optional[str],
        posicao: Optional[str],
    ):
        self.numero = numero
        self.tipo = tipo
        self.posicao = posicao

    @classmethod
    def from_dict(cls, data: dict) -> "CreateFigurinhaRequest":
        return cls(
            numero=data.get("numero"),
            tipo=data.get("tipo"),
            posicao=data.get("posicao"),
        )


class UpdateFigurinhaRequest:
    """
    Dados aceitos no PUT de uma figurinha.

    Como a rota e PUT, os campos editaveis sao obrigatorios. Timestamps seguem
    sendo responsabilidade exclusiva do servidor.
    """

    def __init__(
        self,
        numero: Optional[str],
        tipo: Optional[str],
        posicao: Optional[str],
    ):
        self.numero = numero
        self.tipo = tipo
        self.posicao = posicao

    @classmethod
    def from_dict(cls, data: dict) -> "UpdateFigurinhaRequest":
        return cls(
            numero=data.get("numero"),
            tipo=data.get("tipo"),
            posicao=data.get("posicao"),
        )
