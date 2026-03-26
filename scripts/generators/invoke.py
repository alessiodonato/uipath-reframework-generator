"""
Workflow invocation generators.
"""

from typing import Optional, Dict, List
from .helpers import escape_xml, build_annotation


def gen_invoke_workflow(
    workflow_path: str,
    arguments: Optional[Dict[str, Dict]] = None,
    display_name: Optional[str] = None,
    annotation: Optional[str] = None,
    isolated: bool = False,
    indent: str = ""
) -> str:
    """
    Generate an InvokeWorkflowFile activity.

    Args:
        workflow_path: Relative path to the workflow file (e.g., "Business/Step1.xaml")
        arguments: Dict of {arg_name: {"direction": In/Out/InOut, "type": type_str, "value": expression}}
        display_name: Optional display name
        annotation: Optional annotation
        isolated: Run in isolated context
    """
    name = display_name or f"Invoke {workflow_path.split('/')[-1].replace('.xaml', '')}"
    ann_attr = f'\n{indent}  sap2010:Annotation.AnnotationText="{escape_xml(annotation)}"' if annotation else ""

    # Build arguments block
    args_xml = ""
    if arguments:
        arg_items = []
        for arg_name, arg_spec in arguments.items():
            direction = arg_spec.get("direction", "In")
            arg_type = arg_spec.get("type", "x:String")
            value = arg_spec.get("value", "")

            # Map direction to element
            if direction == "In":
                element = "InArgument"
            elif direction == "Out":
                element = "OutArgument"
            else:
                element = "InOutArgument"

            if value:
                if not value.startswith("["):
                    value = f"[{value}]"
                arg_items.append(
                    f'{indent}      <{element} x:TypeArguments="{arg_type}" x:Key="{arg_name}">{value}</{element}>'
                )
            else:
                arg_items.append(
                    f'{indent}      <{element} x:TypeArguments="{arg_type}" x:Key="{arg_name}" />'
                )

        args_xml = f"""
{indent}  <ui:InvokeWorkflowFile.Arguments>
{chr(10).join(arg_items)}
{indent}  </ui:InvokeWorkflowFile.Arguments>"""

    isolated_attr = ' Isolated="True"' if isolated else ""

    return f"""{indent}<ui:InvokeWorkflowFile
{indent}  DisplayName="{escape_xml(name)}"{ann_attr}
{indent}  WorkflowFileName="{escape_xml(workflow_path)}"
{indent}  UnSafe="False"{isolated_attr}>{args_xml}
{indent}</ui:InvokeWorkflowFile>"""


def gen_invoke_workflow_simple(
    workflow_path: str,
    in_config: bool = True,
    in_transaction_item: bool = False,
    display_name: Optional[str] = None,
    annotation: Optional[str] = None,
    indent: str = ""
) -> str:
    """
    Generate a simple InvokeWorkflowFile with common arguments.

    Args:
        workflow_path: Relative path to workflow
        in_config: Include in_Config argument
        in_transaction_item: Include in_TransactionItem argument
    """
    arguments = {}

    if in_config:
        arguments["in_Config"] = {
            "direction": "In",
            "type": "scg:Dictionary(x:String, x:Object)",
            "value": "in_Config"
        }

    if in_transaction_item:
        arguments["in_TransactionItem"] = {
            "direction": "In",
            "type": "ui:QueueItem",
            "value": "in_TransactionItem"
        }

    return gen_invoke_workflow(
        workflow_path=workflow_path,
        arguments=arguments if arguments else None,
        display_name=display_name,
        annotation=annotation,
        indent=indent
    )


def gen_invoke_code(
    code: str,
    language: str = "vb",
    arguments: Optional[Dict[str, Dict]] = None,
    display_name: str = "Invoke Code",
    annotation: Optional[str] = None,
    indent: str = ""
) -> str:
    """
    Generate an InvokeCode activity.

    Args:
        code: VB.NET or C# code to execute
        language: "vb" or "csharp"
        arguments: Dict of {arg_name: {"direction": In/Out/InOut, "type": type_str}}
    """
    ann_attr = f'\n{indent}  sap2010:Annotation.AnnotationText="{escape_xml(annotation)}"' if annotation else ""

    # Map language
    lang_map = {"vb": "vb", "csharp": "csharp", "cs": "csharp", "c#": "csharp"}
    lang = lang_map.get(language.lower(), "vb")

    # Build arguments
    args_xml = ""
    if arguments:
        arg_items = []
        for arg_name, arg_spec in arguments.items():
            direction = arg_spec.get("direction", "In")
            arg_type = arg_spec.get("type", "x:String")
            arg_items.append(
                f'{indent}      <ui:CodeArgument Name="{arg_name}" Type="{arg_type}" Direction="{direction}" />'
            )
        args_xml = f"""
{indent}  <ui:InvokeCode.Arguments>
{chr(10).join(arg_items)}
{indent}  </ui:InvokeCode.Arguments>"""

    # Escape code for CDATA
    code_escaped = code.replace("]]>", "]]]]><![CDATA[>")

    return f"""{indent}<ui:InvokeCode
{indent}  DisplayName="{escape_xml(display_name)}"{ann_attr}
{indent}  Language="{lang}">
{indent}  <ui:InvokeCode.Code>
{indent}    <![CDATA[{code_escaped}]]>
{indent}  </ui:InvokeCode.Code>{args_xml}
{indent}</ui:InvokeCode>"""


def gen_invoke_method(
    target_object: str,
    method_name: str,
    parameters: Optional[List[Dict]] = None,
    result_variable: Optional[str] = None,
    result_type: str = "x:Object",
    display_name: Optional[str] = None,
    annotation: Optional[str] = None,
    indent: str = ""
) -> str:
    """
    Generate an InvokeMethod activity.

    Args:
        target_object: Expression for target object
        method_name: Name of method to invoke
        parameters: List of {"type": type_str, "value": expression}
        result_variable: Variable to store result (optional)
        result_type: Type of result
    """
    name = display_name or f"Invoke {method_name}"
    ann_attr = f'\n{indent}  sap2010:Annotation.AnnotationText="{escape_xml(annotation)}"' if annotation else ""

    if not target_object.startswith("["):
        target_object = f"[{target_object}]"

    # Build parameters
    params_xml = ""
    if parameters:
        param_items = []
        for param in parameters:
            param_type = param.get("type", "x:Object")
            value = param.get("value", "")
            if not value.startswith("["):
                value = f"[{value}]"
            param_items.append(
                f'{indent}      <InArgument x:TypeArguments="{param_type}">{value}</InArgument>'
            )
        params_xml = f"""
{indent}  <InvokeMethod.Parameters>
{chr(10).join(param_items)}
{indent}  </InvokeMethod.Parameters>"""

    # Result
    result_xml = ""
    if result_variable:
        result_xml = f"""
{indent}  <InvokeMethod.Result>
{indent}    <OutArgument x:TypeArguments="{result_type}">[{result_variable}]</OutArgument>
{indent}  </InvokeMethod.Result>"""

    return f"""{indent}<InvokeMethod
{indent}  DisplayName="{escape_xml(name)}"{ann_attr}
{indent}  TargetObject="{target_object}"
{indent}  MethodName="{method_name}">{params_xml}{result_xml}
{indent}</InvokeMethod>"""
