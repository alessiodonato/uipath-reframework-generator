"""
Orchestrator activity generators: Queue, Credentials, Assets.
"""

from typing import Optional, Dict, List
from .helpers import escape_xml, build_annotation


def gen_get_queue_item(
    queue_name: str,
    result_variable: str = "out_TransactionItem",
    timeout_ms: int = 30000,
    display_name: Optional[str] = None,
    annotation: Optional[str] = None,
    indent: str = ""
) -> str:
    """
    Generate a GetQueueItem activity.

    Args:
        queue_name: VB.NET expression for queue name (or Config key reference)
        result_variable: Variable to store the queue item
        timeout_ms: Timeout in milliseconds
    """
    name = display_name or f"Get Queue Item from '{queue_name[:30]}'"
    ann_attr = f'\n{indent}  sap2010:Annotation.AnnotationText="{escape_xml(annotation)}"' if annotation else ""

    # Wrap in brackets if not already
    if not queue_name.startswith("["):
        queue_name = f"[{queue_name}]"

    return f"""{indent}<ui:GetQueueItem
{indent}  DisplayName="{escape_xml(name)}"{ann_attr}
{indent}  QueueName="{queue_name}"
{indent}  TimeoutMS="{timeout_ms}"
{indent}  Result="[{result_variable}]" />"""


def gen_add_queue_item(
    queue_name: str,
    item_fields: Dict[str, str],
    reference: Optional[str] = None,
    priority: str = "Normal",
    result_variable: Optional[str] = None,
    display_name: Optional[str] = None,
    annotation: Optional[str] = None,
    indent: str = ""
) -> str:
    """
    Generate an AddQueueItem activity.

    Args:
        queue_name: Queue name expression
        item_fields: Dict of {field_name: value_expression}
        reference: Optional reference string expression
        priority: Low, Normal, or High
        result_variable: Variable to store added item
    """
    name = display_name or f"Add Queue Item to '{queue_name[:30]}'"
    ann_attr = f'\n{indent}  sap2010:Annotation.AnnotationText="{escape_xml(annotation)}"' if annotation else ""

    if not queue_name.startswith("["):
        queue_name = f"[{queue_name}]"

    # Build item information
    fields_xml = ""
    for field_name, value in item_fields.items():
        if not value.startswith("["):
            value = f"[{value}]"
        fields_xml += f"""
{indent}      <ui:ItemInformationPair Key="{escape_xml(field_name)}" Value="{value}" />"""

    # Reference
    ref_attr = ""
    if reference:
        if not reference.startswith("["):
            reference = f"[{reference}]"
        ref_attr = f'\n{indent}  Reference="{reference}"'

    # Result
    result_xml = ""
    if result_variable:
        result_xml = f'\n{indent}  Result="[{result_variable}]"'

    return f"""{indent}<ui:AddQueueItem
{indent}  DisplayName="{escape_xml(name)}"{ann_attr}
{indent}  QueueName="{queue_name}"
{indent}  Priority="{priority}"{ref_attr}{result_xml}>
{indent}  <ui:AddQueueItem.ItemInformation>{fields_xml}
{indent}  </ui:AddQueueItem.ItemInformation>
{indent}</ui:AddQueueItem>"""


def gen_set_transaction_status(
    queue_item: str = "in_TransactionItem",
    status: str = "Successful",
    reason: Optional[str] = None,
    error_type: Optional[str] = None,
    display_name: Optional[str] = None,
    annotation: Optional[str] = None,
    indent: str = ""
) -> str:
    """
    Generate a SetTransactionStatus activity.

    Args:
        queue_item: Variable containing the queue item
        status: Successful or Failed
        reason: Reason expression (for Failed status)
        error_type: Business or Application (for Failed status)
    """
    name = display_name or f"Set Transaction Status → {status}"
    ann_attr = f'\n{indent}  sap2010:Annotation.AnnotationText="{escape_xml(annotation)}"' if annotation else ""

    # Validate status
    if status not in ("Successful", "Failed"):
        raise ValueError(f"Invalid status '{status}'. Must be 'Successful' or 'Failed'")

    # Validate error_type
    if error_type and error_type not in ("Business", "Application"):
        raise ValueError(f"Invalid error_type '{error_type}'. Must be 'Business' or 'Application'")

    reason_attr = ""
    if reason:
        if not reason.startswith("["):
            reason = f"[{reason}]"
        reason_attr = f'\n{indent}  Reason="{reason}"'

    error_type_attr = ""
    if error_type:
        error_type_attr = f'\n{indent}  ErrorType="{error_type}"'

    return f"""{indent}<ui:SetTransactionStatus
{indent}  DisplayName="{escape_xml(name)}"{ann_attr}
{indent}  QueueItem="[{queue_item}]"
{indent}  Status="{status}"{reason_attr}{error_type_attr} />"""


def gen_get_credential(
    asset_name: str,
    username_variable: str = "strUsername",
    password_variable: str = "secPassword",
    folder: Optional[str] = None,
    display_name: Optional[str] = None,
    annotation: Optional[str] = None,
    indent: str = ""
) -> str:
    """
    Generate a GetRobotCredential activity.

    Args:
        asset_name: VB.NET expression for asset name
        username_variable: Variable to store username
        password_variable: Variable to store password (SecureString)
        folder: Optional Orchestrator folder
    """
    name = display_name or f"Get Credential '{asset_name[:30]}'"
    ann_attr = f'\n{indent}  sap2010:Annotation.AnnotationText="{escape_xml(annotation)}"' if annotation else ""

    if not asset_name.startswith("["):
        asset_name = f"[{asset_name}]"

    folder_attr = ""
    if folder:
        if not folder.startswith("["):
            folder = f"[{folder}]"
        folder_attr = f'\n{indent}  Folder="{folder}"'

    return f"""{indent}<ui:GetRobotCredential
{indent}  DisplayName="{escape_xml(name)}"{ann_attr}
{indent}  AssetName="{asset_name}"
{indent}  Username="[{username_variable}]"
{indent}  Password="[{password_variable}]"{folder_attr} />"""


def gen_get_asset(
    asset_name: str,
    value_variable: str,
    folder: Optional[str] = None,
    display_name: Optional[str] = None,
    annotation: Optional[str] = None,
    indent: str = ""
) -> str:
    """
    Generate a GetRobotAsset activity.

    Args:
        asset_name: VB.NET expression for asset name
        value_variable: Variable to store asset value
        folder: Optional Orchestrator folder
    """
    name = display_name or f"Get Asset '{asset_name[:30]}'"
    ann_attr = f'\n{indent}  sap2010:Annotation.AnnotationText="{escape_xml(annotation)}"' if annotation else ""

    if not asset_name.startswith("["):
        asset_name = f"[{asset_name}]"

    folder_attr = ""
    if folder:
        if not folder.startswith("["):
            folder = f"[{folder}]"
        folder_attr = f'\n{indent}  Folder="{folder}"'

    return f"""{indent}<ui:GetRobotAsset
{indent}  DisplayName="{escape_xml(name)}"{ann_attr}
{indent}  AssetName="{asset_name}"
{indent}  Value="[{value_variable}]"{folder_attr} />"""


def gen_bulk_add_queue_items(
    queue_name: str,
    data_table: str,
    reference_column: Optional[str] = None,
    commit_type: str = "AllOrNothing",
    display_name: Optional[str] = None,
    annotation: Optional[str] = None,
    indent: str = ""
) -> str:
    """
    Generate a BulkAddQueueItems activity.

    Args:
        queue_name: Queue name expression
        data_table: DataTable variable containing items
        reference_column: Column name for Reference field
        commit_type: AllOrNothing or ProcessAllIndependently
    """
    name = display_name or f"Bulk Add to '{queue_name[:30]}'"
    ann_attr = f'\n{indent}  sap2010:Annotation.AnnotationText="{escape_xml(annotation)}"' if annotation else ""

    if not queue_name.startswith("["):
        queue_name = f"[{queue_name}]"

    ref_attr = ""
    if reference_column:
        ref_attr = f'\n{indent}  ReferenceColumn="{escape_xml(reference_column)}"'

    return f"""{indent}<ui:BulkAddQueueItems
{indent}  DisplayName="{escape_xml(name)}"{ann_attr}
{indent}  QueueName="{queue_name}"
{indent}  DataTable="[{data_table}]"
{indent}  CommitType="{commit_type}"{ref_attr} />"""
