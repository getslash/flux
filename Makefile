default: test

test: env
	.venv/bin/pytest tests

.PHONY: doc
doc: env
	.venv/bin/sphinx-build -a -W -E doc build/sphinx/html


env: .env/.up-to-date
	uv venv
	uv pip install -e ".[testing,doc]"
