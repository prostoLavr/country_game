SET mypath=%~dp0
cd %mypath:~0,-1%
cmd /k "venv\bin\activate & python main.py"

