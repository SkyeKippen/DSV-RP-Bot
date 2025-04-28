@echo off
echo Launching DSV RP Bot...

:: Go to the bot directory (adjust path if needed)
cd /d D:\SE Modding\DSV Modding\DSV-RP-Bot

:: Activate the virtual environment
call venv\Scripts\activate.bat

:: Launch the bot
python RP-Bot.py

:: Keep the window open if the bot crashes
echo Bot has stopped running. Press any key to close this window.
pause > nul
