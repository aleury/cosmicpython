import uuid

import pytest
import requests

import config


def random_suffix() -> str:
    return uuid.uuid4().hex[:6]


def random_sku(name: str = "") -> str:
    return f"sku-{name}-{random_suffix()}"


def random_batchref(num: int = 0) -> str:
    return f"batch-{num:05d}-{random_suffix()}"


def random_order_id(num: int = 0) -> str:
    return f"order-{num:05d}-{random_suffix()}"


@pytest.mark.usefixtures("restart_api")
def test_happy_path_returns_201_and_allocated_batch(add_stock):
    sku, othersku = random_sku(), random_sku("other")
    early_batch = random_batchref(1)
    later_batch = random_batchref(2)
    other_batch = random_batchref(3)
    add_stock(
        [
            (later_batch, sku, 100, "2011-01-02"),
            (early_batch, sku, 100, "2011-01-01"),
            (other_batch, othersku, 100, None),
        ]
    )
    data = {"order_id": random_order_id(), "sku": sku, "qty": 3}
    url = config.get_api_url()

    r = requests.post(f"{url}/allocate", json=data)

    assert r.status_code == 201
    assert r.json()["batchref"] == early_batch


@pytest.mark.usefixtures("restart_api")
def test_unhappy_path_returns_400_and_error_message():
    unknown_sku, large_order = random_sku(), random_order_id()
    data = {"order_id": large_order, "sku": unknown_sku, "qty": 20}
    url = config.get_api_url()

    r = requests.post(f"{url}/allocate", json=data)
    assert r.status_code == 400
    assert r.json()["message"] == f"Invalid sku {unknown_sku}"
