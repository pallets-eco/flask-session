all: clean-pyc test

test:
	python test_session.py

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

release:
	python -m build
	twine upload dist/*

.PHONY: all test clean-pyc release
