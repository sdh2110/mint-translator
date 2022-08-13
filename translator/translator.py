import csv

MINT_DATE = 'Date'
MINT_DESC = 'Description'
MINT_ORG_DESC = 'Original Description'
MINT_AMOUNT = 'Amount'
MINT_TRANSACTION_TYPE = 'Transaction Type'
MINT_CATEGORY = 'Category'
MINT_ACCOUNT = 'Account Name'
MINT_LABELS = 'Labels'
MINT_NOTES = 'Notes'

EXPECTED_MINT_HEADERS = [MINT_DATE, MINT_DESC, MINT_ORG_DESC, MINT_AMOUNT, MINT_TRANSACTION_TYPE, MINT_CATEGORY,
                         MINT_ACCOUNT,
                         MINT_LABELS, MINT_NOTES]

AMOUNT = 'Amount'
DATE = 'Date'
FOR_OR_FROM = 'For/From'
METHOD = 'Monetary Method'
OTHER_INFO = 'Other Info'


def load_resources():
    pass


def check_headers(csv_reader):
    if csv_reader.fieldnames != EXPECTED_MINT_HEADERS:
        error_message = 'CSV file headers do not match expected list of headers. Was:\n{}\nExpected:\n{}'.format(
            csv_reader.fieldnames, EXPECTED_MINT_HEADERS)
        raise Exception(error_message)


def translate_from_mint(mint_transaction):
    transaction = dict()

    if mint_transaction[MINT_TRANSACTION_TYPE] == 'debit':
        transaction[AMOUNT] = '-' + mint_transaction[MINT_AMOUNT]
    else:
        transaction[AMOUNT] = mint_transaction[MINT_AMOUNT]

    transaction[DATE] = mint_transaction[MINT_DATE]
    transaction[FOR_OR_FROM] = mint_transaction[MINT_CATEGORY]
    transaction[METHOD] = mint_transaction[MINT_ACCOUNT]
    transaction[OTHER_INFO] = mint_transaction[MINT_NOTES]

    return transaction


def apply_mapping(mapping_function, list_of_data):
    return list(map(mapping_function, list_of_data))


def main():
    with open('../Inbox/transactions.csv', newline='') as transactions_file:
        load_resources()
        transactions_reader = csv.DictReader(transactions_file, delimiter=',')
        check_headers(transactions_reader)

        raw_transactions = list(transactions_reader)
        formatted_transactions = apply_mapping(translate_from_mint, raw_transactions)

        print(formatted_transactions)


if __name__ == "__main__":
    main()
