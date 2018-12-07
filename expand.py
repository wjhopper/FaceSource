from pandas import DataFrame, concat
from itertools import product


def expand_grid(factors):
    rows = product(*factors.values())
    return DataFrame.from_records(rows, columns=factors.keys())


def replicate(df, n, **args):
    return concat([df]*n, **args)