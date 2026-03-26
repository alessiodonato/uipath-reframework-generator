#!/usr/bin/env python3
"""
Test suite for XAML generators.

Validates that all generators produce valid, well-formed XAML
that passes validation checks.
"""

import unittest
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from generators import (
    # Core
    gen_sequence, gen_if, gen_if_else, gen_foreach, gen_while,
    gen_switch, gen_trycatch, gen_assign, gen_multiple_assign,
    # Logging
    gen_log_message, gen_add_log_fields, gen_comment,
    # Invoke
    gen_invoke_workflow, gen_invoke_workflow_simple,
    # Orchestrator
    gen_get_queue_item, gen_add_queue_item, gen_set_transaction_status,
    gen_get_credential, gen_get_asset,
    # Error handling
    gen_throw, gen_rethrow, gen_retry_scope,
    # UI Automation
    gen_nclick, gen_ntypeinto, gen_ngettext, gen_ncheckstate,
    gen_napplication_card, gen_ngoto_url,
    # Data
    gen_build_datatable, gen_add_data_row, gen_filter_datatable,
    # Helpers
    escape_xml, build_annotation,
)


class TestHelpers(unittest.TestCase):
    """Test helper functions."""

    def test_escape_xml_special_chars(self):
        """Test that special characters are escaped."""
        self.assertEqual(escape_xml("&"), "&amp;")
        self.assertEqual(escape_xml("<"), "&lt;")
        self.assertEqual(escape_xml(">"), "&gt;")
        self.assertEqual(escape_xml('"'), "&quot;")
        self.assertEqual(escape_xml("\n"), "&#xA;")

    def test_escape_xml_combined(self):
        """Test escaping multiple characters."""
        text = 'Value < 10 & Name = "Test"'
        expected = "Value &lt; 10 &amp; Name = &quot;Test&quot;"
        self.assertEqual(escape_xml(text), expected)

    def test_build_annotation(self):
        """Test annotation building."""
        ann = build_annotation(
            reads=["AppUrl", "Credentials"],
            output=[("strResult", "String")],
            throws=[("BusinessRuleException", "invalid data")]
        )
        # Note: build_annotation escapes XML, so apostrophes become &apos;
        self.assertIn("Config(&apos;AppUrl&apos;)", ann)
        self.assertIn("strResult (String)", ann)
        self.assertIn("BusinessRuleException if invalid data", ann)


class TestCoreGenerators(unittest.TestCase):
    """Test core control flow generators."""

    def test_gen_sequence_basic(self):
        """Test basic sequence generation."""
        xaml = gen_sequence("My Sequence")
        self.assertIn('DisplayName="My Sequence"', xaml)
        self.assertIn("<Sequence", xaml)
        self.assertIn("</Sequence>", xaml)

    def test_gen_sequence_with_activities(self):
        """Test sequence with nested activities."""
        inner = gen_log_message("'Test message'", level="Info")
        xaml = gen_sequence("Outer", activities=[inner])
        self.assertIn("LogMessage", xaml)
        self.assertIn("Test message", xaml)

    def test_gen_sequence_with_variables(self):
        """Test sequence with variable declarations."""
        xaml = gen_sequence("With Vars", variables=[
            {"name": "strName", "type": "x:String"},
            {"name": "intCount", "type": "x:Int32", "default": "0"}
        ])
        self.assertIn("Sequence.Variables", xaml)
        self.assertIn('Name="strName"', xaml)
        self.assertIn('Name="intCount"', xaml)

    def test_gen_if_basic(self):
        """Test basic If generation."""
        xaml = gen_if("x > 10", [gen_log_message("'Greater'", "Info")])
        self.assertIn("Condition=\"[x > 10]\"", xaml)
        self.assertIn("If.Then", xaml)

    def test_gen_if_else(self):
        """Test If/Else generation."""
        xaml = gen_if_else(
            "isValid",
            [gen_log_message("'Valid'", "Info")],
            [gen_log_message("'Invalid'", "Warn")]
        )
        self.assertIn("If.Then", xaml)
        self.assertIn("If.Else", xaml)

    def test_gen_foreach(self):
        """Test ForEach generation."""
        xaml = gen_foreach(
            "dtData.Rows",
            "row",
            "sd:DataRow",
            [gen_log_message("row(\"Name\").ToString()", "Info")]
        )
        self.assertIn('x:TypeArguments="sd:DataRow"', xaml)
        self.assertIn('Name="row"', xaml)

    def test_gen_while(self):
        """Test While generation."""
        xaml = gen_while(
            "intCount < 10",
            [gen_assign("intCount", "intCount + 1", "x:Int32")]
        )
        self.assertIn("While", xaml)
        self.assertIn("Condition", xaml)

    def test_gen_switch(self):
        """Test Switch generation."""
        xaml = gen_switch(
            "strStatus",
            "x:String",
            {
                "Active": [gen_log_message("'Active'", "Info")],
                "Inactive": [gen_log_message("'Inactive'", "Warn")],
            }
        )
        self.assertIn("Switch", xaml)
        self.assertIn('x:Key="Active"', xaml)
        self.assertIn('x:Key="Inactive"', xaml)

    def test_gen_trycatch(self):
        """Test TryCatch generation."""
        xaml = gen_trycatch(
            try_activities=[gen_log_message("'Trying'", "Info")],
            catches=[{
                "type": "s:Exception",
                "variable": "ex",
                "activities": [gen_log_message("ex.Message", "Error")]
            }]
        )
        self.assertIn("TryCatch.Try", xaml)
        self.assertIn("TryCatch.Catches", xaml)
        self.assertIn('Name="ex"', xaml)

    def test_gen_assign(self):
        """Test Assign generation."""
        xaml = gen_assign("strResult", '"Hello"', "x:String")
        self.assertIn("Assign.To", xaml)
        self.assertIn("Assign.Value", xaml)
        self.assertIn("[strResult]", xaml)


class TestLoggingGenerators(unittest.TestCase):
    """Test logging generators."""

    def test_gen_log_message_info(self):
        """Test LogMessage with Info level."""
        xaml = gen_log_message("'Test message'", level="Info")
        self.assertIn('Level="Info"', xaml)
        self.assertIn("LogMessage", xaml)

    def test_gen_log_message_error(self):
        """Test LogMessage with Error level."""
        xaml = gen_log_message("strError", level="Error")
        self.assertIn('Level="Error"', xaml)

    def test_gen_log_message_invalid_level(self):
        """Test that invalid log level raises error."""
        with self.assertRaises(ValueError):
            gen_log_message("'Test'", level="Debug")

    def test_gen_comment(self):
        """Test Comment generation."""
        xaml = gen_comment("This is a comment")
        self.assertIn("ui:Comment", xaml)
        self.assertIn("This is a comment", xaml)


class TestOrchestratorGenerators(unittest.TestCase):
    """Test Orchestrator activity generators."""

    def test_gen_get_queue_item(self):
        """Test GetQueueItem generation."""
        xaml = gen_get_queue_item("MyQueue", "txItem")
        self.assertIn("GetQueueItem", xaml)
        self.assertIn("QueueName", xaml)
        self.assertNotIn("QueueType", xaml)  # Common hallucination

    def test_gen_set_transaction_status_success(self):
        """Test SetTransactionStatus for success."""
        xaml = gen_set_transaction_status("txItem", status="Successful")
        self.assertIn('Status="Successful"', xaml)

    def test_gen_set_transaction_status_failed(self):
        """Test SetTransactionStatus for failure."""
        xaml = gen_set_transaction_status(
            "txItem",
            status="Failed",
            reason="ex.Message",
            error_type="Business"
        )
        self.assertIn('Status="Failed"', xaml)
        self.assertIn('ErrorType="Business"', xaml)

    def test_gen_set_transaction_status_invalid(self):
        """Test that invalid status raises error."""
        with self.assertRaises(ValueError):
            gen_set_transaction_status("txItem", status="Error")

    def test_gen_get_credential(self):
        """Test GetRobotCredential generation."""
        xaml = gen_get_credential("MyAsset", "strUser", "secPass")
        self.assertIn("GetRobotCredential", xaml)
        self.assertIn("AssetName", xaml)
        self.assertIn("Username", xaml)
        self.assertIn("Password", xaml)


class TestErrorHandlingGenerators(unittest.TestCase):
    """Test error handling generators."""

    def test_gen_throw_business_exception(self):
        """Test throwing BusinessRuleException."""
        xaml = gen_throw("BusinessRuleException", "Invalid data")
        self.assertIn("Throw", xaml)
        self.assertIn("BusinessRuleException", xaml)
        # Should NOT be fully qualified
        self.assertNotIn("UiPath.Core.BusinessRuleException", xaml)

    def test_gen_throw_application_exception(self):
        """Test throwing ApplicationException."""
        xaml = gen_throw("ApplicationException", "System error")
        self.assertIn("ApplicationException", xaml)
        self.assertNotIn("System.ApplicationException", xaml)

    def test_gen_throw_invalid_type(self):
        """Test that invalid exception type raises error."""
        with self.assertRaises(ValueError):
            gen_throw("InvalidException", "Message")

    def test_gen_rethrow(self):
        """Test Rethrow generation."""
        xaml = gen_rethrow()
        self.assertIn("<Rethrow", xaml)

    def test_gen_retry_scope(self):
        """Test RetryScope generation."""
        xaml = gen_retry_scope(
            action_activities=[gen_log_message("'Trying'", "Info")],
            number_of_retries=3,
            retry_interval="00:00:05"
        )
        self.assertIn("RetryScope", xaml)
        self.assertIn('NumberOfRetries="3"', xaml)
        self.assertIn('RetryInterval="00:00:05"', xaml)


class TestUIAutomationGenerators(unittest.TestCase):
    """Test UI automation generators."""

    def test_gen_nclick(self):
        """Test NClick generation."""
        xaml = gen_nclick('<webctrl tag="BUTTON" />')
        self.assertIn("uix:NClick", xaml)
        self.assertIn('Version="V5"', xaml)  # Must be V5
        self.assertNotIn('Version="V3"', xaml)
        self.assertIn("uix:NClick.Target", xaml)

    def test_gen_nclick_invalid_click_type(self):
        """Test that invalid click type raises error."""
        with self.assertRaises(ValueError):
            gen_nclick('<webctrl />', click_type="Triple")

    def test_gen_ntypeinto(self):
        """Test NTypeInto generation."""
        xaml = gen_ntypeinto(
            '<webctrl id="email" />',
            "strEmail",
            empty_field_mode="SingleLine"
        )
        self.assertIn("uix:NTypeInto", xaml)
        self.assertIn('Version="V5"', xaml)
        self.assertIn('EmptyFieldMode="SingleLine"', xaml)
        self.assertIn('Text="[strEmail]"', xaml)

    def test_gen_ntypeinto_secure(self):
        """Test NTypeInto with SecureText."""
        xaml = gen_ntypeinto(
            '<webctrl id="password" />',
            "secPassword",
            is_secure=True
        )
        self.assertIn("SecureText=", xaml)
        # Check that plain Text attribute is not present (note: SecureText contains "Text")
        self.assertNotIn('\n  Text="', xaml)

    def test_gen_ntypeinto_invalid_empty_mode(self):
        """Test that invalid empty field mode raises error."""
        with self.assertRaises(ValueError):
            gen_ntypeinto('<webctrl />', "text", empty_field_mode="Clear")

    def test_gen_ngettext(self):
        """Test NGetText generation."""
        xaml = gen_ngettext('<webctrl />', "strResult")
        self.assertIn("uix:NGetText", xaml)
        self.assertIn('Value="[strResult]"', xaml)
        self.assertNotIn("Result=", xaml)  # Common hallucination

    def test_gen_napplication_card(self):
        """Test NApplicationCard generation."""
        xaml = gen_napplication_card(
            "strUrl",
            body_activities=[gen_nclick('<webctrl />')],
            open_mode="Always",
            is_incognito=True
        )
        self.assertIn("uix:NApplicationCard", xaml)
        self.assertIn('OpenMode="Always"', xaml)
        self.assertIn('IsIncognito="True"', xaml)
        self.assertIn("uix:NApplicationCard.Body", xaml)

    def test_gen_napplication_card_invalid_mode(self):
        """Test that invalid open mode raises error."""
        with self.assertRaises(ValueError):
            gen_napplication_card("url", [], open_mode="Auto")


class TestDataGenerators(unittest.TestCase):
    """Test data operation generators."""

    def test_gen_build_datatable(self):
        """Test BuildDataTable generation."""
        xaml = gen_build_datatable(
            "dtResult",
            columns=[
                {"name": "Name", "type": "String"},
                {"name": "Amount", "type": "Double"}
            ]
        )
        self.assertIn("BuildDataTable", xaml)
        self.assertIn('ColumnName="Name"', xaml)
        self.assertIn("System.Double", xaml)


class TestXMLValidity(unittest.TestCase):
    """Test that all generators produce valid XML."""

    def _wrap_in_activity(self, xaml: str) -> str:
        """Wrap XAML snippet in minimal Activity element for parsing."""
        return f'''<?xml version="1.0" encoding="utf-8"?>
<Activity
  xmlns="http://schemas.microsoft.com/netfx/2009/xaml/activities"
  xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
  xmlns:s="clr-namespace:System;assembly=mscorlib"
  xmlns:scg="clr-namespace:System.Collections.Generic;assembly=mscorlib"
  xmlns:sd="clr-namespace:System.Data;assembly=System.Data"
  xmlns:ui="http://schemas.uipath.com/workflow/activities"
  xmlns:uix="clr-namespace:UiPath.UIAutomationNext.Activities;assembly=UiPath.UIAutomationNext.Activities"
  xmlns:sap2010="http://schemas.microsoft.com/netfx/2010/xaml/activities/presentation">
  <Sequence>
    {xaml}
  </Sequence>
</Activity>'''

    def test_log_message_xml_valid(self):
        """Test LogMessage produces valid XML."""
        xaml = self._wrap_in_activity(gen_log_message("'Test'", "Info"))
        ET.fromstring(xaml)  # Should not raise

    def test_sequence_xml_valid(self):
        """Test Sequence produces valid XML."""
        xaml = self._wrap_in_activity(gen_sequence("Test"))
        ET.fromstring(xaml)

    def test_if_xml_valid(self):
        """Test If produces valid XML."""
        xaml = self._wrap_in_activity(gen_if("True", []))
        ET.fromstring(xaml)

    def test_trycatch_xml_valid(self):
        """Test TryCatch produces valid XML."""
        xaml = self._wrap_in_activity(gen_trycatch([]))
        ET.fromstring(xaml)

    def test_nclick_xml_valid(self):
        """Test NClick produces valid XML."""
        xaml = self._wrap_in_activity(gen_nclick('<webctrl />'))
        ET.fromstring(xaml)


if __name__ == "__main__":
    unittest.main(verbosity=2)
