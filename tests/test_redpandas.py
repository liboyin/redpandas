import time
from typing import Any, Callable, Generator
import pytest

import pandas as pd
from redis import Redis

import redpandas


@pytest.fixture(scope='module')
def redis_client() -> Generator[Redis, None, None]:
    import subprocess
    subprocess.Popen('redis-server --save "" --appendonly no'.split(), close_fds=True)
    time.sleep(1)
    client = Redis()
    try:
        yield client
    finally:
        client.shutdown()


def _test_fetch(ref_df: pd.DataFrame, fetch: Callable[[Any], pd.DataFrame], *cols: str, pattern: str = '') -> None:
    df_out = fetch(*cols, pattern=pattern)  # type: ignore
    pd.testing.assert_frame_equal(df_out, ref_df)


def _test_fetch_with_df(df: pd.DataFrame, redis_client: Redis, identifier: str) -> None:
    from functools import partial
    fetch = partial(redpandas.fetch, redis_client, identifier)
    _test_fetch(df[['A']], fetch, 'A')
    _test_fetch(df[['A', 'B']], fetch, 'A', 'B')
    _test_fetch(df, fetch, 'A', 'B', 'C', 'D')
    _test_fetch(df[['A']], fetch, pattern='A')
    _test_fetch(df[['A', 'B']], fetch, pattern='[AB]')
    _test_fetch(df, fetch, pattern='?')
    _test_fetch(df[['A', 'B']], fetch, 'B', pattern='A')
    _test_fetch(df, fetch, 'A', 'B', pattern='[B-D]')


def test_random_dataframe(redis_client: Redis) -> None:
    df = pd.util.testing.makeDataFrame()
    redpandas.save(redis_client, 'random_df', df)
    _test_fetch_with_df(df, redis_client, 'random_df')


def test_missing_dataframe(redis_client: Redis) -> None:
    df = pd.util.testing.makeMissingDataframe()
    redpandas.save(redis_client, 'random_missing_df', df)
    _test_fetch_with_df(df, redis_client, 'random_missing_df')


def test_mixed_dataframe(redis_client: Redis) -> None:
    df = pd.util.testing.makeMixedDataFrame()
    redpandas.save(redis_client, 'random_mixed_df', df)
    _test_fetch_with_df(df, redis_client, 'random_mixed_df')
