import time
from pathlib import Path

import pytest
import requests
from requests.exceptions import ConnectionError
from sqlalchemy import Connection, Engine, create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import clear_mappers, sessionmaker

import config
from adapters import orm


@pytest.fixture
def in_memory_db():
    engine = create_engine("sqlite:///:memory:")
    orm.metadata.create_all(engine)
    return engine


@pytest.fixture
def session(in_memory_db):
    orm.start_mappers()
    yield sessionmaker(bind=in_memory_db)()
    clear_mappers()


def wait_for_postgres_to_come_up(engine: Engine) -> Connection:
    deadline = time.time() + 10
    while time.time() < deadline:
        try:
            return engine.connect()
        except OperationalError:
            time.sleep(0.5)
    pytest.fail("postgres never came up")


def wait_for_webapp_to_come_up():
    deadline = time.time() + 10
    url = config.get_api_url()
    while time.time() < deadline:
        try:
            return requests.get(url)
        except ConnectionError:
            time.sleep(0.5)
    pytest.fail("API never came up")


@pytest.fixture
def postgres_db():
    engine = create_engine(config.get_postgres_uri())
    wait_for_postgres_to_come_up(engine)
    orm.metadata.create_all(engine)
    return engine


@pytest.fixture
def postgres_session(postgres_db):
    orm.start_mappers()
    yield sessionmaker(bind=postgres_db)()
    clear_mappers()


@pytest.fixture
def add_stock(postgres_session):
    batches_added = set()
    skus_added = set()

    def _add_stock(lines):
        for ref, sku, qty, eta in lines:
            postgres_session.execute(
                text(
                    "INSERT INTO batches (reference, sku, _purchased_quantity, eta) "
                    "VALUES (:ref, :sku, :qty, :eta)"
                ),
                dict(ref=ref, sku=sku, qty=qty, eta=eta),
            )
            [[batch_id]] = postgres_session.execute(
                text("SELECT id FROM batches WHERE reference=:ref AND sku=:sku"),
                dict(ref=ref, sku=sku),
            )
            batches_added.add(batch_id)
            skus_added.add(sku)
        postgres_session.commit()

    yield _add_stock

    for batch_id in batches_added:
        postgres_session.execute(
            text("DELETE FROM allocations WHERE batch_id=:batch_id"),
            dict(batch_id=batch_id),
        )
        postgres_session.execute(
            text("DELETE FROM batches WHERE id=:batch_id"),
            dict(batch_id=batch_id),
        )
    for sku in skus_added:
        postgres_session.execute(
            text("DELETE FROM order_lines WHERE sku=:sku"),
            dict(sku=sku),
        )


@pytest.fixture
def restart_api():
    time.sleep(0.5)
    wait_for_webapp_to_come_up()
