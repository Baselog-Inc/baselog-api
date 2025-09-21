from typing import Generic, TypeVar, Callable, Union

T = TypeVar("T")
U = TypeVar("U")


class Maybe(Generic[T]):
    def is_some(self) -> bool:
        return isinstance(self, Some)

    def is_nothing(self) -> bool:
        return isinstance(self, Nothing)

    def unwrap(self) -> T:
        if isinstance(self, Some):
            return self.value
        else:
            raise Exception("Tried to unwrap a Nothing")

    def map(self, f: Callable[[T], U]) -> "Maybe[U]":
        if isinstance(self, Some):
            try:
                return Some(f(self.value))
            except Exception:
                return Nothing()
        return self

    def bind(self, f: Callable[[T], "Maybe[U]"]) -> "Maybe[U]":
        if isinstance(self, Some):
            try:
                return f(self.value)
            except Exception:
                return Nothing()
        return self


class Some(Maybe[T]):
    def __init__(self, value: T):
        self.value = value

    def __repr__(self):
        return f"Some({self.value})"


class Nothing(Maybe[T]):
    def __repr__(self):
        return "Nothing()"
