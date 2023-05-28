import pytest

import domain
from adapters.repository import FakeRepository
from service_layer import services


class FakeSession:
    committed = False

    def commit(self):
        self.committed = True


def test_returns_allocation():
    line = domain.OrderLine("o1", "COMPLICATED-LAMP", 10)
    batch = domain.Batch("b1", "COMPLICATED-LAMP", 100, eta=None)
    repo = FakeRepository([batch])

    result = services.allocate(line, repo, FakeSession())
    assert result == "b1"


def test_error_for_out_of_stock_sku():
    line = domain.OrderLine("o1", "DOG-BED", 10)
    batch = domain.Batch("b1", "DOG-BED", 1, eta=None)
    repo = FakeRepository([batch])

    with pytest.raises(domain.OutOfStock, match="Out of stock for sku DOG-BED"):
        services.allocate(line, repo, FakeSession())


def test_error_for_invalid_sku():
    line = domain.OrderLine("o1", "NONEXISTENTSKU", 10)
    batch = domain.Batch("b1", "AREALSKU", 100, eta=None)
    repo = FakeRepository([batch])

    with pytest.raises(services.InvalidSku, match="Invalid sku NONEXISTENTSKU"):
        services.allocate(line, repo, FakeSession())


def test_commits():
    line = domain.OrderLine("o1", "OMINOUS-MIRROR", 10)
    batch = domain.Batch("b1", "OMINOUS-MIRROR", 100, eta=None)
    repo = FakeRepository([batch])
    session = FakeSession()

    services.allocate(line, repo, session)
    assert session.committed is True
