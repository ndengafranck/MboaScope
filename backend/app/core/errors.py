"""Domain errors the API turns into clean HTTP responses. Owner: Developer A."""
from __future__ import annotations


class MboaScopeError(Exception):
    """Base class. `status_code` is the HTTP status the API returns."""

    status_code = 400

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class RegionNotFound(MboaScopeError):
    status_code = 404


class NoDataForRegion(MboaScopeError):
    """The region exists but nothing has been ingested for it yet."""

    status_code = 409


class InvalidPeriod(MboaScopeError):
    status_code = 422


class NotEnoughYears(MboaScopeError):
    status_code = 422
