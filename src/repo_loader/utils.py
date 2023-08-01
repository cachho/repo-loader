import string


def is_readable(input_string):
    """
    Heuristic to determine if a string is "readable" (mostly contains printable characters and forms meaningful words)

    :param input_string: string
    :return: True if the string is more than 95% printable.
    """
    try:
        printable_ratio = sum(c in string.printable for c in input_string) / len(
            input_string
        )
    except ZeroDivisionError:
        printable_ratio = 0
    return printable_ratio > 0.95  # 95% of characters are printable
