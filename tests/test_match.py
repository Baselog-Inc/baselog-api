#!/usr/bin/env python3
"""
Test script for the match function implementation.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.result import Ok, Err, match


def test_basic_success():
    """Test basic success case with numeric values."""
    result = Ok(42)
    value = match(
        result,
        on_success=lambda x: x * 2,
        on_error=lambda e: 0
    )
    assert value == 84, f"Expected 84, got {value}"


def test_basic_error():
    """Test basic error case with string errors."""
    result = Err("Not found")
    value = match(
        result,
        on_success=lambda x: x * 2,
        on_error=lambda e: 0
    )
    assert value == 0, f"Expected 0, got {value}"


def test_type_specific_handling():
    """Test type-specific handling with custom functions."""
    # Test success with string
    result = Ok("data")
    result_str = match(
        result,
        on_success=lambda r: f"Success: {r}",
        on_error=lambda e: f"Error: {e}"
    )
    assert result_str == "Success: data", f"Expected 'Success: data', got {result_str}"

    # Test error with string
    result = Err("error message")
    result_str = match(
        result,
        on_success=lambda r: f"Success: {r}",
        on_error=lambda e: f"Error: {e}"
    )
    assert result_str == "Error: error message", f"Expected 'Error: error message', got {result_str}"


def test_different_return_types():
    """Test functions that return different types."""
    result = Ok(42)
    value = match(
        result,
        on_success=lambda x: str(x),
        on_error=lambda e: None
    )
    assert value == "42", f"Expected '42', got {value}"
    assert isinstance(value, str), f"Expected str, got {type(value)}"

    result = Err("error")
    value = match(
        result,
        on_success=lambda x: str(x),
        on_error=lambda e: None
    )
    assert value is None, f"Expected None, got {value}"


def test_edge_cases():
    """Test edge cases with None values."""
    # Test with None success
    result = Ok(None)
    value = match(
        result,
        on_success=lambda x: "None handled" if x is None else "Not none",
        on_error=lambda e: "Error"
    )
    assert value == "None handled", f"Expected 'None handled', got {value}"

    # Test with None error
    result = Err(None)
    value = match(
        result,
        on_success=lambda x: "Success",
        on_error=lambda e: "None error" if e is None else "Not none error"
    )
    assert value == "None error", f"Expected 'None error', got {value}"


def test_exception_handling_in_callbacks():
    """Test behavior when callbacks raise exceptions."""
    result = Ok("test")

    # Test callback that raises exception
    try:
        match(
            result,
            on_success=lambda x: 1 / 0,  # This will raise ZeroDivisionError
            on_error=lambda e: "error"
        )
        assert False, "Expected ZeroDivisionError to be raised"
    except ZeroDivisionError:
        pass

    result = Err("test")

    try:
        match(
            result,
            on_success=lambda x: "success",
            on_error=lambda e: 1 / 0  # This will raise ZeroDivisionError
        )
        assert False, "Expected ZeroDivisionError to be raised"
    except ZeroDivisionError:
        pass


def test_usage_examples_from_issue():
    """Test the usage examples provided in the issue description."""
    # Basic Usage example
    result = Ok(42)
    value = match(
        result,
        on_success=lambda x: x * 2,
        on_error=lambda e: 0
    )
    assert value == 84, f"Expected 84, got {value}"

    result = Err("Not found")
    value = match(
        result,
        on_success=lambda x: x * 2,
        on_error=lambda e: 0
    )
    assert value == 0, f"Expected 0, got {value}"

    # Type-Specific Handling example
    def handle_success(value: int) -> str:
        return f"Success: {value}"

    def handle_error(error: str) -> str:
        return f"Error: {error}"

    result = Ok(42)
    result_str = match(
        result,
        on_success=handle_success,
        on_error=handle_error
    )
    assert result_str == "Success: 42", f"Expected 'Success: 42', got {result_str}"

    result = Err("error message")
    result_str = match(
        result,
        on_success=handle_success,
        on_error=handle_error
    )
    assert result_str == "Error: error message", f"Expected 'Error: error message', got {result_str}"