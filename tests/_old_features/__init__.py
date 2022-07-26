#!/usr/bin/python3

# __init__.py
# Date:  03/02/2022
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com

""" """


def str2bool(value: str) -> bool:
    """
        Parse a string value and cast it into its boolean value
    :param value:
    :return:
    """
    if value in ["y", "yes", "t", "true", "on", "1"]: return True
    if value in ["n", "no", "f", "false", "off", "0"]: return False
    raise ValueError("boolean value unrecognised")
