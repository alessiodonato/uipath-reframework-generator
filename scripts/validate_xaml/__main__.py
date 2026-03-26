#!/usr/bin/env python3
"""
CLI entry point for XAML validation.

Usage:
    python -m validate_xaml path/to/project --lint
    python -m validate_xaml path/to/file.xaml --lint --fix
    python -m validate_xaml path/to/project --strict
"""

import argparse
import sys
from pathlib import Path

from .validator import validate_file, validate_project, Severity


def main():
    parser = argparse.ArgumentParser(
        description="Validate UiPath XAML files for errors and best practices",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s ./MyProject --lint           Validate project with semantic checks
  %(prog)s ./Main.xaml --lint            Validate single file
  %(prog)s ./MyProject --lint --fix      Validate and auto-fix issues
  %(prog)s ./MyProject --strict          Include naming convention warnings

Exit codes:
  0  No errors found
  1  Errors found (will crash Studio)
  2  Warnings found (may cause runtime issues)
"""
    )

    parser.add_argument("path", help="Path to XAML file or project directory")
    parser.add_argument("--lint", action="store_true",
                       help="Enable semantic/architecture checks")
    parser.add_argument("--fix", action="store_true",
                       help="Auto-fix common issues (writes changes to files)")
    parser.add_argument("--strict", action="store_true",
                       help="Enable strict naming convention warnings")
    parser.add_argument("--json", action="store_true",
                       help="Output results as JSON")
    parser.add_argument("--quiet", "-q", action="store_true",
                       help="Only show errors, not warnings")
    parser.add_argument("--summary", action="store_true",
                       help="Show summary only, not individual issues")

    args = parser.parse_args()

    path = Path(args.path)

    # Run validation
    if path.is_file():
        result = validate_file(str(path), lint=args.lint, strict=args.strict)
    elif path.is_dir():
        result = validate_project(str(path), lint=args.lint, strict=args.strict)
    else:
        print(f"Error: Path not found: {path}", file=sys.stderr)
        sys.exit(1)

    # Apply fixes if requested
    if args.fix:
        from .fixer import apply_fixes
        fixed_count = apply_fixes(result)
        if fixed_count > 0:
            print(f"\nAuto-fixed {fixed_count} issues. Re-running validation...")
            if path.is_file():
                result = validate_file(str(path), lint=args.lint, strict=args.strict)
            else:
                result = validate_project(str(path), lint=args.lint, strict=args.strict)

    # Filter issues if quiet mode
    if args.quiet:
        result.issues = [i for i in result.issues if i.severity == Severity.ERROR]

    # Output results
    if args.json:
        import json
        output = {
            "files_checked": result.files_checked,
            "files_with_errors": result.files_with_errors,
            "error_count": result.error_count,
            "warn_count": result.warn_count,
            "info_count": result.info_count,
            "issues": [
                {
                    "file": i.file_path,
                    "line": i.line_number,
                    "severity": i.severity.value,
                    "rule_id": i.rule_id,
                    "message": i.message,
                    "suggestion": i.suggestion,
                    "auto_fixable": i.auto_fixable,
                }
                for i in result.issues
            ]
        }
        print(json.dumps(output, indent=2))
    else:
        # Human-readable output
        if not args.summary:
            for issue in result.issues:
                severity_color = {
                    Severity.ERROR: "\033[91m",  # Red
                    Severity.WARN: "\033[93m",   # Yellow
                    Severity.INFO: "\033[94m",   # Blue
                }.get(issue.severity, "")
                reset = "\033[0m"

                print(f"{severity_color}{issue}{reset}")
                if issue.suggestion:
                    print(f"    Suggestion: {issue.suggestion}")

        # Summary
        print(f"\n{'='*60}")
        print(f"Validation Summary")
        print(f"{'='*60}")
        print(f"Files checked:      {result.files_checked}")
        print(f"Files with errors:  {result.files_with_errors}")
        print(f"")
        print(f"  Errors:   {result.error_count}")
        print(f"  Warnings: {result.warn_count}")
        print(f"  Info:     {result.info_count}")
        print(f"{'='*60}")

        if result.has_errors:
            print("\n\033[91mValidation FAILED - fix errors before opening in Studio\033[0m")
        elif result.warn_count > 0:
            print("\n\033[93mValidation passed with warnings\033[0m")
        else:
            print("\n\033[92mValidation PASSED\033[0m")

    # Exit code
    if result.has_errors:
        sys.exit(1)
    elif result.warn_count > 0:
        sys.exit(2)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
