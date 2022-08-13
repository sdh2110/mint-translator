import csv

MINT_DATE = 'Date'
MINT_DESC = 'Description'
MINT_ORG_DESC = 'Original Description'
MINT_AMOUNT = 'Amount'
MINT_TRANS_TYPE = 'Transaction Type'
MINT_CATEGORY = 'Category'
MINT_ACCOUNT = 'Account Name'
MINT_LABELS = 'Labels'
MINT_NOTES = 'Notes'

EXPECTED_MINT_HEADERS = [MINT_DATE, MINT_DESC, MINT_ORG_DESC, MINT_AMOUNT, MINT_TRANS_TYPE, MINT_CATEGORY, MINT_ACCOUNT,
                         MINT_LABELS, MINT_NOTES]


def load_resources():
    pass


def check_headers(csv_reader):
    if csv_reader.fieldnames != EXPECTED_MINT_HEADERS:
        error_message = 'CSV file headers do not match expected list of headers. Was:\n{}\nExpected:\n{}'.format(
            csv_reader.fieldnames, EXPECTED_MINT_HEADERS)
        raise Exception(error_message)


def main():
    with open('../Inbox/march_transactions.csv', newline='') as csv_file:
        load_resources()
        csv_reader = csv.DictReader(csv_file, delimiter=',')
        check_headers(csv_reader)


if __name__ == "__main__":
    main()
