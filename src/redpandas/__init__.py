from typing import List

import numpy as np
import pandas as pd

from redis import Redis

__all__ = ['save', 'fetch']


def _encode(data: np.ndarray) -> List[str]:
    # not pickled or compressed for human readability in Redis
    return [data.dtype.str] + list(map(str, data))


def save(client: Redis, identifier: str, df: pd.DataFrame) -> None:
    """Save the given DataFrame to Redis by columns.

    Each column is saved under ``identifier:col_name``.

    The Index is saved under ``identifier:_index``.

    Index and columns are saved as list ``[dtype, element, ...]``.

    Args:
        client (Redis): Redis client.
        identifier (str): Unique identifier of DataFrame.
        df (pd.DataFrame): DataFrame to save.
    """
    pipe = client.pipeline()
    for c in df:
        pipe.rpush(f'{identifier}:{c}', *_encode(df[c].values))
    pipe.rpush(f'{identifier}:_index', *_encode(df.index.values))
    pipe.execute()


def _decode(data: List[bytes]) -> np.ndarray:
    data_str = [x.decode() for x in data]
    return np.array(data_str[1:]).astype(data_str[0])


def fetch(client: Redis, identifier: str, *cols: str, pattern: str = '') -> pd.DataFrame:
    """Fetch queried columns from Redis, and return as a DataFrame.

    Args:
        client (Redis): Redis client.
        identifier (str): Unique identifier of DataFrame.
        cols (str): Static column names to load.
        pattern (str, optional): Glob pattern of column names. Defaults to ''.

    Returns:
        pd.DataFrame: Reassembled DataFrame, sorted by column names.
    """
    static_query = {f'{identifier}:{c}' for c in cols}
    matched_query = {x.decode() for x in client.keys(f'{identifier}:{pattern}')} if pattern else set()
    col_query = sorted(static_query | matched_query)
    pipe = client.pipeline()
    for x in col_query:
        pipe.lrange(x, 0, -1)
    data = [_decode(x) for x in pipe.execute()]
    index = _decode(client.lrange(f'{identifier}:_index', 0, -1))
    prefix_len = len(identifier) + 1
    columns = sorted(set(cols) | {x[prefix_len:] for x in matched_query})
    return pd.DataFrame(zip(*data), index=index, columns=columns)
