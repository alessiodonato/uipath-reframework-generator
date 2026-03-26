"""
Data operation generators: DataTable operations, file operations.
"""

from typing import Optional, List, Dict
from .helpers import escape_xml


def gen_build_datatable(
    result_variable: str,
    columns: List[Dict[str, str]],
    display_name: str = "Build DataTable",
    annotation: Optional[str] = None,
    indent: str = ""
) -> str:
    """
    Generate a BuildDataTable activity.

    Args:
        result_variable: Variable to store the DataTable
        columns: List of {"name": str, "type": str} dicts
    """
    ann_attr = f'\n{indent}  sap2010:Annotation.AnnotationText="{escape_xml(annotation)}"' if annotation else ""

    # Build column definitions
    cols_xml = ""
    for col in columns:
        col_name = col.get("name", "Column")
        col_type = col.get("type", "String")
        # Map to .NET type
        type_map = {
            "String": "System.String",
            "Int32": "System.Int32",
            "Integer": "System.Int32",
            "Boolean": "System.Boolean",
            "DateTime": "System.DateTime",
            "Double": "System.Double",
            "Decimal": "System.Decimal",
            "Object": "System.Object",
        }
        net_type = type_map.get(col_type, col_type)
        cols_xml += f"""
{indent}      <ui:ColumnInfo ColumnName="{escape_xml(col_name)}" DataType="{net_type}" />"""

    return f"""{indent}<ui:BuildDataTable
{indent}  DisplayName="{escape_xml(display_name)}"{ann_attr}
{indent}  DataTable="[{result_variable}]">
{indent}  <ui:BuildDataTable.TableInfo>
{indent}    <ui:TableInfo>{cols_xml}
{indent}    </ui:TableInfo>
{indent}  </ui:BuildDataTable.TableInfo>
{indent}</ui:BuildDataTable>"""


def gen_add_data_row(
    data_table: str,
    row_data: str,
    display_name: str = "Add Data Row",
    annotation: Optional[str] = None,
    indent: str = ""
) -> str:
    """
    Generate an AddDataRow activity.

    Args:
        data_table: Variable containing the DataTable
        row_data: VB.NET array expression for row values
    """
    ann_attr = f'\n{indent}  sap2010:Annotation.AnnotationText="{escape_xml(annotation)}"' if annotation else ""

    if not row_data.startswith("["):
        row_data = f"[{row_data}]"

    return f"""{indent}<ui:AddDataRow
{indent}  DisplayName="{escape_xml(display_name)}"{ann_attr}
{indent}  DataTable="[{data_table}]"
{indent}  ArrayRow="{row_data}" />"""


def gen_filter_datatable(
    input_table: str,
    output_table: str,
    filter_expression: str,
    display_name: str = "Filter DataTable",
    annotation: Optional[str] = None,
    indent: str = ""
) -> str:
    """
    Generate a FilterDataTable activity.

    Args:
        input_table: Input DataTable variable
        output_table: Output DataTable variable
        filter_expression: DataTable Select expression
    """
    ann_attr = f'\n{indent}  sap2010:Annotation.AnnotationText="{escape_xml(annotation)}"' if annotation else ""

    return f"""{indent}<ui:FilterDataTable
{indent}  DisplayName="{escape_xml(display_name)}"{ann_attr}
{indent}  DataTable="[{input_table}]"
{indent}  OutputDataTable="[{output_table}]">
{indent}  <ui:FilterDataTable.FilterConditions>
{indent}    <ui:FilterCondition Column="" Operand="" Value="{escape_xml(filter_expression)}" />
{indent}  </ui:FilterDataTable.FilterConditions>
{indent}</ui:FilterDataTable>"""


def gen_sort_datatable(
    input_table: str,
    output_table: str,
    sort_column: str,
    order: str = "Ascending",
    display_name: str = "Sort DataTable",
    annotation: Optional[str] = None,
    indent: str = ""
) -> str:
    """
    Generate a SortDataTable activity.

    Args:
        input_table: Input DataTable variable
        output_table: Output DataTable variable
        sort_column: Column name to sort by
        order: Ascending or Descending
    """
    ann_attr = f'\n{indent}  sap2010:Annotation.AnnotationText="{escape_xml(annotation)}"' if annotation else ""

    return f"""{indent}<ui:SortDataTable
{indent}  DisplayName="{escape_xml(display_name)}"{ann_attr}
{indent}  DataTable="[{input_table}]"
{indent}  OutputDataTable="[{output_table}]"
{indent}  SortColumn="{escape_xml(sort_column)}"
{indent}  OrderByDirection="{order}" />"""


def gen_read_range(
    workbook_path: str,
    sheet_name: str,
    result_variable: str,
    range_address: str = "",
    add_headers: bool = True,
    display_name: Optional[str] = None,
    annotation: Optional[str] = None,
    indent: str = ""
) -> str:
    """
    Generate a ReadRange activity (Excel).

    Args:
        workbook_path: Path to Excel file
        sheet_name: Sheet name
        result_variable: Variable to store DataTable
        range_address: Optional range (e.g., "A1:D10"), empty for all
        add_headers: Use first row as headers
    """
    name = display_name or f"Read Range from '{sheet_name}'"
    ann_attr = f'\n{indent}  sap2010:Annotation.AnnotationText="{escape_xml(annotation)}"' if annotation else ""

    if not workbook_path.startswith("["):
        workbook_path = f"[{workbook_path}]"

    range_attr = f' Range="{range_address}"' if range_address else ""

    return f"""{indent}<ui:ExcelReadRange
{indent}  DisplayName="{escape_xml(name)}"{ann_attr}
{indent}  WorkbookPath="{workbook_path}"
{indent}  SheetName="{escape_xml(sheet_name)}"{range_attr}
{indent}  AddHeaders="{str(add_headers).lower()}"
{indent}  DataTable="[{result_variable}]" />"""


def gen_write_range(
    workbook_path: str,
    sheet_name: str,
    data_table: str,
    starting_cell: str = "A1",
    add_headers: bool = True,
    display_name: Optional[str] = None,
    annotation: Optional[str] = None,
    indent: str = ""
) -> str:
    """
    Generate a WriteRange activity (Excel).

    Args:
        workbook_path: Path to Excel file
        sheet_name: Sheet name
        data_table: DataTable variable to write
        starting_cell: Cell to start writing from
        add_headers: Write column headers
    """
    name = display_name or f"Write Range to '{sheet_name}'"
    ann_attr = f'\n{indent}  sap2010:Annotation.AnnotationText="{escape_xml(annotation)}"' if annotation else ""

    if not workbook_path.startswith("["):
        workbook_path = f"[{workbook_path}]"

    return f"""{indent}<ui:ExcelWriteRange
{indent}  DisplayName="{escape_xml(name)}"{ann_attr}
{indent}  WorkbookPath="{workbook_path}"
{indent}  SheetName="{escape_xml(sheet_name)}"
{indent}  StartingCell="{starting_cell}"
{indent}  AddHeaders="{str(add_headers).lower()}"
{indent}  DataTable="[{data_table}]" />"""


def gen_read_text_file(
    file_path: str,
    result_variable: str,
    encoding: str = "UTF8",
    display_name: Optional[str] = None,
    annotation: Optional[str] = None,
    indent: str = ""
) -> str:
    """
    Generate a ReadTextFile activity.

    Args:
        file_path: Path to text file
        result_variable: Variable to store content
        encoding: File encoding
    """
    name = display_name or "Read Text File"
    ann_attr = f'\n{indent}  sap2010:Annotation.AnnotationText="{escape_xml(annotation)}"' if annotation else ""

    if not file_path.startswith("["):
        file_path = f"[{file_path}]"

    return f"""{indent}<ui:ReadTextFile
{indent}  DisplayName="{escape_xml(name)}"{ann_attr}
{indent}  FileName="{file_path}"
{indent}  Encoding="{encoding}"
{indent}  Content="[{result_variable}]" />"""


def gen_write_text_file(
    file_path: str,
    content: str,
    encoding: str = "UTF8",
    append: bool = False,
    display_name: Optional[str] = None,
    annotation: Optional[str] = None,
    indent: str = ""
) -> str:
    """
    Generate a WriteTextFile activity.

    Args:
        file_path: Path to text file
        content: VB.NET expression for content
        encoding: File encoding
        append: Append to file instead of overwrite
    """
    name = display_name or "Write Text File"
    ann_attr = f'\n{indent}  sap2010:Annotation.AnnotationText="{escape_xml(annotation)}"' if annotation else ""

    if not file_path.startswith("["):
        file_path = f"[{file_path}]"

    if not content.startswith("["):
        content = f"[{content}]"

    return f"""{indent}<ui:WriteTextFile
{indent}  DisplayName="{escape_xml(name)}"{ann_attr}
{indent}  FileName="{file_path}"
{indent}  Text="{content}"
{indent}  Encoding="{encoding}"
{indent}  Append="{str(append).lower()}" />"""
