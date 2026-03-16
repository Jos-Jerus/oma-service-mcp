"""Exception handling utilities for the Migration Planner client."""

from typing import Callable, TypeVar, ParamSpec, Awaitable
from functools import wraps

import httpx
from oma_service_mcp.src.logger import log


class MigrationPlannerAPIError(Exception):
    """Exception for Migration Planner API errors."""


P = ParamSpec("P")
T = TypeVar("T")


def sanitize_exceptions(func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
    """Decorate a function to sanitize exceptions from API calls.

    Catches httpx errors and wraps them in MigrationPlannerAPIError with
    sanitized messages. For 4xx status codes, includes the response body
    for detailed error information.

    Returns:
        Decorated function that catches and sanitizes exceptions.
    """

    @wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        operation_name = func.__name__
        try:
            return await func(*args, **kwargs)
        except httpx.HTTPStatusError as e:
            log.error(
                "API error during %s: Status: %s, Body: %s",
                operation_name,
                e.response.status_code,
                e.response.text,
            )
            error_msg = f"API error: Status {e.response.status_code}"
            if 400 <= e.response.status_code <= 499:
                error_msg += f", Details: {e.response.text}"
            raise MigrationPlannerAPIError(error_msg) from e
        except httpx.RequestError as e:
            log.error("Request error during %s: %s", operation_name, str(e))
            raise MigrationPlannerAPIError(
                f"Request failed for {operation_name}: {e}"
            ) from e
        except Exception as e:
            log.error("Unexpected error during %s: %s", operation_name, str(e))
            raise MigrationPlannerAPIError("An internal error occurred") from e

    return wrapper
