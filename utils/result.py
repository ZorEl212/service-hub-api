from typing import Any, Generic, Optional, TypeVar

T = TypeVar("T")


class Result(Generic[T]):
    """A class to handle operation results with success/failure states"""

    def __init__(
        self,
        success: bool,
        value: Optional[T] = None,
        exception_case: Optional[Exception] = None,
    ):
        self.success = success
        self.value = value
        self.exception_case = exception_case

    @classmethod
    def success(cls, value: T) -> "Result[T]":
        """Create a successful result with a value"""
        return cls(True, value=value)

    @classmethod
    def failure(cls, exception: Exception) -> "Result[T]":
        """Create a failed result with an exception"""
        return cls(False, exception_case=exception)

    def __bool__(self) -> bool:
        """Allow using Result in boolean contexts"""
        return self.success
