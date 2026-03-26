"""
Auto-fix module for common XAML validation issues.

Applies safe, deterministic fixes to XAML files for issues that
have clear resolutions.
"""

import re
from pathlib import Path
from typing import Dict, List, Tuple

from .validator import ValidationResult, ValidationIssue, Severity


# ═══════════════════════════════════════════════════════════════════════════════
# FIX DEFINITIONS
# ═══════════════════════════════════════════════════════════════════════════════

FIXES: Dict[str, Tuple[str, str]] = {
    # (pattern_to_find, replacement)

    # Version fixes
    "Version-V3": (r'Version="V3"', 'Version="V5"'),
    "Version-V4": (r'Version="V4"', 'Version="V5"'),

    # ElementType fixes
    "ElementType-DataGrid": (r'ElementType="DataGrid"', 'ElementType="Table"'),
    "ElementType-ComboBox": (r'ElementType="ComboBox"', 'ElementType="DropDown"'),
    "ElementType-InputBoxText": (r'ElementType="InputBoxText"', 'ElementType="InputBox"'),

    # Type fixes
    "TYPE-001": (r'x:TypeArguments="DataTable"', 'x:TypeArguments="sd:DataTable"'),
    "TYPE-002": (r'x:TypeArguments="DataRow"', 'x:TypeArguments="sd:DataRow"'),

    # Property renames
    "NExtractData-DataTable": (r'NExtractData([^>]*)DataTable=', r'NExtractData\1ExtractedData='),
    "NExtractData-Result": (r'NExtractData([^>]*)Result=', r'NExtractData\1ExtractedData='),
    "NGetText-Result": (r'NGetText([^>]*)Result=', r'NGetText\1Value='),
    "GetQueueItem-QueueType": (r'GetQueueItem([^>]*)QueueType=', r'GetQueueItem\1QueueName='),

    # Exception shorthand
    "BRE-FullyQualified": (
        r'New\s+UiPath\.Core\.BusinessRuleException\(',
        'New BusinessRuleException('
    ),
    "SysEx-FullyQualified": (
        r'New\s+System\.ApplicationException\(',
        'New ApplicationException('
    ),
}

# Namespace additions
NAMESPACE_FIXES = {
    "NS-001": {
        "check": r'x:TypeArguments="[^"]*DataTable',
        "namespace": 'xmlns:sd="clr-namespace:System.Data;assembly=System.Data"',
        "insert_after": 'xmlns:x=',
    },
    "NS-002": {
        "check": r'<uix:',
        "namespace": 'xmlns:uix="clr-namespace:UiPath.UIAutomationNext.Activities;assembly=UiPath.UIAutomationNext.Activities"',
        "insert_after": 'xmlns:ui=',
    },
}


def apply_fixes(result: ValidationResult) -> int:
    """
    Apply auto-fixes to files with fixable issues.

    Args:
        result: ValidationResult containing issues to fix

    Returns:
        Number of issues fixed
    """
    fixed_count = 0

    # Group issues by file
    issues_by_file: Dict[str, List[ValidationIssue]] = {}
    for issue in result.issues:
        if issue.auto_fixable:
            if issue.file_path not in issues_by_file:
                issues_by_file[issue.file_path] = []
            issues_by_file[issue.file_path].append(issue)

    # Apply fixes to each file
    for file_path, issues in issues_by_file.items():
        path = Path(file_path)
        if not path.exists():
            continue

        content = path.read_text(encoding="utf-8")
        original_content = content

        for issue in issues:
            # Try to find a matching fix
            for fix_id, (pattern, replacement) in FIXES.items():
                if fix_id in issue.rule_id or issue.rule_id in fix_id:
                    new_content = re.sub(pattern, replacement, content)
                    if new_content != content:
                        content = new_content
                        fixed_count += 1
                        break

            # Check namespace fixes
            for fix_id, fix_spec in NAMESPACE_FIXES.items():
                if fix_id == issue.rule_id:
                    if re.search(fix_spec["check"], content) and fix_spec["namespace"] not in content:
                        # Find insertion point
                        insert_after = fix_spec["insert_after"]
                        match = re.search(rf'({insert_after}"[^"]*")', content)
                        if match:
                            insert_pos = match.end()
                            content = (
                                content[:insert_pos] +
                                '\n  ' + fix_spec["namespace"] +
                                content[insert_pos:]
                            )
                            fixed_count += 1

        # Write changes if any
        if content != original_content:
            path.write_text(content, encoding="utf-8")
            print(f"  Fixed: {file_path}")

    return fixed_count


def preview_fixes(result: ValidationResult) -> List[Tuple[str, str, str]]:
    """
    Preview fixes without applying them.

    Returns:
        List of (file_path, original_text, fixed_text) tuples
    """
    previews = []

    for issue in result.issues:
        if not issue.auto_fixable:
            continue

        path = Path(issue.file_path)
        if not path.exists():
            continue

        content = path.read_text(encoding="utf-8")

        for fix_id, (pattern, replacement) in FIXES.items():
            if fix_id in issue.rule_id or issue.rule_id in fix_id:
                match = re.search(pattern, content)
                if match:
                    original = match.group()
                    fixed = re.sub(pattern, replacement, original)
                    previews.append((issue.file_path, original, fixed))
                    break

    return previews
