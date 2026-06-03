"""
repository/figurinha_repository.py
----------------------------------
Interface de persistência usada pelo service.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from domain.figurinha import Figurinha


class FigurinhaRepository(ABC):
    """Contrato que qualquer repositorio de figurinhas precisa cumprir."""

    @abstractmethod
    def create(self, figurinha: Figurinha) -> Figurinha:
        raise NotImplementedError

    @abstractmethod
    def find_all(self, tipo: str = "", posicao: str = "") -> List[Figurinha]:
        raise NotImplementedError

    @abstractmethod
    def find_by_id(self, id: int) -> Optional[Figurinha]:
        raise NotImplementedError

    @abstractmethod
    def update(self, figurinha: Figurinha) -> Figurinha:
        raise NotImplementedError

    @abstractmethod
    def delete(self, id: int) -> None:
        raise NotImplementedError
