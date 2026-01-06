@echo off
cd /d %~dp0

title Checking for Python Installation...
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo You do not have Python installed on you system.
    echo Go to https://www.python.org/downloads and install the latest avaliable version.
    pause > 3
    goto ERROR
)

title Checking libaries
echo Checking for 'customtkinter' (1/4)
python -c "import customtkinter" > nul 2>&1
if %errorlevel% neq 0 (
    echo Installing customtkinter...
    python -m pip install customtkinter > nul
)

echo Checking 'pillow' (2/4)
python -c "import PIL" > nul 2>&1
if %errorlevel% neq 0 (
    echo Installing pillow...
    python -m pip install pillow > nul
)

echo Checking 'pyaes' (3/4)
python -c "import pyaes" > nul 2>&1
if %errorlevel% neq 0 (
    echo Installing pyaes...
    python -m pip install pyaesm > nul
)

echo Checking 'urllib3' (4/4)
python -c "import urllib3" > nul 2>&1
if %errorlevel% neq 0 (
    echo Installing urllib3...
    python -m pip install urllib3 > nul
)

cls
title Starter builder...
python gui.py
if %errorlevel% neq 0 goto ERROR
exit

:ERROR
title [ERROR]
color 4
echo Error trying trying to run the builder make sure you have these:
echo (1) Python installed.
echo (2) The gui.py file on your system.
pause > nul
