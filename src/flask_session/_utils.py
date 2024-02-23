"""
MIT License

Copyright (c) 2023 giuppep

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import time
from functools import wraps
from typing import Any, Callable

from flask import current_app


def total_seconds(timedelta):
    return int(timedelta.total_seconds())


def retry_query(
    *, max_attempts: int = 3, delay: float = 0.3, backoff: int = 2
) -> Callable[..., Any]:
    """Decorator to retry a query when an OperationalError is raised.

    Args:
        max_attempts: Maximum number of attempts. Defaults to 3.
        delay: Delay between attempts in seconds. Defaults to 0.3.
        backoff: Backoff factor. Defaults to 2.
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                # TODO: use proper exception type
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise e

                    sleep_time = delay * backoff**attempt
                    current_app.logger.exception(
                        f"Exception when querying database ({e})."
                        f"Retrying ({attempt + 1}/{max_attempts}) in {sleep_time:.2f}s."
                    )
                    time.sleep(sleep_time)

        return wrapper

    return decorator
