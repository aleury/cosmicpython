from datetime import date
from typing import Iterable

import pytest

import domain
from service_layer import services


class FakeSession:
    committed = False

    def commit(self):
        self.committed = True


class FakeRepository:
    def __init__(self, batches: Iterable[domain.Batch]):
        self._batches = set(batches)

    def add(self, batch: domain.Batch):
        return self._batches.add(batch)

    def get(self, reference: str):
        return next(b for b in self._batches if b.reference == reference)

    def list(self) -> list[domain.Batch]:
        return list(self._batches)

    @staticmethod
    def for_batch(ref: str, sku: str, qty: int, eta: date | None = None):
        return FakeRepository([domain.Batch(ref, sku, qty, eta)])


def test_returns_allocation():
    repo = FakeRepository.for_batch("b1", "COMPLICATED-LAMP", 100, eta=None)
    result = services.allocate("o1", "COMPLICATED-LAMP", 10, repo, FakeSession())
    assert result == "b1"


def test_error_for_out_of_stock_sku():
    repo = FakeRepository.for_batch("b1", "DOG-BED", 1, eta=None)

    with pytest.raises(domain.OutOfStock, match="Out of stock for sku DOG-BED"):
        services.allocate("o1", "DOG-BED", 10, repo, FakeSession())


def test_error_for_invalid_sku():
    repo = FakeRepository.for_batch("b1", "AREALSKU", 100, eta=None)

    with pytest.raises(services.InvalidSku, match="Invalid sku NONEXISTENTSKU"):
        services.allocate("o1", "NONEXISTENTSKU", 10, repo, FakeSession())


def test_commits():
    repo = FakeRepository.for_batch("b1", "OMINOUS-MIRROR", 100, eta=None)
    session = FakeSession()

    services.allocate("o1", "OMINOUS-MIRROR", 10, repo, session)
    assert session.committed is True
