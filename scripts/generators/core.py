"""
Core control flow generators: Sequence, If, ForEach, While, Switch, TryCatch.
"""

from typing import List, Optional, Dict, Any
from .helpers import escape_xml, generate_guid, build_annotation, indent_xml


def gen_sequence(
    display_name: str,
    activities: Optional[List[str]] = None,
    variables: Optional[List[Dict[str, str]]] = None,
    annotation: Optional[str] = None,
    indent: str = ""
) -> str:
    """
    Generate a Sequence activity.

    Args:
        display_name: Display name for the sequence
        activities: List of activity XAML strings
        variables: List of {"name": str, "type": str, "default": str?} dicts
        annotation: Optional annotation text
        indent: Indentation prefix
    """
    # Build variables block
    vars_xml = ""
    if variables:
        var_items = []
        for var in variables:
            var_type = var.get("type", "x:String")
            default = var.get("default", "")
            default_attr = f' Default="{escape_xml(default)}"' if default else ""
            var_items.append(
                f'<Variable x:TypeArguments="{var_type}" Name="{var["name"]}"{default_attr} />'
            )
        vars_xml = f"""
{indent}  <Sequence.Variables>
{indent}    {"".join(var_items)}
{indent}  </Sequence.Variables>"""

    # Build annotation
    annotation_attr = ""
    if annotation:
        annotation_attr = f'\n{indent}  sap2010:Annotation.AnnotationText="{escape_xml(annotation)}"'

    # Build activities content
    activities_xml = ""
    if activities:
        activities_xml = "\n" + "\n".join(
            indent_xml(a, len(indent) + 4) for a in activities
        ) + "\n" + indent

    return f"""{indent}<Sequence
{indent}  DisplayName="{escape_xml(display_name)}"{annotation_attr}>{vars_xml}
{activities_xml}</Sequence>"""


def gen_if(
    condition: str,
    then_activities: List[str],
    else_activities: Optional[List[str]] = None,
    display_name: Optional[str] = None,
    annotation: Optional[str] = None,
    indent: str = ""
) -> str:
    """
    Generate an If activity.

    Args:
        condition: VB.NET condition expression (will be wrapped in [])
        then_activities: Activities for Then branch
        else_activities: Activities for Else branch (optional)
        display_name: Display name
        annotation: Optional annotation
    """
    name = display_name or f"If {condition[:30]}..."
    ann_attr = f' sap2010:Annotation.AnnotationText="{escape_xml(annotation)}"' if annotation else ""

    # Ensure condition is wrapped in brackets
    if not condition.startswith("["):
        condition = f"[{condition}]"

    then_content = "\n".join(indent_xml(a, 6) for a in then_activities)
    else_xml = ""
    if else_activities:
        else_content = "\n".join(indent_xml(a, 6) for a in else_activities)
        else_xml = f"""
{indent}  <If.Else>
{indent}    <Sequence DisplayName="Else">
{else_content}
{indent}    </Sequence>
{indent}  </If.Else>"""

    return f"""{indent}<If Condition="{condition}" DisplayName="{escape_xml(name)}"{ann_attr}>
{indent}  <If.Then>
{indent}    <Sequence DisplayName="Then">
{then_content}
{indent}    </Sequence>
{indent}  </If.Then>{else_xml}
{indent}</If>"""


def gen_if_else(
    condition: str,
    then_activities: List[str],
    else_activities: List[str],
    display_name: Optional[str] = None,
    annotation: Optional[str] = None,
    indent: str = ""
) -> str:
    """Convenience wrapper for If with Else branch."""
    return gen_if(condition, then_activities, else_activities, display_name, annotation, indent)


def gen_foreach(
    values: str,
    item_name: str,
    item_type: str,
    body_activities: List[str],
    display_name: Optional[str] = None,
    annotation: Optional[str] = None,
    indent: str = ""
) -> str:
    """
    Generate a ForEach activity.

    Args:
        values: VB.NET expression for the collection (wrapped in [])
        item_name: Name of the loop variable
        item_type: Type of the loop variable (e.g., "sd:DataRow")
        body_activities: Activities inside the loop
    """
    name = display_name or f"For Each {item_name}"
    ann_attr = f' sap2010:Annotation.AnnotationText="{escape_xml(annotation)}"' if annotation else ""

    if not values.startswith("["):
        values = f"[{values}]"

    body_content = "\n".join(indent_xml(a, 6) for a in body_activities)

    return f"""{indent}<ForEach x:TypeArguments="{item_type}" Values="{values}" DisplayName="{escape_xml(name)}"{ann_attr}>
{indent}  <ActivityAction x:TypeArguments="{item_type}">
{indent}    <ActivityAction.Argument>
{indent}      <DelegateInArgument x:TypeArguments="{item_type}" Name="{item_name}" />
{indent}    </ActivityAction.Argument>
{indent}    <Sequence DisplayName="Body">
{body_content}
{indent}    </Sequence>
{indent}  </ActivityAction>
{indent}</ForEach>"""


def gen_while(
    condition: str,
    body_activities: List[str],
    display_name: Optional[str] = None,
    annotation: Optional[str] = None,
    indent: str = ""
) -> str:
    """
    Generate a While activity.

    Args:
        condition: VB.NET condition expression
        body_activities: Activities inside the loop
    """
    name = display_name or f"While {condition[:30]}..."
    ann_attr = f' sap2010:Annotation.AnnotationText="{escape_xml(annotation)}"' if annotation else ""

    if not condition.startswith("["):
        condition = f"[{condition}]"

    body_content = "\n".join(indent_xml(a, 4) for a in body_activities)

    return f"""{indent}<While Condition="{condition}" DisplayName="{escape_xml(name)}"{ann_attr}>
{indent}  <Sequence DisplayName="While Body">
{body_content}
{indent}  </Sequence>
{indent}</While>"""


def gen_switch(
    expression: str,
    expression_type: str,
    cases: Dict[str, List[str]],
    default_activities: Optional[List[str]] = None,
    display_name: Optional[str] = None,
    annotation: Optional[str] = None,
    indent: str = ""
) -> str:
    """
    Generate a Switch activity.

    Args:
        expression: VB.NET expression to switch on
        expression_type: Type of expression (e.g., "x:String")
        cases: Dict of {case_value: [activities]}
        default_activities: Activities for default case
    """
    name = display_name or f"Switch on {expression[:20]}..."
    ann_attr = f' sap2010:Annotation.AnnotationText="{escape_xml(annotation)}"' if annotation else ""

    if not expression.startswith("["):
        expression = f"[{expression}]"

    cases_xml = ""
    for case_value, activities in cases.items():
        case_content = "\n".join(indent_xml(a, 8) for a in activities)
        cases_xml += f"""
{indent}    <Case x:Key="{escape_xml(case_value)}">
{indent}      <Sequence DisplayName="Case: {escape_xml(case_value)}">
{case_content}
{indent}      </Sequence>
{indent}    </Case>"""

    default_xml = ""
    if default_activities:
        default_content = "\n".join(indent_xml(a, 6) for a in default_activities)
        default_xml = f"""
{indent}  <Switch.Default>
{indent}    <Sequence DisplayName="Default">
{default_content}
{indent}    </Sequence>
{indent}  </Switch.Default>"""

    return f"""{indent}<Switch x:TypeArguments="{expression_type}" Expression="{expression}" DisplayName="{escape_xml(name)}"{ann_attr}>
{indent}  <Switch.Cases>{cases_xml}
{indent}  </Switch.Cases>{default_xml}
{indent}</Switch>"""


def gen_trycatch(
    try_activities: List[str],
    catches: Optional[List[Dict[str, Any]]] = None,
    finally_activities: Optional[List[str]] = None,
    display_name: str = "TryCatch",
    annotation: Optional[str] = None,
    indent: str = ""
) -> str:
    """
    Generate a TryCatch activity.

    Args:
        try_activities: Activities in Try block
        catches: List of {"type": exception_type, "variable": var_name, "activities": [...]}
        finally_activities: Activities in Finally block (optional)
    """
    ann_attr = f' sap2010:Annotation.AnnotationText="{escape_xml(annotation)}"' if annotation else ""

    try_content = "\n".join(indent_xml(a, 6) for a in try_activities)

    catches_xml = ""
    if catches:
        for catch in catches:
            exc_type = catch.get("type", "s:Exception")
            var_name = catch.get("variable", "ex")
            catch_activities = catch.get("activities", [])
            catch_content = "\n".join(indent_xml(a, 10) for a in catch_activities)

            catches_xml += f"""
{indent}    <Catch x:TypeArguments="{exc_type}">
{indent}      <ActivityAction x:TypeArguments="{exc_type}">
{indent}        <ActivityAction.Argument>
{indent}          <DelegateInArgument x:TypeArguments="{exc_type}" Name="{var_name}" />
{indent}        </ActivityAction.Argument>
{indent}        <Sequence DisplayName="Catch {exc_type}">
{catch_content}
{indent}        </Sequence>
{indent}      </ActivityAction>
{indent}    </Catch>"""

    catches_block = f"""
{indent}  <TryCatch.Catches>{catches_xml}
{indent}  </TryCatch.Catches>""" if catches_xml else ""

    finally_xml = ""
    if finally_activities:
        finally_content = "\n".join(indent_xml(a, 6) for a in finally_activities)
        finally_xml = f"""
{indent}  <TryCatch.Finally>
{indent}    <Sequence DisplayName="Finally">
{finally_content}
{indent}    </Sequence>
{indent}  </TryCatch.Finally>"""

    return f"""{indent}<TryCatch DisplayName="{escape_xml(display_name)}"{ann_attr}>
{indent}  <TryCatch.Try>
{indent}    <Sequence DisplayName="Try">
{try_content}
{indent}    </Sequence>
{indent}  </TryCatch.Try>{catches_block}{finally_xml}
{indent}</TryCatch>"""


def gen_assign(
    to_variable: str,
    value: str,
    to_type: str = "x:String",
    display_name: Optional[str] = None,
    annotation: Optional[str] = None,
    indent: str = ""
) -> str:
    """
    Generate an Assign activity.

    Args:
        to_variable: Target variable name
        value: VB.NET expression for value
        to_type: Type of target variable
    """
    name = display_name or f"Assign {to_variable}"
    ann_attr = f' sap2010:Annotation.AnnotationText="{escape_xml(annotation)}"' if annotation else ""

    return f"""{indent}<Assign DisplayName="{escape_xml(name)}"{ann_attr}>
{indent}  <Assign.To>
{indent}    <OutArgument x:TypeArguments="{to_type}">[{to_variable}]</OutArgument>
{indent}  </Assign.To>
{indent}  <Assign.Value>
{indent}    <InArgument x:TypeArguments="{to_type}">[{value}]</InArgument>
{indent}  </Assign.Value>
{indent}</Assign>"""


def gen_multiple_assign(
    assignments: List[Dict[str, str]],
    display_name: str = "Multiple Assign",
    annotation: Optional[str] = None,
    indent: str = ""
) -> str:
    """
    Generate a MultipleAssign activity.

    Args:
        assignments: List of {"to": var_name, "value": expression, "type": type_str}
    """
    ann_attr = f' sap2010:Annotation.AnnotationText="{escape_xml(annotation)}"' if annotation else ""

    assigns_xml = ""
    for assign in assignments:
        to_var = assign["to"]
        value = assign["value"]
        var_type = assign.get("type", "x:String")
        assigns_xml += f"""
{indent}    <ui:AssignItem To="[{to_var}]" Value="[{value}]" />"""

    return f"""{indent}<ui:MultipleAssign DisplayName="{escape_xml(display_name)}"{ann_attr}>
{indent}  <ui:MultipleAssign.Items>{assigns_xml}
{indent}  </ui:MultipleAssign.Items>
{indent}</ui:MultipleAssign>"""
