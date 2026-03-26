#!/usr/bin/env python3
"""
Framework Wiring for UiPath ReFramework Projects.

Automates common framework modifications:
- Wire UiElement arguments across workflow chain
- Insert InvokeWorkflowFile calls
- Add variables to workflows
- Replace SCAFFOLD markers with generated XAML

Usage:
    # Wire UiElement for an app across all framework files
    python modify_framework.py wire-uielement ./MyProject WebApp

    # Insert an invoke call into a workflow
    python modify_framework.py insert-invoke ./Process.xaml "Business/Step1.xaml"

    # Add variables to a workflow
    python modify_framework.py add-variables ./Main.xaml strName:String intCount:Int32

    # List available markers in a file
    python modify_framework.py list-markers ./GetTransactionData.xaml
"""

import argparse
import re
import sys
from pathlib import Path
from typing import List, Optional, Dict, Tuple


# ═══════════════════════════════════════════════════════════════════════════════
# WIRE UIELEMENT
# ═══════════════════════════════════════════════════════════════════════════════

def wire_uielement(project_dir: str, app_name: str) -> bool:
    """
    Wire UiElement argument chain for an application.

    This adds:
    - out_ui{AppName} (OutArgument) to InitAllApplications.xaml
    - ui{AppName} (Variable) to Main.xaml
    - io_ui{AppName} (InOutArgument) to Process.xaml
    - in_ui{AppName} (InArgument) to CloseAllApplications.xaml

    Args:
        project_dir: Path to project directory
        app_name: Application name (PascalCase)

    Returns:
        True if changes were made
    """
    project_path = Path(project_dir)
    var_name = f"ui{app_name}"

    changes = []

    # 1. InitAllApplications.xaml - add OutArgument
    init_apps = project_path / "Framework" / "InitAllApplications.xaml"
    if init_apps.exists():
        content = init_apps.read_text(encoding="utf-8")
        if f"out_{var_name}" not in content:
            # Add OutArgument to x:Members
            arg_xml = f'''    <x:Property Name="out_{var_name}" Type="OutArgument(uix:UiElement)"
      sap2010:Annotation.AnnotationText="UiElement for {app_name} browser/app instance" />'''

            content = _add_to_xmembers(content, arg_xml)
            init_apps.write_text(content, encoding="utf-8")
            changes.append(f"InitAllApplications.xaml: added out_{var_name}")

    # 2. Main.xaml - add Variable
    main_xaml = project_path / "Main.xaml"
    if main_xaml.exists():
        content = main_xaml.read_text(encoding="utf-8")
        if f'Name="{var_name}"' not in content:
            # Add Variable to StateMachine.Variables or first Sequence.Variables
            var_xml = f'<Variable x:TypeArguments="uix:UiElement" Name="{var_name}" />'
            content = _add_variable(content, var_xml)
            main_xaml.write_text(content, encoding="utf-8")
            changes.append(f"Main.xaml: added variable {var_name}")

    # 3. Process.xaml - add InOutArgument
    process_xaml = project_path / "Process.xaml"
    if process_xaml.exists():
        content = process_xaml.read_text(encoding="utf-8")
        if f"io_{var_name}" not in content:
            arg_xml = f'''    <x:Property Name="io_{var_name}" Type="InOutArgument(uix:UiElement)"
      sap2010:Annotation.AnnotationText="UiElement for {app_name} - passed to action workflows" />'''

            content = _add_to_xmembers(content, arg_xml)
            process_xaml.write_text(content, encoding="utf-8")
            changes.append(f"Process.xaml: added io_{var_name}")

    # 4. CloseAllApplications.xaml - add InArgument
    close_apps = project_path / "Framework" / "CloseAllApplications.xaml"
    if close_apps.exists():
        content = close_apps.read_text(encoding="utf-8")
        if f"in_{var_name}" not in content:
            arg_xml = f'''    <x:Property Name="in_{var_name}" Type="InArgument(uix:UiElement)"
      sap2010:Annotation.AnnotationText="UiElement for {app_name} - used to close the app" />'''

            content = _add_to_xmembers(content, arg_xml)
            close_apps.write_text(content, encoding="utf-8")
            changes.append(f"CloseAllApplications.xaml: added in_{var_name}")

    # Report
    if changes:
        print(f"Wired UiElement chain for {app_name}:")
        for change in changes:
            print(f"  - {change}")
        return True
    else:
        print(f"UiElement chain for {app_name} already exists")
        return False


# ═══════════════════════════════════════════════════════════════════════════════
# INSERT INVOKE
# ═══════════════════════════════════════════════════════════════════════════════

def insert_invoke(
    xaml_file: str,
    workflow_path: str,
    arguments: Optional[Dict[str, str]] = None,
    position: str = "end"
) -> bool:
    """
    Insert an InvokeWorkflowFile call into a workflow.

    Args:
        xaml_file: Path to XAML file to modify
        workflow_path: Relative path to workflow to invoke
        arguments: Optional dict of {arg_name: expression}
        position: "end" (before </Sequence>) or "start" (after <Sequence>)

    Returns:
        True if changes were made
    """
    from generators.invoke import gen_invoke_workflow_simple

    path = Path(xaml_file)
    if not path.exists():
        print(f"Error: {xaml_file} not found", file=sys.stderr)
        return False

    content = path.read_text(encoding="utf-8")

    # Generate invoke XAML
    invoke_xml = gen_invoke_workflow_simple(
        workflow_path=workflow_path,
        in_config=True,
        in_transaction_item="TransactionItem" in content or "Process" in str(path),
        indent="    "
    )

    # Find insertion point
    if position == "end":
        # Insert before the last </Sequence>
        match = re.search(r'(\s*)</Sequence>\s*</Activity>', content)
        if match:
            indent = match.group(1)
            insert_pos = match.start()
            content = content[:insert_pos] + "\n" + invoke_xml + content[insert_pos:]
    else:
        # Insert after first <Sequence ...>
        match = re.search(r'(<Sequence[^>]*>)', content)
        if match:
            insert_pos = match.end()
            content = content[:insert_pos] + "\n" + invoke_xml + content[insert_pos:]

    path.write_text(content, encoding="utf-8")
    print(f"Inserted invoke to {workflow_path} in {xaml_file}")
    return True


# ═══════════════════════════════════════════════════════════════════════════════
# ADD VARIABLES
# ═══════════════════════════════════════════════════════════════════════════════

def add_variables(xaml_file: str, variables: List[str]) -> bool:
    """
    Add variables to a workflow.

    Args:
        xaml_file: Path to XAML file
        variables: List of "name:type" strings

    Returns:
        True if changes were made
    """
    path = Path(xaml_file)
    if not path.exists():
        print(f"Error: {xaml_file} not found", file=sys.stderr)
        return False

    content = path.read_text(encoding="utf-8")
    added = []

    for var_spec in variables:
        if ":" not in var_spec:
            print(f"Warning: Invalid variable spec '{var_spec}' (use name:type)", file=sys.stderr)
            continue

        name, var_type = var_spec.split(":", 1)
        xaml_type = _map_type(var_type)

        # Check if already exists
        if f'Name="{name}"' in content:
            print(f"  Skip: {name} already exists")
            continue

        var_xml = f'<Variable x:TypeArguments="{xaml_type}" Name="{name}" />'
        content = _add_variable(content, var_xml)
        added.append(f"{name} ({xaml_type})")

    if added:
        path.write_text(content, encoding="utf-8")
        print(f"Added variables to {xaml_file}:")
        for var in added:
            print(f"  - {var}")
        return True

    return False


# ═══════════════════════════════════════════════════════════════════════════════
# REPLACE MARKER
# ═══════════════════════════════════════════════════════════════════════════════

def replace_marker(xaml_file: str, marker: str, replacement_xaml: str) -> bool:
    """
    Replace a SCAFFOLD marker with generated XAML.

    Markers are XML comments like: <!-- SCAFFOLD:MARKER_NAME -->

    Args:
        xaml_file: Path to XAML file
        marker: Marker name (e.g., "PROCESS_BODY")
        replacement_xaml: XAML to insert

    Returns:
        True if changes were made
    """
    path = Path(xaml_file)
    if not path.exists():
        print(f"Error: {xaml_file} not found", file=sys.stderr)
        return False

    content = path.read_text(encoding="utf-8")

    # Find marker
    marker_pattern = rf'<!--\s*SCAFFOLD:{marker}\s*-->'
    match = re.search(marker_pattern, content)

    if not match:
        print(f"Marker 'SCAFFOLD:{marker}' not found in {xaml_file}", file=sys.stderr)
        return False

    # Replace marker with content
    content = content[:match.start()] + replacement_xaml + content[match.end():]
    path.write_text(content, encoding="utf-8")
    print(f"Replaced marker SCAFFOLD:{marker} in {xaml_file}")
    return True


def list_markers(xaml_file: str) -> List[str]:
    """
    List all SCAFFOLD markers in a file.

    Args:
        xaml_file: Path to XAML file

    Returns:
        List of marker names
    """
    path = Path(xaml_file)
    if not path.exists():
        print(f"Error: {xaml_file} not found", file=sys.stderr)
        return []

    content = path.read_text(encoding="utf-8")

    markers = re.findall(r'<!--\s*SCAFFOLD:(\w+)\s*-->', content)

    if markers:
        print(f"Markers in {xaml_file}:")
        for marker in markers:
            print(f"  - SCAFFOLD:{marker}")
    else:
        print(f"No SCAFFOLD markers found in {xaml_file}")

    return markers


# ═══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def _add_to_xmembers(content: str, arg_xml: str) -> str:
    """Add an argument to x:Members block."""
    # Find </x:Members>
    match = re.search(r'(\s*)</x:Members>', content)
    if match:
        indent = match.group(1)
        insert_pos = match.start()
        return content[:insert_pos] + "\n" + arg_xml + content[insert_pos:]
    return content


def _add_variable(content: str, var_xml: str) -> str:
    """Add a variable to Sequence.Variables or StateMachine.Variables."""
    # Try Sequence.Variables first
    patterns = [
        r'(<Sequence\.Variables>)',
        r'(<StateMachine\.Variables>)',
        r'(<Flowchart\.Variables>)',
    ]

    for pattern in patterns:
        match = re.search(pattern, content)
        if match:
            insert_pos = match.end()
            return content[:insert_pos] + "\n      " + var_xml + content[insert_pos:]

    # No variables block found - need to create one
    # Find first <Sequence or <StateMachine after x:Members
    seq_match = re.search(r'(<Sequence[^>]*>)', content)
    if seq_match:
        insert_pos = seq_match.end()
        vars_block = f"\n    <Sequence.Variables>\n      {var_xml}\n    </Sequence.Variables>"
        return content[:insert_pos] + vars_block + content[insert_pos:]

    return content


def _map_type(type_str: str) -> str:
    """Map simple type name to XAML type."""
    mapping = {
        "String": "x:String",
        "string": "x:String",
        "Int32": "x:Int32",
        "int": "x:Int32",
        "Integer": "x:Int32",
        "Boolean": "x:Boolean",
        "bool": "x:Boolean",
        "DateTime": "s:DateTime",
        "DataTable": "sd:DataTable",
        "DataRow": "sd:DataRow",
        "Object": "x:Object",
        "QueueItem": "ui:QueueItem",
        "UiElement": "uix:UiElement",
        "Dictionary": "scg:Dictionary(x:String, x:Object)",
    }
    return mapping.get(type_str, type_str)


# ═══════════════════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Framework wiring for UiPath ReFramework projects",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command")

    # wire-uielement command
    wire_parser = subparsers.add_parser("wire-uielement",
                                        help="Wire UiElement chain for an app")
    wire_parser.add_argument("project", help="Path to project directory")
    wire_parser.add_argument("app_name", help="Application name (PascalCase)")

    # insert-invoke command
    invoke_parser = subparsers.add_parser("insert-invoke",
                                          help="Insert InvokeWorkflowFile call")
    invoke_parser.add_argument("xaml_file", help="Path to XAML file to modify")
    invoke_parser.add_argument("workflow_path", help="Path to workflow to invoke")
    invoke_parser.add_argument("--position", "-p", choices=["start", "end"],
                              default="end", help="Insertion position")

    # add-variables command
    vars_parser = subparsers.add_parser("add-variables",
                                        help="Add variables to a workflow")
    vars_parser.add_argument("xaml_file", help="Path to XAML file")
    vars_parser.add_argument("variables", nargs="+",
                            help="Variables as name:type pairs")

    # replace-marker command
    marker_parser = subparsers.add_parser("replace-marker",
                                          help="Replace SCAFFOLD marker with XAML")
    marker_parser.add_argument("xaml_file", help="Path to XAML file")
    marker_parser.add_argument("marker", help="Marker name")
    marker_parser.add_argument("xaml", help="XAML content or @file")

    # list-markers command
    list_parser = subparsers.add_parser("list-markers",
                                        help="List SCAFFOLD markers in file")
    list_parser.add_argument("xaml_file", help="Path to XAML file")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "wire-uielement":
        wire_uielement(args.project, args.app_name)
    elif args.command == "insert-invoke":
        insert_invoke(args.xaml_file, args.workflow_path, position=args.position)
    elif args.command == "add-variables":
        add_variables(args.xaml_file, args.variables)
    elif args.command == "replace-marker":
        xaml = args.xaml
        if xaml.startswith("@"):
            xaml = Path(xaml[1:]).read_text(encoding="utf-8")
        replace_marker(args.xaml_file, args.marker, xaml)
    elif args.command == "list-markers":
        list_markers(args.xaml_file)


if __name__ == "__main__":
    main()
