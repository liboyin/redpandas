import time
from typing import Any, Callable, Generator
import pytest
from subprocess import PIPE, Popen

import pandas as pd
from redis import Redis
from redis.exceptions import ConnectionError

import redpandas


def start_server(client: Redis, retry: int = 30) -> Popen:
    server = Popen('redis-server --save "" --appendonly no'.split(), stdout=PIPE, stderr=PIPE, close_fds=True)
    for _ in range(retry):
        try:
            if client.ping():
                break
        except ConnectionError:
            time.sleep(1)
    else:  # still cannot connect after 30 seconds
        server.terminate()
        server.wait()
        raise TimeoutError(client)
    return server


@pytest.fixture(scope='module')
def redis_client() -> Generator[Redis, None, None]:
    client = Redis()
    try:
        client.ping()
    except ConnectionError:
        start_server(client)
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
    df = pd._testing.makeDataFrame()
    redpandas.save(redis_client, 'random_df', df)
    _test_fetch_with_df(df, redis_client, 'random_df')


def test_missing_dataframe(redis_client: Redis) -> None:
    df = pd._testing.makeMissingDataframe()
    redpandas.save(redis_client, 'random_missing_df', df)
    _test_fetch_with_df(df, redis_client, 'random_missing_df')


def test_mixed_dataframe(redis_client: Redis) -> None:
    df = pd._testing.makeMixedDataFrame()
    redpandas.save(redis_client, 'random_mixed_df', df)
    _test_fetch_with_df(df, redis_client, 'random_mixed_df')
