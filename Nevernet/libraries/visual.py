import colorama
from colorama import Fore, Back, Style

def ascii_table(headers, data):
    # Determine the maximum length of each column
    max_lengths = [len(header) for header in headers]
    for row in data:
        for i, value in enumerate(row):
            max_lengths[i] = max(max_lengths[i], len(str(value)))
    # Build the table string
    table = ''
    header_row = '┌'
    for i, header in enumerate(headers):
        header_row += '─' * (max_lengths[i] + 2) + '┬' if i < len(headers) - 1 else '─' * (max_lengths[i] + 2) + '┐'
    table += header_row + '\n'
    header_row = '│'
    for i, header in enumerate(headers):
        header_row += ' {} │'.format(header.ljust(max_lengths[i]))
    table += header_row + '\n'
    horizontal_line = '├'
    for i, length in enumerate(max_lengths):
        horizontal_line += '─' * (length + 2) + '┼' if i < len(max_lengths) - 1 else '─' * (length + 2) + '┤'
    table += horizontal_line + '\n'
    
    for i, row in enumerate(data):

        if i % 2 == 0:
            data_row = f'{Fore.YELLOW}│{Fore.RESET}'
        else:
            data_row = f'│{Fore.RESET}'

        for j, value in enumerate(row):
            if i % 2 == 0:
                data_row += f' {str(value).ljust(max_lengths[j])} {Fore.YELLOW}│{Fore.RESET}'
            else:
                data_row += f' {str(value).ljust(max_lengths[j])} │{Fore.RESET}'


        if i % 2 == 0:
            table += Fore.BLACK + Back.YELLOW + data_row + Style.RESET_ALL + '\n'
        else:
            table += data_row + '\n'

    bottom_line = '└'
    for i, length in enumerate(max_lengths):
        bottom_line += '─' * (length + 2) + '┴' if i < len(max_lengths) - 1 else '─' * (length + 2) + '┘'
    table += bottom_line
    return table