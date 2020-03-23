mkdir TEST
pipenv run mypy --show-error-codes pdl2pdf.py > TEST/mypy.txt && pipenv run python setup.py test > TEST/pytest.txt && echo OK
