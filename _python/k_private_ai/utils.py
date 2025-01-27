"""
utils
"""

from typing import Any
from math import isnan


def get_data(data: Any) -> None | Any:
    return (
        None
        if isinstance(data, float) and isnan(data)
        else (data.strip() if isinstance(data, str) else data)
    )
