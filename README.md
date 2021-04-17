# Redpandas

![Build Status](https://github.com/liboyin/redpandas/workflows/tests/badge.svg)

`Redpandas` solves a small problem: caching a `DataFrame` to Redis, and querying a subset of columns.

This is achieved by storing the `DataFrame` by columns, and re-assembling the `DataFrame` at query time.

A use case is when the entire `DataFrame` is expensive to load, but only a few columns are needed at a time.

`Redpandas` has some strong limitations:

- Single layer column, where order is not important
- Single layer index
- Each `DataFrame` can be uniquely identified with a tag
- Frequency and period in index do not work
