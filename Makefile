tests: ## Clean and Make unit tests
	python3 -m pytest -vvv tornado_sqlalchemy_login/tests/ --cov=tornado_sqlalchemy_login

annotate: ## MyPy type annotation check
	mypy -s tornado_sqlalchemy_login  

annotate_l: ## MyPy type annotation check - count only
	mypy -s tornado_sqlalchemy_login | wc -l 

lint: ## run linter
	python3 -m flake8 tornado_sqlalchemy_login

fix:  ## run autopep8/tslint fix
	autopep8 --in-place -r -a -a tornado_sqlalchemy_login/

clean: ## clean the repository
	find . -name "__pycache__" | xargs  rm -rf
	rm -rf .pytest_cache 
	find . -name "*.pyc" | xargs rm -rf 
	rm -rf .coverage cover htmlcov logs build dist *.egg-info

build:  ## build the repository
	python3 setup.py build

install:  ## install to site-packages
	python3 -m pip install .

dist:  ## dist to pypi
	rm -rf dist build
	python3 setup.py sdist
	python3 setup.py bdist_wheel
	twine check dist/* && twine upload dist/*

# Thanks to Francoise at marmelab.com for this
.DEFAULT_GOAL := help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

print-%:
	@echo '$*=$($*)'

.PHONY: clean tests help annotate annotate_l dist
