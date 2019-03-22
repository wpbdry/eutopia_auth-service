import re


def is_valid_email(address):
    return re.match(r"[^@]+@[^@]+\.[^@]+", address)
