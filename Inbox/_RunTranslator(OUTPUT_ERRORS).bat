MODE 150, 30

python ../translator/translator.py force

IF %ERRORLEVEL% NEQ 0 (
    PAUSE
)