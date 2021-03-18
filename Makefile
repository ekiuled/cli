.PHONY: run lint test clean clean-pyc clean-test

run:
	python cli

lint:
	python -m pip install flake8
	flake8

test:
	python -m pip install pytest pytest-cov
	pytest --cov=cli

clean: clean-pyc clean-test

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test:
	rm -f .coverage
	rm -fr .pytest_cache
	rm -fr tests/.pytest_cache