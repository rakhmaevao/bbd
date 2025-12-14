format:
	uv run ruff check --preview --select I,RUF022 --fix .
	uv run ruff format .