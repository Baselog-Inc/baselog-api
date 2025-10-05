from typing import Generic, Self, TypeVar, Callable, Protocol

T = TypeVar("T")  # Success type
E = TypeVar("E")  # Error type
U = TypeVar("U")  # Type for mapping
R = TypeVar("R")  # Return type for match function


class Result(Protocol[T, E]):
    def is_ok(self) -> bool: ...
    def is_err(self) -> bool: ...
    def unwrap(self) -> T: ...
    def map(self, f: Callable[[T], U]) -> Self: ...
    def bind(self, f: Callable[[T], Self]) -> Self: ...


class Ok(Result, Generic[T, E]):
    def __init__(self, value: T):
        self.value = value

    def is_ok(self) -> bool:
        return True

    def is_err(self) -> bool:
        return False

    def unwrap(self) -> T:
        return self.value

    def map(self, f: Callable[[T], U]) -> Self:
        try:
            return Ok(f(self.value))
        except Exception as e:
            return Err(e)

    def bind(self, f: Callable[[T], Self]) -> Self:
        try:
            return f(self.value)
        except Exception as e:
            return Err(e)

    def __repr__(self):
        return f"Ok({self.value})"


class Err(Result, Generic[T, E]):
    def __init__(self, error: E):
        self.error = error

    def is_ok(self) -> bool:
        return False

    def is_err(self) -> bool:
        return True

    def unwrap(self) -> T:
        return self.error

    def map(self, f: Callable[[T], U]) -> Self:
        return self  # propagate error

    def bind(self, f: Callable[[T], Self]) -> Self:
        return self  # propagate error

    def __repr__(self):
        return f"Err({self.error})"


def match(result: Result[T, E], *, on_success: Callable[[T], R], on_error: Callable[[E], R]) -> R:
    """
    Functional pattern matching for Result objects.

    Args:
        result: The Result object to match against
        on_success: Function to call for success values
        on_error: Function to call for error values

    Returns:
        The result of calling either on_success or on_error
    """
    if result.is_ok():
        return on_success(result.unwrap())
    else:
        return on_error(result.unwrap())
