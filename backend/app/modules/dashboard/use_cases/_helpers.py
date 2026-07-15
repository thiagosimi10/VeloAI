"""Utilitários de data compartilhados entre os use cases do Dashboard."""

from __future__ import annotations

from datetime import date


def first_day_of_month(reference: date) -> date:
    return reference.replace(day=1)


def add_months(reference: date, months: int) -> date:
    month_index = reference.month - 1 + months
    year = reference.year + month_index // 12
    month = month_index % 12 + 1
    return reference.replace(year=year, month=month, day=1)
