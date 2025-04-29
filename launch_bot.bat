@echo off
echo Launching DSV RP Bot...

:: set UTF-8 Encoding
chcp 65001 > nul

:: Go to the bot directory (adjust path if needed)
cd /d D:\SE Modding\DSV Modding\DSV-RP-Bot

:: Activate the virtual environment
call venv\Scripts\activate.bat

:: Launch the bot and log terminal
python RP-Bot.py

:: After bot exits, dump console output to log
echo Copying session output to bot_output.log...
:: Save the full console buffer to a file
(for /f "delims=" %%i in ('type CON') do echo(%%i)) > bot_output.log

:: Keep the window open if the bot crashes
echo Bot has stopped running. Press any key to close this window.
pause > nul
