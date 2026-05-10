source venv/bin/activate
ruff check . && mypy . && pytest tests