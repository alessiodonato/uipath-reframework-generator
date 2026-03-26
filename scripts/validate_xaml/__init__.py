"""
XAML Validation Module for UiPath ReFramework Generator

Provides comprehensive validation of generated XAML files to catch:
- LLM hallucination patterns (wrong enums, invalid properties)
- Structural issues (missing namespaces, malformed XML)
- UiPath-specific errors (wrong activity attributes, type mismatches)
- Architecture violations (ReFramework best practices)

Usage:
    from validate_xaml import validate_file, validate_project

    # Validate single file
    issues = validate_file("path/to/workflow.xaml")

    # Validate entire project
    issues = validate_project("path/to/project/")

    # CLI usage
    python -m validate_xaml path/to/project --lint --fix
"""

from .validator import (
    validate_file,
    validate_project,
    ValidationIssue,
    Severity,
)

from .constants import (
    VALID_ENUMS,
    KNOWN_ACTIVITIES,
    REQUIRED_NAMESPACES,
)

__all__ = [
    "validate_file",
    "validate_project",
    "ValidationIssue",
    "Severity",
    "VALID_ENUMS",
    "KNOWN_ACTIVITIES",
    "REQUIRED_NAMESPACES",
]
