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


class SqlAlchemyRepository:
    def __init__(self, session: Session):
        self.session = session

    def add(self, batch: domain.Batch):
        self.session.add(batch)

    def get(self, reference: str) -> domain.Batch:
        return self.session.query(domain.Batch).filter_by(reference=reference).one()

    def list(self) -> list[domain.Batch]:
        return self.session.query(domain.Batch).all()
