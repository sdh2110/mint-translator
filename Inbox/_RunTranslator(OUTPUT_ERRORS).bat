MODE 150, 30

python ../translator/translator.py force

IF exist "formatted_transactions.csv (
    CLIP < formatted_transactions.csv
)

IF %ERRORLEVEL% NEQ 0 (
    PAUSE
)