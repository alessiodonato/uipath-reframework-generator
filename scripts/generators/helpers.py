"""
Helper functions for XAML generation.
"""

import uuid
import re
from typing import Dict, List, Optional, Tuple


def escape_xml(text: str) -> str:
    """Escape text for use in XML attributes and content."""
    if not text:
        return ""
    return (text
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
        .replace("\n", "&#xA;")
        .replace("\r", "&#xD;")
        .replace("\t", "&#x9;"))


def escape_vb_string(text: str) -> str:
    """Escape text for use in VB.NET string literals."""
    if not text:
        return ""
    return text.replace('"', '""')


def generate_guid() -> str:
    """Generate a new GUID for XAML IdRef."""
    return str(uuid.uuid4())


def generate_short_id() -> str:
    """Generate a short ID for internal references."""
    return uuid.uuid4().hex[:8]


def build_annotation(
    reads: Optional[List[str]] = None,
    output: Optional[List[Tuple[str, str]]] = None,
    throws: Optional[List[Tuple[str, str]]] = None,
    description: Optional[str] = None
) -> str:
    """
    Build a rich annotation string in standard format.

    Args:
        reads: List of Config keys or inputs read
        output: List of (variable_name, type) tuples
        throws: List of (exception_type, condition) tuples
        description: Optional description text

    Returns:
        Formatted annotation string
    """
    parts = []

    if description:
        parts.append(description)

    # Reads section
    if reads:
        reads_str = ", ".join(f"Config('{k}')" if not k.startswith("in_") else k for k in reads)
        parts.append(f"Reads: {reads_str}")
    else:
        parts.append("Reads: N/A")

    # Output section
    if output:
        output_str = ", ".join(f"{name} ({typ})" for name, typ in output)
        parts.append(f"Output: {output_str}")
    else:
        parts.append("Output: N/A")

    # Throws section
    if throws:
        throws_str = ", ".join(f"{exc} if {cond}" for exc, cond in throws)
        parts.append(f"Throws: {throws_str}")
    else:
        parts.append("Throws: N/A")

    return escape_xml(" | ".join(parts))


def vb_type(type_str: str) -> str:
    """Map simple type names to VB.NET XAML type arguments."""
    mapping = {
        "String": "x:String",
        "string": "x:String",
        "Int32": "x:Int32",
        "Integer": "x:Int32",
        "int": "x:Int32",
        "Boolean": "x:Boolean",
        "Bool": "x:Boolean",
        "bool": "x:Boolean",
        "DateTime": "s:DateTime",
        "Date": "s:DateTime",
        "DataTable": "sd:DataTable",
        "Table": "sd:DataTable",
        "DataRow": "sd:DataRow",
        "Double": "x:Double",
        "Decimal": "x:Decimal",
        "Float": "x:Double",
        "Object": "x:Object",
        "QueueItem": "ui:QueueItem",
        "SecureString": "s:Security.SecureString",
        "UiElement": "uix:UiElement",
    }
    return mapping.get(type_str, mapping.get(type_str.capitalize(), "x:Object"))


def indent_xml(xml: str, spaces: int = 2) -> str:
    """Indent XML content by specified number of spaces."""
    indent = " " * spaces
    lines = xml.split("\n")
    return "\n".join(indent + line if line.strip() else line for line in lines)


def wrap_in_sequence(activities: List[str], display_name: str = "Sequence") -> str:
    """Wrap multiple activities in a Sequence container."""
    from .core import gen_sequence
    return gen_sequence(display_name=display_name, activities=activities)


# ═══════════════════════════════════════════════════════════════════════════════
# TYPE MAPPINGS
# ═══════════════════════════════════════════════════════════════════════════════

TYPE_TO_XAML = {
    "String": "x:String",
    "Int32": "x:Int32",
    "Integer": "x:Int32",
    "Boolean": "x:Boolean",
    "Double": "x:Double",
    "Decimal": "x:Decimal",
    "DateTime": "s:DateTime",
    "TimeSpan": "s:TimeSpan",
    "Object": "x:Object",
    "DataTable": "sd:DataTable",
    "DataRow": "sd:DataRow",
    "QueueItem": "ui:QueueItem",
    "SecureString": "s:Security.SecureString",
    "Dictionary": "scg:Dictionary(x:String, x:Object)",
    "List<String>": "scg:List(x:String)",
    "Array<String>": "x:String[]",
    "UiElement": "uix:UiElement",
    "Browser": "uix:Browser",
}

XAML_NAMESPACES = {
    "x": "http://schemas.microsoft.com/winfx/2006/xaml",
    "s": "clr-namespace:System;assembly=mscorlib",
    "scg": "clr-namespace:System.Collections.Generic;assembly=mscorlib",
    "sd": "clr-namespace:System.Data;assembly=System.Data",
    "ui": "http://schemas.uipath.com/workflow/activities",
    "uix": "clr-namespace:UiPath.UIAutomationNext.Activities;assembly=UiPath.UIAutomationNext.Activities",
    "sap2010": "http://schemas.microsoft.com/netfx/2010/xaml/activities/presentation",
}


def get_required_namespaces(xaml_content: str) -> Dict[str, str]:
    """Determine which namespaces are needed based on content."""
    required = {
        "xmlns": "http://schemas.microsoft.com/netfx/2009/xaml/activities",
        "xmlns:x": "http://schemas.microsoft.com/winfx/2006/xaml",
    }

    # Check for namespace usage
    if "sd:" in xaml_content or "DataTable" in xaml_content:
        required["xmlns:sd"] = XAML_NAMESPACES["sd"]

    if "scg:" in xaml_content or "Dictionary" in xaml_content:
        required["xmlns:scg"] = XAML_NAMESPACES["scg"]

    if "ui:" in xaml_content or "LogMessage" in xaml_content:
        required["xmlns:ui"] = XAML_NAMESPACES["ui"]

    if "uix:" in xaml_content or "NClick" in xaml_content:
        required["xmlns:uix"] = XAML_NAMESPACES["uix"]

    if "sap2010:" in xaml_content or "Annotation" in xaml_content:
        required["xmlns:sap2010"] = XAML_NAMESPACES["sap2010"]

    if "s:" in xaml_content or "DateTime" in xaml_content:
        required["xmlns:s"] = XAML_NAMESPACES["s"]

    return required
