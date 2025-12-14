format:
	uv run ruff check --preview --select I,RUF022 --fix .
	uv run ruff format .

mypy:
	uv run mypy --ignore-missing-imports --explicit-package-bases src tests main.py