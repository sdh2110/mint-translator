# mint-translator

Converts CSV exports of transactions from Mint into the format used by my personal finances spreadsheet.

To use:

- Python must be installed to `PATH`.
- Export `transactions.csv` from Mint and place in `/Inbox` folder.
- Click on the `RunTranslator.bat` script to run the translator.
- Results will be output as follows:
    - The translated transactions will be placed in a `formatted_transactions.csv` file
    - Any translations that errored out will be placed in `formatted_translations(ERRORED).csv` file
    - The raw version of the errored out transactions will be placed in `transactions(ERRORED).csv` file. These
      transactions can be reprocessed through the translator after errors have been resolved by removing the `(ERRORED)`
      text from the title.