"""Custom exceptions for the application."""

from __future__ import annotations


class NovelNotFoundError(Exception):
    pass


class InvalidFileError(Exception):
    def __init__(self, message: str, code: str = "INVALID_FILE"):
        self.message = message
        self.code = code
        super().__init__(message)


class ProcessingError(Exception):
    pass


__all__ = ["NovelNotFoundError", "InvalidFileError", "ProcessingError"]

