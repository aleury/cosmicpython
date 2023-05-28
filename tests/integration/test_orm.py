from sqlalchemy.sql import text

import domain


def test_orderline_mapper_can_load_lines(session):
    session.execute(
        text(
            "INSERT INTO order_lines (order_id, sku, qty) VALUES "
            '("order1", "RED-CHAIR", 12),'
            '("order2", "RED-TABLE", 13),'
            '("order3", "BLUE-LIPSTICK", 14)'
        )
    )
    expected = [
        domain.OrderLine("order1", "RED-CHAIR", 12),
        domain.OrderLine("order2", "RED-TABLE", 13),
        domain.OrderLine("order3", "BLUE-LIPSTICK", 14),
    ]
    assert session.query(domain.OrderLine).all() == expected


def test_orderline_mapper_can_save_lines(session):
    new_line = domain.OrderLine("order1", "DECORATIVE-WIDGET", 12)
    session.add(new_line)
    session.commit()

    rows = list(session.execute(text('SELECT order_id, sku, qty FROM "order_lines"')))
    assert rows == [("order1", "DECORATIVE-WIDGET", 12)]
