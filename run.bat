SET mypath=%~dp0
cd %mypath:~0,-1%
venv/bin/python3.10 main.py

