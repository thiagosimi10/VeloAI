"""Reexporta a configuração de logging compartilhada, já vinculada ao nome deste serviço."""

from __future__ import annotations

from veloai_shared.logging import configure_logging, get_logger

__all__ = ["configure_logging", "get_logger"]
