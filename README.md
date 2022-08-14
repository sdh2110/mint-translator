# mint-translator

## Overview

Converts CSV exports of transactions from Mint into the format used by my personal finances spreadsheet.

## Using the Translator Tool

### Standard Use

To use:

- Python must be installed to `PATH`.
- Export `transactions.csv` from Mint and place in `/Inbox` folder.
- Click on the `_RunTranslator.bat` script to run the translator.
- If everything is successfully translated, the translations will be placed in a `formatted_transactions.csv` file.
- However, if there were any errored transactions found, then those transactions will be displayed in the console along
  with their errors and no transactions will be exported.

### Other Run Commands

In addition to the `_RunTranslator.bat` script, there are three more utility scripts you can use:

- `_ClearALL.bat` - Deletes both the `transactions.csv` file AND all of the output files.
- `_ClearOutputOnly.bat` - Deletes only the output files, leaving the `transactions.csv` file untouched.
- `_RunTranslator(OUTPUT_ERRORS).bat` - Runs the translator like normal, but if there are errors found, it still outputs
  the `formatted_transactions.csv` file in addition to these two error files:
    - Any translations that errored out will be placed in `formatted_transactions(ERRORED).csv` file
    - The raw version of the errored out transactions will be placed in `transactions(ERRORED).csv` file. These
      transactions can be reprocessed through the translator after errors have been resolved by removing the `(ERRORED)`
      text from the title.

### Maintaining the Translator

The files within the `/Inbox/resources` folder are used to convert between the way Mint names items to the way I name
items. This is what each file is for:

- `monetary_accounts.csv` - Lists the names of each Mint monetary on the left that gets converted to my naming on the
  right.
- `categories.csv` - Lists the names of each Mint category on the left that gets converted to my naming on the right.
- `transfer_categories.csv` - A single list of Mint categories that I classify as transfers between one account to
  another.

These resources are intended to be updated as more conversions are found or arise.