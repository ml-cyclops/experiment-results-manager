.PHONY: dev
dev:
	pip install -qU pip
	poetry config virtualenvs.in-project true
	python -m venv .venv
	poetry install --no-root
	poetry run pre-commit install
	poetry run pre-commit run -a

.PHONY: fmt
fmt:
	poetry run pre-commit run -a

.PHONY: install_python
install_python:
	CONFIGURE_OPTS=--enable-shared pyenv install $$(cat .python_version | tr -d '\n')
