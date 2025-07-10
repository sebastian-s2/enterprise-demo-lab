# Copyright (c) 2024 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the LICENSE file.
from collections import defaultdict
from typing import Any, Generator


def get_indices_of_duplicate_items(values: list) -> Generator[tuple[Any, list[int]], None, None]:
    """
    Returns a Generator of Tuples with (<value>, [<indices of duplicate items>])
    """
    counters = defaultdict(list)
    for index, item in enumerate(values):
        counters[item].append(index)
    return ((value, indices) for value, indices in counters.items() if len(indices) > 1)
