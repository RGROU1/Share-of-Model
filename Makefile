.PHONY: setup demo regras teste limpar

setup:
	pip install -e ".[dev]"

demo:
	python -m som demo

regras:
	python -m som regras

teste:
	python -m pytest -q

limpar:
	find . -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache *.egg-info
