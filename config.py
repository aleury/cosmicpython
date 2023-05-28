import os


def get_api_url() -> str:
    host = os.environ.get("API_HOST", "localhost")
    port = 5000 if host == "localhost" else 80
    return f"http://{host}:{port}"


def get_postgres_uri():
    host = os.environ.get("DB_HOST", "localhost")
    user = os.environ.get("DB_USER", "postgres")
    password = os.environ.get("DB_PASSWORD", "")
    db_name = os.environ.get("DB_NAME", "allocation")
    return f"postgresql://{user}:{password}@{host}:5432/{db_name}"
