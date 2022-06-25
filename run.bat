SET mypath=%~dp0
cd %mypath:~0,-1%
exec "venv\bin\python3.10 main.py"

