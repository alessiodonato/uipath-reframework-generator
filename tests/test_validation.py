#!/usr/bin/env python3
"""
Test suite for XAML validation module.

Tests all lint rules and validation logic.
"""

import unittest
import sys
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from validate_xaml import validate_file, validate_project, Severity


class TestXMLWellFormedness(unittest.TestCase):
    """Test XML well-formedness checks."""

    def test_valid_xml(self):
        """Test that valid XML passes."""
        xaml = '''<?xml version="1.0"?>
<Activity xmlns="http://schemas.microsoft.com/netfx/2009/xaml/activities">
  <Sequence DisplayName="Test" />
</Activity>'''

        # Write to temp file
        temp_file = Path(__file__).parent / "temp_valid.xaml"
        temp_file.write_text(xaml)

        try:
            result = validate_file(str(temp_file), lint=False)
            self.assertEqual(result.error_count, 0)
        finally:
            temp_file.unlink()

    def test_malformed_xml(self):
        """Test that malformed XML is caught."""
        xaml = '''<?xml version="1.0"?>
<Activity>
  <Sequence DisplayName="Test">
  <!-- Missing closing tag -->
</Activity>'''

        temp_file = Path(__file__).parent / "temp_malformed.xaml"
        temp_file.write_text(xaml)

        try:
            result = validate_file(str(temp_file), lint=False)
            self.assertGreater(result.error_count, 0)
            self.assertTrue(any("XML" in i.rule_id for i in result.issues))
        finally:
            temp_file.unlink()

    def test_unescaped_ampersand(self):
        """Test that unescaped & is caught."""
        xaml = '''<?xml version="1.0"?>
<Activity xmlns="http://schemas.microsoft.com/netfx/2009/xaml/activities">
  <Sequence DisplayName="Test & Value" />
</Activity>'''

        temp_file = Path(__file__).parent / "temp_ampersand.xaml"
        temp_file.write_text(xaml)

        try:
            result = validate_file(str(temp_file), lint=False)
            self.assertGreater(result.error_count, 0)
        finally:
            temp_file.unlink()


class TestHallucinationPatterns(unittest.TestCase):
    """Test detection of common LLM hallucination patterns."""

    def _make_xaml(self, content: str) -> str:
        return f'''<?xml version="1.0"?>
<Activity
  xmlns="http://schemas.microsoft.com/netfx/2009/xaml/activities"
  xmlns:uix="clr-namespace:UiPath.UIAutomationNext.Activities"
  xmlns:ui="http://schemas.uipath.com/workflow/activities">
  {content}
</Activity>'''

    def test_version_v3_detected(self):
        """Test that Version=V3 is caught."""
        xaml = self._make_xaml('<uix:NClick Version="V3" />')

        temp_file = Path(__file__).parent / "temp_v3.xaml"
        temp_file.write_text(xaml)

        try:
            result = validate_file(str(temp_file), lint=True)
            self.assertTrue(any("Version" in str(i) or "V3" in str(i) for i in result.issues))
        finally:
            temp_file.unlink()

    def test_version_v5_passes(self):
        """Test that Version=V5 is accepted."""
        xaml = self._make_xaml('<uix:NClick Version="V5" />')

        temp_file = Path(__file__).parent / "temp_v5.xaml"
        temp_file.write_text(xaml)

        try:
            result = validate_file(str(temp_file), lint=True)
            version_issues = [i for i in result.issues if "Version" in str(i)]
            self.assertEqual(len(version_issues), 0)
        finally:
            temp_file.unlink()

    def test_element_type_datagrid_detected(self):
        """Test that ElementType=DataGrid is caught."""
        xaml = self._make_xaml('<uix:NExtractData ElementType="DataGrid" />')

        temp_file = Path(__file__).parent / "temp_datagrid.xaml"
        temp_file.write_text(xaml)

        try:
            result = validate_file(str(temp_file), lint=True)
            self.assertTrue(any("DataGrid" in str(i) or "ElementType" in str(i) for i in result.issues))
        finally:
            temp_file.unlink()


class TestTypeValidation(unittest.TestCase):
    """Test type declaration validation."""

    def _make_xaml(self, content: str) -> str:
        return f'''<?xml version="1.0"?>
<Activity
  xmlns="http://schemas.microsoft.com/netfx/2009/xaml/activities"
  xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml">
  {content}
</Activity>'''

    def test_unqualified_datatable_detected(self):
        """Test that unqualified DataTable is caught."""
        xaml = self._make_xaml('<Variable x:TypeArguments="DataTable" Name="dt" />')

        temp_file = Path(__file__).parent / "temp_dt.xaml"
        temp_file.write_text(xaml)

        try:
            result = validate_file(str(temp_file), lint=True)
            self.assertTrue(any("DataTable" in str(i) for i in result.issues))
        finally:
            temp_file.unlink()

    def test_qualified_datatable_passes(self):
        """Test that sd:DataTable is accepted."""
        xaml = f'''<?xml version="1.0"?>
<Activity
  xmlns="http://schemas.microsoft.com/netfx/2009/xaml/activities"
  xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
  xmlns:sd="clr-namespace:System.Data;assembly=System.Data">
  <Variable x:TypeArguments="sd:DataTable" Name="dt" />
</Activity>'''

        temp_file = Path(__file__).parent / "temp_sd_dt.xaml"
        temp_file.write_text(xaml)

        try:
            result = validate_file(str(temp_file), lint=True)
            type_issues = [i for i in result.issues if "TYPE-001" in i.rule_id]
            self.assertEqual(len(type_issues), 0)
        finally:
            temp_file.unlink()


class TestEnumValidation(unittest.TestCase):
    """Test enum value validation."""

    def _make_xaml(self, content: str) -> str:
        return f'''<?xml version="1.0"?>
<Activity
  xmlns="http://schemas.microsoft.com/netfx/2009/xaml/activities"
  xmlns:uix="clr-namespace:UiPath.UIAutomationNext.Activities"
  xmlns:ui="http://schemas.uipath.com/workflow/activities">
  {content}
</Activity>'''

    def test_valid_log_level(self):
        """Test that valid log levels pass."""
        for level in ["Trace", "Info", "Warn", "Error", "Fatal"]:
            xaml = self._make_xaml(f'<ui:LogMessage Level="{level}" />')

            temp_file = Path(__file__).parent / f"temp_log_{level.lower()}.xaml"
            temp_file.write_text(xaml)

            try:
                result = validate_file(str(temp_file), lint=True)
                enum_issues = [i for i in result.issues if "ENUM" in i.rule_id and "LogLevel" in i.rule_id]
                self.assertEqual(len(enum_issues), 0, f"Level {level} should be valid")
            finally:
                temp_file.unlink()

    def test_invalid_log_level(self):
        """Test that invalid log levels are caught."""
        xaml = self._make_xaml('<ui:LogMessage Level="Debug" />')

        temp_file = Path(__file__).parent / "temp_log_debug.xaml"
        temp_file.write_text(xaml)

        try:
            result = validate_file(str(temp_file), lint=True)
            self.assertTrue(any("ENUM-Level" in i.rule_id or "Debug" in str(i) for i in result.issues))
        finally:
            temp_file.unlink()


class TestValidationResult(unittest.TestCase):
    """Test ValidationResult behavior."""

    def test_has_errors(self):
        """Test has_errors property."""
        from validate_xaml.validator import ValidationResult, ValidationIssue

        result = ValidationResult()
        self.assertFalse(result.has_errors)

        result.add(ValidationIssue(
            file_path="test.xaml",
            line_number=1,
            severity=Severity.WARN,
            rule_id="TEST",
            message="Warning"
        ))
        self.assertFalse(result.has_errors)

        result.add(ValidationIssue(
            file_path="test.xaml",
            line_number=2,
            severity=Severity.ERROR,
            rule_id="TEST",
            message="Error"
        ))
        self.assertTrue(result.has_errors)

    def test_counts(self):
        """Test issue count properties."""
        from validate_xaml.validator import ValidationResult, ValidationIssue

        result = ValidationResult()

        for i in range(3):
            result.add(ValidationIssue("test.xaml", i, Severity.ERROR, "E", "Error"))
        for i in range(2):
            result.add(ValidationIssue("test.xaml", i, Severity.WARN, "W", "Warning"))
        result.add(ValidationIssue("test.xaml", 0, Severity.INFO, "I", "Info"))

        self.assertEqual(result.error_count, 3)
        self.assertEqual(result.warn_count, 2)
        self.assertEqual(result.info_count, 1)


class TestFileNotFound(unittest.TestCase):
    """Test handling of missing files."""

    def test_missing_file(self):
        """Test that missing file is reported."""
        result = validate_file("/nonexistent/path/file.xaml")
        self.assertGreater(result.error_count, 0)
        self.assertTrue(any("not found" in i.message.lower() for i in result.issues))

    def test_missing_directory(self):
        """Test that missing directory is reported."""
        result = validate_project("/nonexistent/path/")
        self.assertGreater(result.error_count, 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
