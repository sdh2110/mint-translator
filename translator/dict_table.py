def _get_column_width(items, headers):
    widths = dict()

    for header in headers:
        max_width = len(header)
        for item in items:
            max_width = max(max_width, len('{}'.format(item[header])))

        widths[header] = max_width

    return widths


def _print_cell(value, width, align_right):
    if align_right:
        align = '>'
    else:
        align = '<'
    print(('{:' + align + str(width) + '}  ').format(value), end='')


def print_table(items, headers, right_aligned_headers):
    column_widths = _get_column_width(items, headers)

    for header in headers:
        _print_cell(header, column_widths[header], False)

    print()

    for item in items:
        for header in headers:
            _print_cell(item[header], column_widths[header], header in right_aligned_headers)
        print()
