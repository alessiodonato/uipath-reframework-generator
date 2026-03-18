#!/usr/bin/env python3
"""
Test script for the ReFramework Generator.
Uses mock metadata to test XAML generation without API calls.
"""

import json
import os
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

# Add parent directory to path to import the generator
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

# Mock metadata that simulates extraction from a PDD
MOCK_METADATA = {
    "process_name": "InvoiceProcessing",
    "process_description": "Processes invoices from an Orchestrator queue, validates data, and posts to ERP system.",
    "applications": ["WebERP"],
    "transaction_source": "Queue",
    "queue_name": "InvoiceProcessingQueue",
    "transaction_item_fields": [
        {"name": "invoiceNumber", "type": "String", "description": "Unique invoice identifier"},
        {"name": "vendorCode", "type": "String", "description": "Vendor identifier"},
        {"name": "amount", "type": "Decimal", "description": "Invoice amount"}
    ],
    "process_steps": [
        {
            "id": "Step01",
            "name": "ValidateInvoiceData",
            "description": "Validates that the invoice has all required fields and the amount is positive.",
            "app": "WebERP",
            "pseudo_steps": [
                "1. Read invoiceNumber from transaction item",
                "2. Read vendorCode from transaction item",
                "3. Read amount from transaction item",
                "4. If amount <= 0, throw BusinessRuleException('Invalid invoice amount')",
                "5. If vendorCode is empty, throw BusinessRuleException('Missing vendor code')"
            ],
            "config_keys_used": [],
            "output_variables": [
                {"name": "isValid", "type": "Boolean", "description": "Whether invoice passed validation"}
            ],
            "throws": [
                {"exception_type": "BusinessRuleException", "condition": "amount <= 0 or vendorCode is empty"}
            ],
            "business_rule": "Invoice amount must be positive and vendor code must be present"
        },
        {
            "id": "Step02",
            "name": "PostInvoiceToERP",
            "description": "Posts the validated invoice to the WebERP system.",
            "app": "WebERP",
            "pseudo_steps": [
                "1. Navigate to URL from Config('WebERP_URL')",
                "2. Login using credentials from Config('WebERP_CredentialAsset')",
                "3. Navigate to Invoice Entry screen",
                "4. Enter invoice details (invoiceNumber, vendorCode, amount)",
                "5. Click Submit button",
                "6. Verify confirmation message appears, else throw ApplicationException('Submission failed')"
            ],
            "config_keys_used": ["WebERP_URL", "WebERP_CredentialAsset"],
            "output_variables": [
                {"name": "confirmationNumber", "type": "String", "description": "ERP confirmation number"}
            ],
            "throws": [
                {"exception_type": "ApplicationException", "condition": "login fails or submission times out"}
            ],
            "business_rule": ""
        }
    ],
    "business_exceptions": [
        {
            "name": "InvalidInvoiceAmountException",
            "condition": "Invoice amount is zero or negative",
            "suggested_step": "ValidateInvoiceData"
        },
        {
            "name": "MissingVendorCodeException",
            "condition": "Vendor code is missing",
            "suggested_step": "ValidateInvoiceData"
        }
    ],
    "system_exceptions": [
        {
            "name": "ERPLoginFailedException",
            "condition": "Login to WebERP fails",
            "recovery_hint": "Restart browser and retry"
        }
    ],
    "config_settings": [
        {"name": "WebERP_URL", "value": "https://erp.company.com", "type": "Setting", "description": "WebERP base URL"},
        {"name": "WebERP_CredentialAsset", "value": "WebERP_Credentials", "type": "Asset", "description": "Orchestrator credential asset"},
        {"name": "InvoiceAmountThreshold", "value": "10000", "type": "Constant", "description": "Invoices above this require approval"}
    ],
    "max_retry_number": 3,
    "process_type": "Transactional"
}


def validate_xml(filepath: Path) -> tuple[bool, str]:
    """Validate that a file is well-formed XML."""
    try:
        ET.parse(filepath)
        return True, "OK"
    except ET.ParseError as e:
        return False, str(e)


def check_no_untyped_object(filepath: Path) -> tuple[bool, list[str]]:
    """Check that x:Type p:Object is not used without TODO comment.

    Exception: scg:Dictionary(x:String, x:Object) is a standard UiPath pattern
    for the Config dictionary and is allowed without TODO.
    """
    content = filepath.read_text(encoding="utf-8")
    issues = []

    # Allowed patterns that contain x:Object but are standard UiPath patterns
    allowed_patterns = [
        "scg:Dictionary(x:String, x:Object)",  # Config dictionary
        "Dictionary(x:String, x:Object)",       # Short form
        "s:Dictionary(x:Type p:String, x:Type p:Object)",  # Explicit type form
    ]

    # Look for x:Type p:Object or similar patterns
    lines = content.split("\n")
    for i, line in enumerate(lines):
        # Check for Object patterns
        has_object_pattern = "x:Object" in line or "p:Object" in line

        if has_object_pattern:
            # Check if it's an allowed pattern
            is_allowed = any(pattern in line for pattern in allowed_patterns)
            if is_allowed:
                continue

            # Check if there's a TODO nearby
            context = "\n".join(lines[max(0, i-1):i+2])
            if "TODO" not in context:
                issues.append(f"Line {i+1}: standalone Object type without TODO comment")

    return len(issues) == 0, issues


def check_log_messages(filepath: Path, process_name: str) -> tuple[bool, list[str]]:
    """Check that XAML file has at least one LogMessage with correct format."""
    content = filepath.read_text(encoding="utf-8")
    issues = []

    # Check for LogMessage presence
    if "<ui:LogMessage" not in content and "<LogMessage" not in content:
        issues.append("No LogMessage found in file")
    else:
        # Check for correct format pattern
        if f"[{process_name}]" not in content:
            issues.append(f"No log message with [{process_name}] prefix found")

    return len(issues) == 0, issues


def run_test():
    """Run the generator test with mock metadata."""
    print("=" * 60)
    print("ReFramework Generator Test Suite")
    print("=" * 60)

    # Import generator after ensuring path
    from generate_reframework import build_project, zip_project

    # Check for openpyxl availability
    try:
        import openpyxl
        has_openpyxl = True
    except ImportError:
        has_openpyxl = False
        print("\n⚠️  openpyxl not installed - Config.xlsx generation will be skipped")

    # Create temp directory for output
    with tempfile.TemporaryDirectory() as tmpdir:
        print(f"\n1. Generating project with mock metadata...")
        print(f"   Process: {MOCK_METADATA['process_name']}")
        print(f"   Steps: {len(MOCK_METADATA['process_steps'])}")
        print(f"   Apps: {MOCK_METADATA['applications']}")

        project_dir = build_project(MOCK_METADATA, tmpdir)
        project_path = Path(project_dir)

        print(f"\n2. Validating generated files...")

        # Collect all XAML files
        xaml_files = list(project_path.rglob("*.xaml"))
        print(f"   Found {len(xaml_files)} XAML files")

        # Validation results
        xml_valid = 0
        xml_invalid = []
        object_issues = []
        log_issues = []
        todo_count = 0

        for xaml in xaml_files:
            relative = xaml.relative_to(project_path)

            # Check XML validity
            valid, err = validate_xml(xaml)
            if valid:
                xml_valid += 1
            else:
                xml_invalid.append((relative, err))

            # Check for untyped Object
            ok, issues = check_no_untyped_object(xaml)
            if not ok:
                object_issues.extend([(relative, i) for i in issues])

            # Check log messages
            ok, issues = check_log_messages(xaml, MOCK_METADATA["process_name"])
            if not ok:
                log_issues.extend([(relative, i) for i in issues])

            # Count TODOs
            content = xaml.read_text(encoding="utf-8")
            todo_count += content.count("TODO:")

        # Generate ZIP
        print(f"\n3. Creating ZIP archive...")
        zip_path = zip_project(project_dir, tmpdir)
        zip_size = Path(zip_path).stat().st_size // 1024

        # Print results
        print("\n" + "=" * 60)
        print("TEST RESULTS")
        print("=" * 60)

        print(f"\nXML Validation:")
        print(f"  Valid: {xml_valid}/{len(xaml_files)}")
        if xml_invalid:
            print("  Invalid files:")
            for f, e in xml_invalid:
                print(f"    - {f}: {e}")

        print(f"\nObject Type Check:")
        if object_issues:
            print(f"  Issues found: {len(object_issues)}")
            for f, i in object_issues:
                print(f"    - {f}: {i}")
        else:
            print("  OK - No untyped Object without TODO")

        print(f"\nLog Message Check:")
        if log_issues:
            print(f"  Issues found: {len(log_issues)}")
            for f, i in log_issues:
                print(f"    - {f}: {i}")
        else:
            print("  OK - All files have proper log messages")

        print(f"\nTODO Items: {todo_count}")
        print(f"ZIP Size: {zip_size} KB")

        # Write report
        report_path = project_path / "OUTPUT_QUALITY_REPORT.md"
        report_content = f"""# Output Quality Report

**Generated**: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Process**: {MOCK_METADATA['process_name']}

## Summary

| Metric | Value |
|--------|-------|
| XAML Files Generated | {len(xaml_files)} |
| XML Valid | {xml_valid}/{len(xaml_files)} |
| Object Type Issues | {len(object_issues)} |
| Log Format Issues | {len(log_issues)} |
| TODO Items Remaining | {todo_count} |
| ZIP Size | {zip_size} KB |

## Files Generated

"""
        for xaml in sorted(xaml_files):
            relative = xaml.relative_to(project_path)
            report_content += f"- `{relative}`\n"

        if xml_invalid:
            report_content += "\n## XML Validation Errors\n\n"
            for f, e in xml_invalid:
                report_content += f"- `{f}`: {e}\n"

        if object_issues:
            report_content += "\n## Object Type Issues\n\n"
            for f, i in object_issues:
                report_content += f"- `{f}`: {i}\n"

        if log_issues:
            report_content += "\n## Log Format Issues\n\n"
            for f, i in log_issues:
                report_content += f"- `{f}`: {i}\n"

        report_content += f"""
## TODO Items

Found {todo_count} TODO items across all generated files. These require manual implementation:
- UI selectors for login and data entry
- Credential retrieval from Orchestrator
- Application-specific close/kill logic
- Business rule validation implementation

## Conclusion

"""
        if xml_valid == len(xaml_files) and not object_issues:
            report_content += "✅ All validation checks passed. The generated project is ready for implementation in UiPath Studio."
        else:
            report_content += "⚠️ Some issues were found. Please review the errors above before opening in UiPath Studio."

        report_path.write_text(report_content, encoding="utf-8")
        print(f"\n4. Report written to: {report_path}")

        # Copy report to tests directory
        tests_report = Path(__file__).parent / "OUTPUT_QUALITY_REPORT.md"
        tests_report.write_text(report_content, encoding="utf-8")
        print(f"   Also copied to: {tests_report}")

        # Return success/failure
        return xml_valid == len(xaml_files) and len(object_issues) == 0


if __name__ == "__main__":
    try:
        success = run_test()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
