@ECHO OFF
MODE CON: cols=150, lines=30

python ../translator/translator.py
set save_error=%ERRORLEVEL%

IF exist "formatted_transactions.csv" (
    CLIP < formatted_transactions.csv
)

IF %save_error% NEQ 0 (
    PAUSE
)