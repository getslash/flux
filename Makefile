default: test

test: env
	.env/bin/py.test tests

.PHONY: doc
doc: env
	.env/bin/python setup.py build_sphinx -a -E


env: .env/.up-to-date

.env/.up-to-date: setup.py Makefile
	python -m virtualenv .env
	.env/bin/pip install -e .
	.env/bin/pip install Sphinx
	.env/bin/python scripts/test_setup.py
	touch $@

