run:
	flask run --host=0.0.0.0 --port=5000


reset:
	dropdb allocation
	createdb allocation


test: reset
	pytest tests/
