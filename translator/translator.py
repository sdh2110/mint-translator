import csv

EXPECTED_HEADERS = []


def load_resources():
    with open('resources/expected_headers.csv', newline='') as headers_file:
        global EXPECTED_HEADERS
        headers_reader = csv.DictReader(headers_file, delimiter=',')
        EXPECTED_HEADERS = headers_reader.fieldnames


def check_headers(csv_reader):
    if csv_reader.fieldnames != EXPECTED_HEADERS:
        error_message = 'CSV file headers do not match expected list of headers. Was:\n{}\nExpected:\n{}'.format(
            csv_reader.fieldnames, EXPECTED_HEADERS)
        raise Exception(error_message)


def main():
    with open('../Inbox/march_transactions.csv', newline='') as csv_file:
        load_resources()
        csv_reader = csv.DictReader(csv_file, delimiter=',')
        check_headers(csv_reader)


if __name__ == "__main__":
    main()
