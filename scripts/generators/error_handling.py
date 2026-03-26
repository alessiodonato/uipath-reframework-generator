"""
Error handling generators: Throw, Rethrow, RetryScope.
"""

from typing import Optional, List
from .helpers import escape_xml


def gen_throw(
    exception_type: str,
    message: str,
    display_name: Optional[str] = None,
    annotation: Optional[str] = None,
    indent: str = ""
) -> str:
    """
    Generate a Throw activity.

    Args:
        exception_type: Exception type (BusinessRuleException or ApplicationException)
        message: VB.NET expression for error message
    """
    # Validate exception type
    valid_types = {"BusinessRuleException", "ApplicationException", "Exception"}
    if exception_type not in valid_types:
        raise ValueError(f"Invalid exception type '{exception_type}'. Use: {valid_types}")

    name = display_name or f"Throw {exception_type}"
    ann_attr = f'\n{indent}  sap2010:Annotation.AnnotationText="{escape_xml(annotation)}"' if annotation else ""

    # Build exception expression
    if message.startswith("["):
        # It's an expression
        msg_expr = message[1:-1] if message.endswith("]") else message[1:]
    elif message.startswith('"'):
        # It's a string literal
        msg_expr = message
    else:
        # Wrap as string
        msg_expr = f'"{escape_xml(message)}"'

    exception_expr = f"New {exception_type}({msg_expr})"

    return f"""{indent}<Throw
{indent}  DisplayName="{escape_xml(name)}"{ann_attr}
{indent}  Exception="[{exception_expr}]" />"""


def gen_throw_business_exception(
    message: str,
    display_name: Optional[str] = None,
    annotation: Optional[str] = None,
    indent: str = ""
) -> str:
    """Convenience function for throwing BusinessRuleException."""
    return gen_throw(
        exception_type="BusinessRuleException",
        message=message,
        display_name=display_name or "Throw BusinessRuleException",
        annotation=annotation,
        indent=indent
    )


def gen_throw_application_exception(
    message: str,
    display_name: Optional[str] = None,
    annotation: Optional[str] = None,
    indent: str = ""
) -> str:
    """Convenience function for throwing ApplicationException."""
    return gen_throw(
        exception_type="ApplicationException",
        message=message,
        display_name=display_name or "Throw ApplicationException",
        annotation=annotation,
        indent=indent
    )


def gen_rethrow(
    display_name: str = "Rethrow",
    annotation: Optional[str] = None,
    indent: str = ""
) -> str:
    """
    Generate a Rethrow activity.

    Used in Catch blocks to propagate the exception up the call stack.
    """
    ann_attr = f' sap2010:Annotation.AnnotationText="{escape_xml(annotation)}"' if annotation else ""

    return f"""{indent}<Rethrow DisplayName="{escape_xml(display_name)}"{ann_attr} />"""


def gen_retry_scope(
    action_activities: List[str],
    condition_activities: Optional[List[str]] = None,
    number_of_retries: int = 3,
    retry_interval: str = "00:00:05",
    display_name: str = "Retry Scope",
    annotation: Optional[str] = None,
    indent: str = ""
) -> str:
    """
    Generate a RetryScope activity.

    Args:
        action_activities: Activities to execute (will be retried)
        condition_activities: Optional condition check activities
        number_of_retries: Number of retry attempts
        retry_interval: TimeSpan for retry interval (default 5 seconds)
    """
    ann_attr = f'\n{indent}  sap2010:Annotation.AnnotationText="{escape_xml(annotation)}"' if annotation else ""

    from .helpers import indent_xml
    action_content = "\n".join(indent_xml(a, 6) for a in action_activities)

    condition_xml = ""
    if condition_activities:
        condition_content = "\n".join(indent_xml(a, 6) for a in condition_activities)
        condition_xml = f"""
{indent}  <ui:RetryScope.Condition>
{indent}    <ActivityAction>
{indent}      <Sequence DisplayName="Condition">
{condition_content}
{indent}      </Sequence>
{indent}    </ActivityAction>
{indent}  </ui:RetryScope.Condition>"""

    return f"""{indent}<ui:RetryScope
{indent}  DisplayName="{escape_xml(display_name)}"{ann_attr}
{indent}  NumberOfRetries="{number_of_retries}"
{indent}  RetryInterval="{retry_interval}">
{indent}  <ui:RetryScope.Action>
{indent}    <ActivityAction>
{indent}      <Sequence DisplayName="Action">
{action_content}
{indent}      </Sequence>
{indent}    </ActivityAction>
{indent}  </ui:RetryScope.Action>{condition_xml}
{indent}</ui:RetryScope>"""


def gen_terminate_workflow(
    reason: str,
    exception: Optional[str] = None,
    display_name: str = "Terminate Workflow",
    annotation: Optional[str] = None,
    indent: str = ""
) -> str:
    """
    Generate a TerminateWorkflow activity.

    Args:
        reason: Reason for termination
        exception: Optional exception expression
    """
    ann_attr = f'\n{indent}  sap2010:Annotation.AnnotationText="{escape_xml(annotation)}"' if annotation else ""

    if not reason.startswith("["):
        reason = f"[{reason}]" if not reason.startswith('"') else f"[{reason}]"

    exception_attr = ""
    if exception:
        if not exception.startswith("["):
            exception = f"[{exception}]"
        exception_attr = f'\n{indent}  Exception="{exception}"'

    return f"""{indent}<TerminateWorkflow
{indent}  DisplayName="{escape_xml(display_name)}"{ann_attr}
{indent}  Reason="{reason}"{exception_attr} />"""
