import csv
import sys
from datetime import datetime

import unidecode

from dict_table import print_table

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
                         MINT_ACCOUNT, MINT_LABELS, MINT_NOTES]

AMOUNT = 'Amount'
DATE = 'Date'
FOR_OR_FROM = 'For/From'
MONETARY_METHOD = 'Monetary Method'
OTHER_INFO = 'Other Info'

OUTPUT_HEADERS = [AMOUNT, DATE, FOR_OR_FROM, MONETARY_METHOD, OTHER_INFO]

ERROR = '_ERROR'
ORIGINAL_INDEX = '_INDEX'

OUTPUT_HEADERS_WITH_ERROR = [AMOUNT, DATE, FOR_OR_FROM, MONETARY_METHOD, OTHER_INFO, ERROR, ORIGINAL_INDEX]
ERROR_PRINT_HEADERS = [AMOUNT, DATE, FOR_OR_FROM, MONETARY_METHOD, ERROR, ORIGINAL_INDEX]
RIGHT_ALIGNED_HEADERS = [AMOUNT, ORIGINAL_INDEX]

TRANSFER_CATEGORIES = []
INVERTED_CATEGORIES = []
BONUS_CATEGORIES = []
CATEGORY_IDX = dict()
MONETARY_IDX = dict()
WARNING_PATTERNS = []

WARNING_PATTERN_HEADERS = [AMOUNT, DATE, FOR_OR_FROM, MONETARY_METHOD, OTHER_INFO, ERROR]

DATE_FORMAT = '%m/%d/%Y'
TRANSFER_RANGE = 1  # Transfers can only be merged if they are within 1 day of each other


def load_single_line_csv_list(filename, list_to_load):
    with open('resources/{}'.format(filename), newline='') as list_file:
        list_to_load.extend(list(csv.reader(list_file, delimiter=','))[0])


def load_mapping_index(index_filename, index_map):
    with open('./resources/{}'.format(index_filename), newline='') as index_file:
        index_reader = csv.reader(index_file, delimiter=',')
        for mapping in index_reader:
            index_map[mapping[0]] = mapping[1]


def load_resources():
    load_single_line_csv_list('transfer_categories.csv', TRANSFER_CATEGORIES)
    load_single_line_csv_list('inverted_categories.csv', INVERTED_CATEGORIES)
    load_single_line_csv_list('bonus_categories.csv', BONUS_CATEGORIES)

    load_mapping_index('categories.csv', CATEGORY_IDX)
    load_mapping_index('monetary_accounts.csv', MONETARY_IDX)

    global WARNING_PATTERNS
    with open('resources/warning_patterns.csv', newline='') as warnings_file:
        WARNING_PATTERNS = list(csv.DictReader(warnings_file, delimiter=','))


def read_transactions():
    with open('transactions.csv', newline='') as transactions_file:
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


def translate_from_mint(mint_transaction, index):
    transaction = dict()

    # Set simple fields
    transaction[DATE] = mint_transaction[MINT_DATE]
    transaction[OTHER_INFO] = mint_transaction[MINT_NOTES]
    transaction[ORIGINAL_INDEX] = index

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


def translate_all_from_mint(raw_transactions):
    return [translate_from_mint(raw_transaction, index) for index, raw_transaction in enumerate(raw_transactions)]


def are_two_transfers_paired(transfer1, transfer2):
    if float(transfer1[AMOUNT]) + float(transfer2[AMOUNT]) == 0:
        date1 = datetime.strptime(transfer1[DATE], DATE_FORMAT)
        date2 = datetime.strptime(transfer2[DATE], DATE_FORMAT)
        return abs((date2 - date1).days) <= TRANSFER_RANGE
    else:
        return False


def merge_two_transfers(transfer1, transfer2):
    if float(transfer1[AMOUNT]) < 0:
        primary, secondary = transfer1, transfer2
    else:
        primary, secondary = transfer2, transfer1

    primary[FOR_OR_FROM] = secondary[MONETARY_METHOD]

    if ERROR in secondary:
        error_out_transaction(primary, '[From merged transaction (index={}): {}]'.format(secondary[ORIGINAL_INDEX],
                                                                                         secondary[ERROR]))

    return primary


def combine_all_transfers(formatted_transactions):
    normalized_transactions = []
    transfers = []

    for transaction in formatted_transactions:
        if transaction[FOR_OR_FROM] in TRANSFER_CATEGORIES:
            transfers.append(transaction)
        else:
            normalized_transactions.append(transaction)

    while len(transfers) > 0:
        next_transfer = transfers.pop()
        matching_transfer = None

        for index, other_transfer in enumerate(transfers):
            if are_two_transfers_paired(next_transfer, other_transfer):
                transfers.pop(index)
                matching_transfer = other_transfer
                break

        if matching_transfer is None:
            error_out_transaction(next_transfer, 'No matching transfer found')
            normalized_transactions.append(next_transfer)
        else:
            normalized_transactions.append(merge_two_transfers(next_transfer, matching_transfer))

    normalized_transactions.sort(key=lambda transaction: transaction[ORIGINAL_INDEX])
    return normalized_transactions


def invert_amount_for(transaction):
    transaction[AMOUNT] = str(0 - float(transaction[AMOUNT]))


def invert_amounts_for_specific_categories(transactions):
    for transaction in transactions:
        if transaction[FOR_OR_FROM] in INVERTED_CATEGORIES:
            invert_amount_for(transaction)


def split_bonuses(transactions):
    transactions_with_bonuses = []

    for transaction in transactions:
        if transaction[FOR_OR_FROM] in BONUS_CATEGORIES:
            bonus = transaction.copy()
            bonus[FOR_OR_FROM] = 'bonus - {}'.format(bonus[FOR_OR_FROM])
            invert_amount_for(bonus)
            transactions_with_bonuses.append(bonus)

        transactions_with_bonuses.append(transaction)

    return transactions_with_bonuses


def is_errored_transaction_only_warning(errored_transaction):
    for warning_pattern in WARNING_PATTERNS:
        still_matches_pattern = True

        for header in WARNING_PATTERN_HEADERS:
            if warning_pattern[header] != '' and errored_transaction[header] != warning_pattern[header]:
                still_matches_pattern = False
                break

        if still_matches_pattern:
            return True

    return False


def sort_transactions(transactions, raw_transactions):
    good_transactions = []
    warning_transactions = []
    errored_transactions = []
    raw_errored_transactions = []

    for transaction in transactions:
        if ERROR not in transaction:
            good_transactions.append(transaction)
        else:
            if is_errored_transaction_only_warning(transaction):
                good_transactions.append(transaction)
                warning_transactions.append(transaction)
            else:
                errored_transactions.append(transaction)
                raw_errored_transactions.append(raw_transactions[transaction[ORIGINAL_INDEX]])

    return good_transactions, warning_transactions, errored_transactions, raw_errored_transactions


def export_transactions(transactions, headers, filename, output_enabled):
    if output_enabled:
        with open(filename, 'w', newline='') as output_file:
            output_writer = csv.DictWriter(output_file, fieldnames=headers, extrasaction='ignore')
            output_writer.writeheader()
            output_writer.writerows(transactions)


def main(force_output):
    load_resources()

    raw_transactions = read_transactions()
    formatted_transactions = translate_all_from_mint(raw_transactions)
    transactions_with_transfers = combine_all_transfers(formatted_transactions)
    invert_amounts_for_specific_categories(transactions_with_transfers)
    transactions_with_bonuses = split_bonuses(transactions_with_transfers)

    (good_transactions, warning_transactions, errored_transactions, raw_errored_transactions) = sort_transactions(
        transactions_with_bonuses,
        raw_transactions)

    processed_count = len(raw_transactions)
    warning_count = len(warning_transactions)
    error_count = len(errored_transactions)
    output_enabled = force_output or error_count == 0

    print('Processed {} transactions.'.format(processed_count))
    export_transactions(good_transactions, OUTPUT_HEADERS, 'formatted_transactions.csv', output_enabled)

    if warning_count > 0:
        print('\nWARNING: {} of the transactions contained warnings:\n'.format(warning_count))
        print_table(warning_transactions, ERROR_PRINT_HEADERS, RIGHT_ALIGNED_HEADERS)

    if error_count > 0:
        print('\nERROR: {} of the transactions contained errors. Errored transactions:\n'.format(error_count))
        print_table(errored_transactions, ERROR_PRINT_HEADERS, RIGHT_ALIGNED_HEADERS)
        export_transactions(errored_transactions, OUTPUT_HEADERS_WITH_ERROR, 'formatted_transactions(ERRORED).csv',
                            output_enabled)
        export_transactions(raw_errored_transactions, EXPECTED_MINT_HEADERS, 'transactions(ERRORED).csv',
                            output_enabled)

    if warning_count + error_count > 0:
        print()
        sys.exit(
            'Errors were found in {} transactions and warnings were found in {}'.format(error_count, warning_count))


if __name__ == "__main__":
    main('force' in sys.argv)
