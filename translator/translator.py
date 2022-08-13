import csv
import pprint

import unidecode

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
MONETARY_METHOD = 'Monetary Method'
OTHER_INFO = 'Other Info'

ERROR = '_ERROR'

TRANSFER_CATEGORIES = []
CATEGORY_IDX = dict()
MONETARY_IDX = dict()


def load_mapping_index(index_filename, index_map):
    with open('./resources/{}'.format(index_filename), newline='') as index_file:
        index_reader = csv.reader(index_file, delimiter='>')
        for mapping in index_reader:
            index_map[mapping[0]] = mapping[1]


def load_resources():
    global TRANSFER_CATEGORIES
    with open('resources/transfer_categories.csv', newline='') as transfer_file:
        TRANSFER_CATEGORIES = list(csv.reader(transfer_file, delimiter=','))[0]

    load_mapping_index('categories.csv', CATEGORY_IDX)
    load_mapping_index('monetary_accounts.csv', MONETARY_IDX)


def read_transactions():
    with open('../Inbox/transactions.csv', newline='') as transactions_file:
        transactions_reader = csv.DictReader(transactions_file, delimiter=',')
        check_headers(transactions_reader)
        return list(transactions_reader)


def check_headers(csv_reader):
    if csv_reader.fieldnames != EXPECTED_MINT_HEADERS:
        error_message = 'CSV file headers do not match expected list of headers. Was:\n{}\nExpected:\n{}'.format(
            csv_reader.fieldnames, EXPECTED_MINT_HEADERS)
        raise Exception(error_message)


def error_out_transaction(transaction, error_message):
    if ERROR not in transaction:
        transaction[ERROR] = error_message
    else:
        transaction[ERROR] += ' | ' + error_message


def translate_from_mint(mint_transaction):
    transaction = dict()

    # Set simple fields
    transaction[DATE] = mint_transaction[MINT_DATE]
    transaction[OTHER_INFO] = mint_transaction[MINT_NOTES]

    # Set amount
    if mint_transaction[MINT_TRANSACTION_TYPE] == 'debit':
        transaction[AMOUNT] = '-' + mint_transaction[MINT_AMOUNT]
    else:
        transaction[AMOUNT] = mint_transaction[MINT_AMOUNT]

    # Set for/from
    if mint_transaction[MINT_CATEGORY] in TRANSFER_CATEGORIES:
        transaction[FOR_OR_FROM] = mint_transaction[MINT_CATEGORY]
    else:
        if mint_transaction[MINT_CATEGORY] in CATEGORY_IDX:
            transaction[FOR_OR_FROM] = CATEGORY_IDX[mint_transaction[MINT_CATEGORY]]
        else:
            transaction[FOR_OR_FROM] = mint_transaction[MINT_CATEGORY]
            error_out_transaction(transaction, 'Unknown category of for/from')

    # Set monetary method
    mint_account = unidecode.unidecode(mint_transaction[MINT_ACCOUNT])
    if mint_account in MONETARY_IDX:
        transaction[MONETARY_METHOD] = MONETARY_IDX[mint_account]
    else:
        transaction[MONETARY_METHOD] = mint_account
        error_out_transaction(transaction, 'Unknown monetary method')

    return transaction


def apply_mapping(mapping_function, list_of_data):
    return list(map(mapping_function, list_of_data))


def sort_transactions(transactions, raw_transactions):
    good_transactions = []
    errored_transactions = []
    raw_errored_transactions = []

    for index, transaction in enumerate(transactions):
        if ERROR not in transaction:
            good_transactions.append(transaction)
        else:
            errored_transactions.append(transaction)
            raw_errored_transactions.append(raw_transactions[index])

    return good_transactions, errored_transactions, raw_errored_transactions


def main():
    load_resources()

    raw_transactions = read_transactions()
    formatted_transactions = apply_mapping(translate_from_mint, raw_transactions)

    (good_transactions, errored_transactions, raw_errored_transactions) = sort_transactions(formatted_transactions,
                                                                                            raw_transactions)

    print('Processed {} transactions.'.format(len(formatted_transactions)))
    if len(errored_transactions) > 0:
        print('\nWARNING: {} of the transactions contained errors. Errored transactions:\n'.format(
            len(errored_transactions)))
        pprint.pprint(errored_transactions)


if __name__ == "__main__":
    main()
