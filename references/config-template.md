# Config.xlsx Template

## Sheet structure

Two sheets: **Settings** (env-specific values) and **Constants** (business rule values).

## Settings sheet

| Name | Value | Description |
|------|-------|-------------|
| OrchestratorQueueName | {queue_name} | Queue to read from |
| MaxRetryNumber | 3 | Retry count for System Exceptions |
| MaxConsecutiveSystemExceptions | 3 | Abort threshold |
| logF_BusinessProcessName | {process_name} | Orchestrator log tag |
| {App}_URL | TODO | Entry URL for {App} |
| {App}_CredentialAsset | {App}_Credentials | Orchestrator credential asset name |

## Constants sheet

| Name | Value | Description |
|------|-------|-------------|
| {config_setting.name} | {config_setting.value} | {config_setting.description} |

## Accessing Config values in XAML/VB.NET

```vb
' String
in_Config("OrchestratorQueueName").ToString()

' Integer
CInt(in_Config("MaxRetryNumber"))

' Check before access
If in_Config.ContainsKey("MyKey") Then in_Config("MyKey").ToString() Else "default"
```

## openpyxl generation code

```python
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

def generate_config_xlsx(metadata: dict, output_path: str):
    wb = openpyxl.Workbook()
    process_name = metadata["process_name"]

    header_font = Font(bold=True, color="FFFFFF", size=11)
    header_fill = PatternFill("solid", fgColor="1F4E79")
    alt_fill = PatternFill("solid", fgColor="D6E4F0")
    thin = Border(left=Side(style="thin"), right=Side(style="thin"),
                  top=Side(style="thin"), bottom=Side(style="thin"))

    def write_sheet(ws, rows):
        for col, h in enumerate(["Name", "Value", "Description"], 1):
            cell = ws.cell(row=1, column=col, value=h)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal="center")
            cell.border = thin
        for ri, (n, v, d) in enumerate(rows, 2):
            fill = alt_fill if ri % 2 == 0 else None
            for ci, val in enumerate([n, v, d], 1):
                cell = ws.cell(row=ri, column=ci, value=val)
                cell.border = thin
                if fill: cell.fill = fill
        ws.column_dimensions["A"].width = 38
        ws.column_dimensions["B"].width = 32
        ws.column_dimensions["C"].width = 50
        ws.freeze_panes = "A2"

    # Settings
    ws = wb.active
    ws.title = "Settings"
    rows = [
        ("OrchestratorQueueName", metadata.get("queue_name", ""), "Orchestrator queue name"),
        ("MaxRetryNumber", metadata.get("max_retry_number", 3), "Max retries for System Exceptions"),
        ("MaxConsecutiveSystemExceptions", 3, "Abort threshold"),
        ("logF_BusinessProcessName", process_name, "Log tag"),
    ]
    for app in metadata.get("applications", []):
        rows += [
            (f"{app}_URL", "TODO: add URL", f"Entry URL for {app}"),
            (f"{app}_CredentialAsset", f"{app}_Credentials", f"Orchestrator asset for {app}"),
        ]
    write_sheet(ws, rows)

    # Constants
    ws2 = wb.create_sheet("Constants")
    rows2 = [
        (s["name"], s["value"], s.get("description", f"Type: {s['type']}"))
        for s in metadata.get("config_settings", [])
        if s["type"] in ("Constant", "Asset")
    ]
    if not rows2:
        rows2 = [("EXAMPLE_CONSTANT", "value", "Add business rule constants here")]
    write_sheet(ws2, rows2)

    wb.save(output_path)
```
