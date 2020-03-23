del /S /Q build && pipenv run python setup.py sdist && pipenv run python setup_cx.py bdist bdist_msi && echo OK
