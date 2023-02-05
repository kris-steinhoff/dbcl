lint: pylint black

pylint:
	poetry run pylint dbcl

black:
	poetry run black .
