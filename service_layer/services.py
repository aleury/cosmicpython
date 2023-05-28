from os import walk

import domain
from adapters.repository import Repository


class InvalidSku(Exception):
    pass


def is_valid_sku(sku: str, batches: list[domain.Batch]) -> bool:
    return sku in {b.sku for b in batches}


def allocate(order_id: str, sku: str, qty: int, repo: Repository, session) -> str:
    batches = repo.list()
    if not is_valid_sku(sku, batches):
        raise InvalidSku(f"Invalid sku {sku}")

    line = domain.OrderLine(order_id, sku, qty)
    batchref = domain.allocate(line, batches)

    session.commit()
    return batchref
