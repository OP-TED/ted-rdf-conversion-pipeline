from itertools import chain, islice
from typing import Iterable


def chunks(iterable: Iterable, chunk_size: int):
    """
    This function split in chunks a iterable structure based on chunk_size parameter.
    :param iterable:
    :param chunk_size:
    :return:
    """
    iterator = iter(iterable)
    for first in iterator:
        yield chain([first], islice(iterator, chunk_size - 1))
