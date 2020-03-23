if "%1"=="FAST" goto FAST
:SLOW
call checks.cmd || echo ERROR && exit /b
if exist build rmdir /S /Q build || echo ERROR && exit /b
pipenv run python setup_cx.py bdist bdist_msi || echo ERROR && exit /b
pipenv run python setup.py sdist || echo ERROR && exit /b
build\exe.win-amd64-3.8\pdl2pdf.exe --self-test || echo ERROR && exit /b
goto OK_END
:FAST
rem Don't do any checks and don't build source and MSI distributions - just the EXE in ZIP
if exist build rmdir /S /Q build || echo ERROR && exit /b
pipenv run python setup_cx.py bdist || echo ERROR && exit /b
build\exe.win-amd64-3.8\pdl2pdf.exe --self-test || echo ERROR && exit /b
goto OK_END
:OK_END
echo OK
