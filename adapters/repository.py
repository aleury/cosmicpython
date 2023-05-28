from typing import Iterable, Protocol

from sqlalchemy.orm import Session

import domain


class Repository(Protocol):
    def add(self, batch: domain.Batch):
        raise NotImplementedError

    def get(self, reference: str) -> domain.Batch:
        raise NotImplementedError

    def list(self) -> list[domain.Batch]:
        raise NotImplementedError


class FakeRepository:
    def __init__(self, batches: Iterable[domain.Batch]):
        self._batches = set(batches)

    def add(self, batch: domain.Batch):
        return self._batches.add(batch)

    def get(self, reference: str):
        return next(b for b in self._batches if b.reference == reference)

    def list(self) -> list[domain.Batch]:
        return list(self._batches)


class SqlAlchemyRepository:
    def __init__(self, session: Session):
        self.session = session

    def add(self, batch: domain.Batch):
        self.session.add(batch)

    def get(self, reference: str) -> domain.Batch:
        return self.session.query(domain.Batch).filter_by(reference=reference).one()

    def list(self) -> list[domain.Batch]:
        return self.session.query(domain.Batch).all()
