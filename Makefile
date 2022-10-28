default: test

test: env
	.env/bin/pytest tests

.PHONY: doc
doc: env
	.env/bin/sphinx-build -a -W -E doc build/sphinx/html


env: .env/.up-to-date

.env/.up-to-date: pyproject.toml Makefile
	python3 -m venv .env
	.env/bin/pip install -e .[testing,doc]
	touch $@

