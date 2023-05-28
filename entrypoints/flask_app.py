from flask import Flask, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import config
import domain
from adapters import orm, repository
from service_layer import services

orm.start_mappers()
get_session = sessionmaker(bind=create_engine(config.get_postgres_uri()))

app = Flask(__name__)


@app.route("/allocate", methods=["POST"])
def allocate_endpoint():
    json = request.get_json()

    session = get_session()
    batch_repo = repository.SqlAlchemyRepository(session)
    line = domain.OrderLine(
        json["order_id"],
        json["sku"],
        json["qty"],
    )

    try:
        batchref = services.allocate(line, batch_repo, session)
    except (domain.OutOfStock, services.InvalidSku) as e:
        return {"message": str(e)}, 400

    return {"batchref": batchref}, 201
