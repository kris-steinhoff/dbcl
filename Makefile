lint: pylint black bandit

pylint:
	poetry run pylint dbcl

black:
	poetry run black --check .

bandit:
	poetry run bandit -r dbcl
