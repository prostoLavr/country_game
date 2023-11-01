SET mypath=%~dp0
cd %mypath:~0,-1%
cmd /k "python country_game/main.py"

