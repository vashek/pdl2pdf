if not exist TEST mkdir TEST
pipenv run python setup.py test > TEST/pytest.txt && echo OK
