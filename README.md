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

The files within the `/Inbox/resources` folder are used to convert between the way Mint names items to the way I
name items. This is what each file is for:

- `monetary_accounts.csv` - Lists the names of each Mint monetary on the left that gets converted to my naming on the right.
- `categories.csv` - Lists the names of each Mint category on the left that gets converted to my naming on the right.
- `transfer_categories.csv` - A single list of Mint categories that I classify as transfers between one account to another.