"""
Core XAML validation logic.

Validates XAML files against:
- XML well-formedness
- UiPath-specific rules (enums, properties, namespaces)
- LLM hallucination patterns
- ReFramework architecture best practices
"""

import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import List, Optional, Dict, Set, Tuple

from .constants import (
    VALID_ENUMS,
    KNOWN_ACTIVITIES,
    REQUIRED_NAMESPACES,
    HALLUCINATION_PATTERNS,
    ARCHITECTURE_RULES,
)


class Severity(Enum):
    """Validation issue severity levels."""
    ERROR = "ERROR"    # Will crash Studio or cause compile failure
    WARN = "WARN"      # Runtime failure or silent data loss risk
    INFO = "INFO"      # Best practice violation


@dataclass
class ValidationIssue:
    """Represents a single validation issue found in XAML."""
    file_path: str
    line_number: Optional[int]
    severity: Severity
    rule_id: str
    message: str
    suggestion: Optional[str] = None
    auto_fixable: bool = False

    def __str__(self) -> str:
        loc = f":{self.line_number}" if self.line_number else ""
        return f"[{self.severity.value}] {self.file_path}{loc} - {self.rule_id}: {self.message}"


@dataclass
class ValidationResult:
    """Result of validating one or more XAML files."""
    issues: List[ValidationIssue] = field(default_factory=list)
    files_checked: int = 0
    files_with_errors: int = 0

    @property
    def has_errors(self) -> bool:
        return any(i.severity == Severity.ERROR for i in self.issues)

    @property
    def error_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == Severity.ERROR)

    @property
    def warn_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == Severity.WARN)

    @property
    def info_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == Severity.INFO)

    def add(self, issue: ValidationIssue):
        self.issues.append(issue)

    def merge(self, other: "ValidationResult"):
        self.issues.extend(other.issues)
        self.files_checked += other.files_checked
        self.files_with_errors += other.files_with_errors


def validate_file(file_path: str, lint: bool = True, strict: bool = False) -> ValidationResult:
    """
    Validate a single XAML file.

    Args:
        file_path: Path to the XAML file
        lint: Enable semantic/architecture checks (default True)
        strict: Enable strict naming convention warnings (default False)

    Returns:
        ValidationResult with all issues found
    """
    result = ValidationResult(files_checked=1)
    path = Path(file_path)

    if not path.exists():
        result.add(ValidationIssue(
            file_path=str(path),
            line_number=None,
            severity=Severity.ERROR,
            rule_id="FILE-001",
            message=f"File not found: {path}"
        ))
        result.files_with_errors = 1
        return result

    if path.suffix.lower() != ".xaml":
        return result

    content = path.read_text(encoding="utf-8")

    # Phase 1: XML well-formedness
    xml_issues = _check_xml_wellformed(str(path), content)
    for issue in xml_issues:
        result.add(issue)

    if any(i.severity == Severity.ERROR for i in xml_issues):
        result.files_with_errors = 1
        return result  # Can't continue if XML is malformed

    # Phase 2: Hallucination pattern detection
    hallucination_issues = _check_hallucination_patterns(str(path), content)
    for issue in hallucination_issues:
        result.add(issue)

    if lint:
        # Phase 3: Namespace validation
        namespace_issues = _check_namespaces(str(path), content)
        for issue in namespace_issues:
            result.add(issue)

        # Phase 4: Activity-specific validation
        activity_issues = _check_activities(str(path), content)
        for issue in activity_issues:
            result.add(issue)

        # Phase 5: Enum validation
        enum_issues = _check_enums(str(path), content)
        for issue in enum_issues:
            result.add(issue)

        # Phase 6: Type validation
        type_issues = _check_types(str(path), content)
        for issue in type_issues:
            result.add(issue)

        # Phase 7: Architecture rules
        arch_issues = _check_architecture(str(path), content)
        for issue in arch_issues:
            result.add(issue)

    if strict:
        # Phase 8: Naming conventions
        naming_issues = _check_naming(str(path), content)
        for issue in naming_issues:
            result.add(issue)

    if any(i.severity == Severity.ERROR for i in result.issues):
        result.files_with_errors = 1

    return result


def validate_project(project_path: str, lint: bool = True, strict: bool = False) -> ValidationResult:
    """
    Validate all XAML files in a UiPath project.

    Args:
        project_path: Path to project directory (containing project.json)
        lint: Enable semantic/architecture checks
        strict: Enable strict naming convention warnings

    Returns:
        ValidationResult with all issues found across all files
    """
    result = ValidationResult()
    project_dir = Path(project_path)

    if not project_dir.is_dir():
        result.add(ValidationIssue(
            file_path=str(project_dir),
            line_number=None,
            severity=Severity.ERROR,
            rule_id="PROJECT-001",
            message=f"Not a directory: {project_dir}"
        ))
        return result

    # Find all XAML files
    xaml_files = list(project_dir.rglob("*.xaml"))

    if not xaml_files:
        result.add(ValidationIssue(
            file_path=str(project_dir),
            line_number=None,
            severity=Severity.WARN,
            rule_id="PROJECT-002",
            message="No XAML files found in project"
        ))
        return result

    # Validate each file
    for xaml_file in xaml_files:
        file_result = validate_file(str(xaml_file), lint=lint, strict=strict)
        result.merge(file_result)

    # Cross-file validation
    if lint:
        cross_file_issues = _check_cross_file(project_dir, xaml_files)
        for issue in cross_file_issues:
            result.add(issue)

    return result


# ═══════════════════════════════════════════════════════════════════════════════
# VALIDATION PHASES
# ═══════════════════════════════════════════════════════════════════════════════

def _check_xml_wellformed(file_path: str, content: str) -> List[ValidationIssue]:
    """Check if XAML is well-formed XML."""
    issues = []
    try:
        ET.fromstring(content)
    except ET.ParseError as e:
        line_num = e.position[0] if e.position else None
        issues.append(ValidationIssue(
            file_path=file_path,
            line_number=line_num,
            severity=Severity.ERROR,
            rule_id="XML-001",
            message=f"XML parse error: {e}",
            suggestion="Check for unescaped special characters (& < > \" ')"
        ))
    return issues


def _check_hallucination_patterns(file_path: str, content: str) -> List[ValidationIssue]:
    """Check for known LLM hallucination patterns."""
    issues = []
    lines = content.split('\n')

    for pattern, severity_str, message in HALLUCINATION_PATTERNS:
        for line_num, line in enumerate(lines, 1):
            if re.search(pattern, line):
                issues.append(ValidationIssue(
                    file_path=file_path,
                    line_number=line_num,
                    severity=Severity[severity_str],
                    rule_id="HALL-" + pattern[:20].replace(r'\\', '').replace('"', ''),
                    message=message,
                    auto_fixable=severity_str == "ERROR"
                ))
    return issues


def _check_namespaces(file_path: str, content: str) -> List[ValidationIssue]:
    """Check for required and correct namespaces."""
    issues = []

    # Check for DataTable usage without sd: namespace
    if "DataTable" in content and 'xmlns:sd=' not in content:
        if re.search(r'x:TypeArguments="[^"]*DataTable', content):
            issues.append(ValidationIssue(
                file_path=file_path,
                line_number=None,
                severity=Severity.ERROR,
                rule_id="NS-001",
                message="DataTable used but sd: namespace not declared",
                suggestion='Add xmlns:sd="clr-namespace:System.Data;assembly=System.Data"'
            ))

    # Check for modern UI activities without uix: namespace
    if re.search(r'<uix:', content) and 'xmlns:uix=' not in content:
        issues.append(ValidationIssue(
            file_path=file_path,
            line_number=None,
            severity=Severity.ERROR,
            rule_id="NS-002",
            message="Modern UI activities (uix:) used but namespace not declared",
            suggestion='Add xmlns:uix="clr-namespace:UiPath.UIAutomationNext.Activities;assembly=UiPath.UIAutomationNext.Activities"'
        ))

    return issues


def _check_activities(file_path: str, content: str) -> List[ValidationIssue]:
    """Check activity-specific rules (valid properties, required children)."""
    issues = []

    for activity_name, rules in KNOWN_ACTIVITIES.items():
        # Find all instances of this activity
        pattern = rf'<{re.escape(activity_name)}[^>]*>'
        for match in re.finditer(pattern, content):
            activity_text = match.group()
            line_num = content[:match.start()].count('\n') + 1

            # Check for invalid properties
            invalid_props = rules.get("invalid_props", set())
            for prop in invalid_props:
                if f'{prop}=' in activity_text or f'{prop} =' in activity_text:
                    issues.append(ValidationIssue(
                        file_path=file_path,
                        line_number=line_num,
                        severity=Severity.ERROR,
                        rule_id=f"ACT-{activity_name.replace(':', '_')}",
                        message=f"{activity_name} has invalid property '{prop}'",
                        suggestion=f"Remove or replace '{prop}'"
                    ))

    return issues


def _check_enums(file_path: str, content: str) -> List[ValidationIssue]:
    """Check that enum values are valid."""
    issues = []

    for enum_name, valid_values in VALID_ENUMS.items():
        # Find all uses of this enum attribute
        pattern = rf'{enum_name}="([^"]*)"'
        for match in re.finditer(pattern, content):
            value = match.group(1)
            # Skip VB expressions
            if value.startswith('[') or '(' in value:
                continue
            if value not in valid_values:
                line_num = content[:match.start()].count('\n') + 1
                issues.append(ValidationIssue(
                    file_path=file_path,
                    line_number=line_num,
                    severity=Severity.ERROR,
                    rule_id=f"ENUM-{enum_name}",
                    message=f"Invalid {enum_name} value '{value}'",
                    suggestion=f"Valid values: {', '.join(sorted(valid_values))}"
                ))

    return issues


def _check_types(file_path: str, content: str) -> List[ValidationIssue]:
    """Check for type declaration issues."""
    issues = []

    # Check for unqualified DataTable/DataRow types
    if re.search(r'x:TypeArguments="DataTable"', content):
        line_num = _find_line(content, 'x:TypeArguments="DataTable"')
        issues.append(ValidationIssue(
            file_path=file_path,
            line_number=line_num,
            severity=Severity.ERROR,
            rule_id="TYPE-001",
            message="Unqualified DataTable type - use sd:DataTable",
            suggestion='Change x:TypeArguments="DataTable" to x:TypeArguments="sd:DataTable"',
            auto_fixable=True
        ))

    if re.search(r'x:TypeArguments="DataRow"', content):
        line_num = _find_line(content, 'x:TypeArguments="DataRow"')
        issues.append(ValidationIssue(
            file_path=file_path,
            line_number=line_num,
            severity=Severity.ERROR,
            rule_id="TYPE-002",
            message="Unqualified DataRow type - use sd:DataRow",
            suggestion='Change x:TypeArguments="DataRow" to x:TypeArguments="sd:DataRow"',
            auto_fixable=True
        ))

    # Check for empty Out/InOut bindings (silent data loss)
    for match in re.finditer(r'<(Out|InOut)Argument[^>]*>\s*\[\s*\]', content):
        line_num = content[:match.start()].count('\n') + 1
        issues.append(ValidationIssue(
            file_path=file_path,
            line_number=line_num,
            severity=Severity.WARN,
            rule_id="TYPE-003",
            message="Empty Out/InOut argument binding causes silent data loss",
            suggestion="Bind to a variable: [variableName]"
        ))

    return issues


def _check_architecture(file_path: str, content: str) -> List[ValidationIssue]:
    """Check ReFramework architecture rules."""
    issues = []
    file_name = Path(file_path).name
    rel_path = str(Path(file_path))

    # Check for restricted activities
    for activity, allowed_files in ARCHITECTURE_RULES.get("restricted_activities", {}).items():
        if activity in content:
            if not any(allowed in rel_path for allowed in allowed_files):
                line_num = _find_line(content, activity)
                issues.append(ValidationIssue(
                    file_path=file_path,
                    line_number=line_num,
                    severity=Severity.INFO,
                    rule_id=f"ARCH-{activity}",
                    message=f"{activity} should only be in: {', '.join(allowed_files)}",
                    suggestion=f"Move {activity} to appropriate framework file"
                ))

    # Check for hardcoded URLs
    url_pattern = r'(https?://[^\s<>"]+)'
    for match in re.finditer(url_pattern, content):
        url = match.group(1)
        # Skip Config references
        if 'Config(' not in content[max(0, match.start()-50):match.start()]:
            line_num = content[:match.start()].count('\n') + 1
            issues.append(ValidationIssue(
                file_path=file_path,
                line_number=line_num,
                severity=Severity.INFO,
                rule_id="ARCH-URL",
                message=f"Hardcoded URL found: {url[:50]}...",
                suggestion="Use Config() to store URLs"
            ))

    return issues


def _check_naming(file_path: str, content: str) -> List[ValidationIssue]:
    """Check naming conventions (strict mode)."""
    issues = []
    file_name = Path(file_path).stem

    # Check workflow file naming (PascalCase)
    if not re.match(r'^[A-Z][a-zA-Z0-9]*$', file_name.replace('_', '')):
        issues.append(ValidationIssue(
            file_path=file_path,
            line_number=None,
            severity=Severity.INFO,
            rule_id="NAME-001",
            message=f"Workflow file name '{file_name}' should be PascalCase",
            suggestion="Rename to PascalCase (e.g., MyWorkflow.xaml)"
        ))

    # Check DisplayName format
    for match in re.finditer(r'DisplayName="([^"]*)"', content):
        display_name = match.group(1)
        # Check for generic names
        if display_name.lower() in ('sequence', 'if', 'while', 'foreach', 'trycatch'):
            line_num = content[:match.start()].count('\n') + 1
            issues.append(ValidationIssue(
                file_path=file_path,
                line_number=line_num,
                severity=Severity.INFO,
                rule_id="NAME-002",
                message=f"Generic DisplayName '{display_name}' - use descriptive name",
                suggestion="Use descriptive DisplayName that explains what the activity does"
            ))

    return issues


def _check_cross_file(project_dir: Path, xaml_files: List[Path]) -> List[ValidationIssue]:
    """Cross-file validation (invoke targets exist, etc.)."""
    issues = []

    # Build map of available workflows
    available_workflows = set()
    for f in xaml_files:
        rel_path = f.relative_to(project_dir)
        available_workflows.add(str(rel_path))
        available_workflows.add(str(rel_path).replace('/', '\\'))
        available_workflows.add(str(rel_path).replace('\\', '/'))

    # Check InvokeWorkflowFile targets
    for xaml_file in xaml_files:
        content = xaml_file.read_text(encoding="utf-8")
        for match in re.finditer(r'WorkflowFileName="([^"]*)"', content):
            target = match.group(1)
            # Skip expressions
            if target.startswith('['):
                continue
            # Normalize path
            target_normalized = target.replace('\\', '/').replace('//', '/')
            if target_normalized not in available_workflows:
                # Check if it's a relative path issue
                found = False
                for avail in available_workflows:
                    if avail.endswith(target_normalized) or target_normalized.endswith(avail):
                        found = True
                        break
                if not found:
                    line_num = content[:match.start()].count('\n') + 1
                    issues.append(ValidationIssue(
                        file_path=str(xaml_file),
                        line_number=line_num,
                        severity=Severity.WARN,
                        rule_id="CROSS-001",
                        message=f"InvokeWorkflowFile target not found: {target}",
                        suggestion="Check file path and ensure target workflow exists"
                    ))

    return issues


# ═══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def _find_line(content: str, pattern: str) -> Optional[int]:
    """Find line number of first occurrence of pattern."""
    idx = content.find(pattern)
    if idx == -1:
        return None
    return content[:idx].count('\n') + 1
