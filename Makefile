tests: ## Clean and Make unit tests
	python -m pytest -vvv tornado_sqlalchemy_login/tests/ --cov=tornado_sqlalchemy_login --junitxml=python_junit.xml --cov-report=xml --cov-branch

lint: ## run linter
	python -m flake8 tornado_sqlalchemy_login setup.py

fix:  ## run autopep8/tslint fix
	black tornado_sqlalchemy_login/ setup.py

clean: ## clean the repository
	find . -name "__pycache__" | xargs  rm -rf
	rm -rf .pytest_cache 
	find . -name "*.pyc" | xargs rm -rf 
	rm -rf .coverage cover htmlcov logs build dist *.egg-info
	make -C ./docs clean

docs:  ## make documentation
	make -C ./docs html
	open ./docs/_build/html/index.html

build:  ## build the repository
	python setup.py build

install:  ## install to site-packages
	python -m pip install .

dist:  ## create dists
	rm -rf dist build
	python setup.py sdist bdist_wheel
	python -m twine check dist/*
	
publish: dist  ## dist to pypi
	python -m twine upload dist/* --skip-existing

# Thanks to Francoise at marmelab.com for this
.DEFAULT_GOAL := help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

print-%:
	@echo '$*=$($*)'

.PHONY: clean tests help annotate annotate_l dist docs
