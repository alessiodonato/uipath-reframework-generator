"""
Logging and comment generators.
"""

from typing import Optional, List, Dict
from .helpers import escape_xml


def gen_log_message(
    message: str,
    level: str = "Info",
    display_name: Optional[str] = None,
    annotation: Optional[str] = None,
    indent: str = ""
) -> str:
    """
    Generate a LogMessage activity.

    Args:
        message: VB.NET expression for the message (will be wrapped in [])
        level: Log level - Trace, Info, Warn, Error, Fatal
        display_name: Optional display name
        annotation: Optional annotation
    """
    # Validate level
    valid_levels = {"Trace", "Info", "Warn", "Error", "Fatal"}
    if level not in valid_levels:
        raise ValueError(f"Invalid log level '{level}'. Must be one of: {valid_levels}")

    # Wrap message in brackets if it's a string literal or expression
    if not message.startswith("["):
        # Check if it's a string literal (starts with quote)
        if message.startswith('"') or message.startswith("'"):
            message = f"[{message}]"
        else:
            # Assume it's an expression
            message = f"[{message}]"

    name = display_name or f"Log: {message[1:31]}..." if len(message) > 35 else f"Log: {message[1:-1]}"
    ann_attr = f' sap2010:Annotation.AnnotationText="{escape_xml(annotation)}"' if annotation else ""

    return f"""{indent}<ui:LogMessage
{indent}  Level="{level}"
{indent}  Message="{message}"
{indent}  DisplayName="{escape_xml(name)}"{ann_attr} />"""


def gen_log_bookend_start(
    workflow_name: str,
    process_name: str,
    level: str = "Trace",
    indent: str = ""
) -> str:
    """Generate a log message for workflow start (bookend pattern)."""
    message = f"'[{process_name}] {workflow_name} - Started'"
    return gen_log_message(
        message=message,
        level=level,
        display_name=f"Log: {workflow_name} started",
        indent=indent
    )


def gen_log_bookend_end(
    workflow_name: str,
    process_name: str,
    level: str = "Trace",
    indent: str = ""
) -> str:
    """Generate a log message for workflow end (bookend pattern)."""
    message = f"'[{process_name}] {workflow_name} - Completed'"
    return gen_log_message(
        message=message,
        level=level,
        display_name=f"Log: {workflow_name} completed",
        indent=indent
    )


def gen_add_log_fields(
    fields: Dict[str, str],
    display_name: str = "Add Log Fields",
    annotation: Optional[str] = None,
    indent: str = ""
) -> str:
    """
    Generate an AddLogFields activity.

    Args:
        fields: Dict of {field_name: expression}
    """
    ann_attr = f' sap2010:Annotation.AnnotationText="{escape_xml(annotation)}"' if annotation else ""

    fields_xml = ""
    for name, value in fields.items():
        if not value.startswith("["):
            value = f"[{value}]"
        fields_xml += f"""
{indent}    <ui:LogField Name="{escape_xml(name)}" Value="{value}" />"""

    return f"""{indent}<ui:AddLogFields DisplayName="{escape_xml(display_name)}"{ann_attr}>
{indent}  <ui:AddLogFields.Fields>{fields_xml}
{indent}  </ui:AddLogFields.Fields>
{indent}</ui:AddLogFields>"""


def gen_remove_log_fields(
    field_names: List[str],
    display_name: str = "Remove Log Fields",
    annotation: Optional[str] = None,
    indent: str = ""
) -> str:
    """
    Generate a RemoveLogFields activity.

    Args:
        field_names: List of field names to remove
    """
    ann_attr = f' sap2010:Annotation.AnnotationText="{escape_xml(annotation)}"' if annotation else ""

    names_xml = ", ".join(f'"{name}"' for name in field_names)

    return f"""{indent}<ui:RemoveLogFields
{indent}  FieldNames="{{x:Array Type=x:String}}{{{names_xml}}}"
{indent}  DisplayName="{escape_xml(display_name)}"{ann_attr} />"""


def gen_comment(
    text: str,
    display_name: Optional[str] = None,
    indent: str = ""
) -> str:
    """
    Generate a Comment activity.

    Args:
        text: Comment text
    """
    name = display_name or text[:40] + "..." if len(text) > 40 else text

    return f"""{indent}<ui:Comment
{indent}  Text="{escape_xml(text)}"
{indent}  DisplayName="{escape_xml(name)}" />"""


def gen_comment_out(
    activities: List[str],
    display_name: str = "Commented Out",
    annotation: Optional[str] = None,
    indent: str = ""
) -> str:
    """
    Generate a CommentOut activity (disables contained activities).

    Args:
        activities: Activities to comment out
    """
    ann_attr = f' sap2010:Annotation.AnnotationText="{escape_xml(annotation)}"' if annotation else ""

    from .helpers import indent_xml
    content = "\n".join(indent_xml(a, 4) for a in activities)

    return f"""{indent}<ui:CommentOut DisplayName="{escape_xml(display_name)}"{ann_attr}>
{indent}  <Sequence DisplayName="Disabled">
{content}
{indent}  </Sequence>
{indent}</ui:CommentOut>"""
