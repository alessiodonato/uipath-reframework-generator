# UiPath ReFramework Generator - Cheat Sheet

Quick reference for common patterns and commands.

---

## CLI Commands

### Generate Project from PDD
```bash
# Interactive mode
python scripts/generate_reframework.py

# Direct mode
python scripts/generate_reframework.py --input MyProcess_PDD.pdf --output ./output/

# With variant
python scripts/generate_reframework.py --input MyProcess_PDD.pdf --variant sequence

# Preview metadata only
python scripts/generate_reframework.py --input MyProcess_PDD.pdf --metadata-only
```

### Validate XAML
```bash
# Validate project
python -m scripts.validate_xaml ./MyProject --lint

# Validate single file
python -m scripts.validate_xaml ./Main.xaml --lint

# Auto-fix issues
python -m scripts.validate_xaml ./MyProject --lint --fix

# Strict mode (naming conventions)
python -m scripts.validate_xaml ./MyProject --lint --strict

# Output as JSON
python -m scripts.validate_xaml ./MyProject --lint --json
```

### Resolve NuGet Versions
```bash
# Get latest versions of common packages
python scripts/resolve_nuget.py

# Get specific packages
python scripts/resolve_nuget.py UiPath.Excel.Activities UiPath.Mail.Activities

# Update project.json
python scripts/resolve_nuget.py --update ./MyProject/project.json

# Detect required packages from XAML
python scripts/resolve_nuget.py --detect ./MyProject
```

### Manage Config.xlsx
```bash
# List all keys
python scripts/config_manager.py list ./MyProject

# Add a key
python scripts/config_manager.py add ./MyProject \
  --sheet Settings --key WebApp_URL --value "https://..." --desc "Web App URL"

# Validate (find missing/unused keys)
python scripts/config_manager.py validate ./MyProject

# Export as JSON
python scripts/config_manager.py export ./MyProject
```

### Framework Wiring
```bash
# Wire UiElement chain for an app
python scripts/modify_framework.py wire-uielement ./MyProject WebApp

# Add variables to workflow
python scripts/modify_framework.py add-variables ./Main.xaml strName:String intCount:Int32

# Insert invoke call
python scripts/modify_framework.py insert-invoke ./Process.xaml "Business/Step1.xaml"

# List markers in file
python scripts/modify_framework.py list-markers ./GetTransactionData.xaml
```

---

## Project Variants

| Variant | Use Case | Transaction Loop | Entry Point |
|---------|----------|-----------------|-------------|
| `reframework` (default) | Queue-based batch processing | Yes | Main.xaml (State Machine) |
| `dispatcher` | Load data into queue | Yes (DataRow) | Main.xaml (State Machine) |
| `performer` | Process queue items | Yes (QueueItem) | Main.xaml (State Machine) |
| `sequence` | Simple linear automation | No | Main.xaml (Sequence) |

---

## Generator Functions

### Core Control Flow
```python
from generators import gen_sequence, gen_if, gen_foreach, gen_trycatch

# Sequence
gen_sequence("My Sequence", activities=[...], variables=[{"name": "x", "type": "x:String"}])

# If/Else
gen_if("x > 10", then_activities=[...], else_activities=[...])

# ForEach
gen_foreach("dtData.Rows", "row", "sd:DataRow", body_activities=[...])

# TryCatch
gen_trycatch(try_activities=[...], catches=[{"type": "s:Exception", "variable": "ex", "activities": [...]}])
```

### Logging
```python
from generators import gen_log_message

gen_log_message("'[ProcessName] Step completed'", level="Info")
gen_log_message("strVariable", level="Trace")  # Variable expression
```

### Orchestrator
```python
from generators import gen_get_queue_item, gen_set_transaction_status, gen_get_credential

# Get queue item
gen_get_queue_item('in_Config("QueueName").ToString()', result_variable="txItem")

# Set status
gen_set_transaction_status("txItem", status="Successful")
gen_set_transaction_status("txItem", status="Failed", reason="ex.Message", error_type="Business")

# Get credential
gen_get_credential('in_Config("CredentialAsset").ToString()', "strUser", "secPass")
```

### UI Automation (Modern)
```python
from generators import gen_nclick, gen_ntypeinto, gen_napplication_card

# Click
gen_nclick('<webctrl tag="BUTTON" />', click_type="Single", input_mode="Simulate")

# Type Into
gen_ntypeinto('<webctrl id="email" />', "strEmail", empty_field_mode="SingleLine")

# Secure password
gen_ntypeinto('<webctrl id="password" />', "secPassword", is_secure=True)

# Application Card (browser scope)
gen_napplication_card(
    'in_Config("AppUrl").ToString()',
    body_activities=[...],
    open_mode="Always",
    is_incognito=True,
    out_uielement="uiApp"
)
```

### Error Handling
```python
from generators import gen_throw, gen_rethrow, gen_retry_scope

# Throw BusinessRuleException
gen_throw("BusinessRuleException", '"Invoice already processed"')

# Throw ApplicationException
gen_throw("ApplicationException", '"Login failed: " + strError')

# Rethrow in catch block
gen_rethrow()

# Retry scope
gen_retry_scope(action_activities=[...], number_of_retries=3, retry_interval="00:00:05")
```

### Invoke Workflow
```python
from generators import gen_invoke_workflow, gen_invoke_workflow_simple

# Full control
gen_invoke_workflow(
    "Business/Step1.xaml",
    arguments={
        "in_Config": {"direction": "In", "type": "scg:Dictionary(x:String, x:Object)", "value": "in_Config"},
        "out_Result": {"direction": "Out", "type": "x:String", "value": "strResult"}
    }
)

# Simple (auto-adds in_Config)
gen_invoke_workflow_simple("Business/Step1.xaml", in_config=True, in_transaction_item=True)
```

---

## Type Mappings

| Simple Type | XAML Type |
|-------------|-----------|
| String | `x:String` |
| Int32, Integer | `x:Int32` |
| Boolean, Bool | `x:Boolean` |
| DateTime | `s:DateTime` |
| DataTable | `sd:DataTable` |
| DataRow | `sd:DataRow` |
| QueueItem | `ui:QueueItem` |
| SecureString | `s:Security.SecureString` |
| Dictionary | `scg:Dictionary(x:String, x:Object)` |
| UiElement | `uix:UiElement` |

---

## Validation Rules Quick Reference

### Critical Errors (will crash Studio)
- `Version="V3"` or `Version="V4"` → Must be `Version="V5"`
- `ElementType="DataGrid"` → Must be `ElementType="Table"`
- `x:TypeArguments="DataTable"` → Must be `x:TypeArguments="sd:DataTable"`
- `NExtractData.*DataTable=` → Must use `ExtractedData=`
- `GetQueueItem.*QueueType=` → Must use `QueueName=`

### Warnings (may cause runtime issues)
- Empty `OutArgument` bindings → Silent data loss
- `NSelectItem.*InteractionMode=` → Property doesn't exist
- Hardcoded URLs → Use Config()
- Missing log bookends → Add START/END logs

### Best Practices
- Use descriptive DisplayNames (not "Sequence", "If")
- Add annotations with Reads/Output/Throws format
- Keep workflows under 150 lines
- One UI scope per workflow

---

## Config.xlsx Structure

### Settings Sheet
| Name | Value | Description |
|------|-------|-------------|
| OrchestratorQueueName | MyQueue | Queue name |
| MaxRetryNumber | 3 | Max retries |
| AppName_URL | https://... | App URL |
| AppName_CredentialAsset | AppName_Cred | Credential asset name |

### Constants Sheet
| Name | Value | Description |
|------|-------|-------------|
| MaxProcessingTime | 60 | Minutes |
| DefaultTimeout | 30000 | Milliseconds |

### Assets Sheet
| Name | Asset | Folder | Description |
|------|-------|--------|-------------|
| LogPath | Logs | Shared | Log folder path |

---

## Exception Handling Pattern

```
BusinessRuleException:
  - Caught in Process.xaml
  - SetTransactionStatus → Failed (Business)
  - NO retry
  - Does NOT rethrow

ApplicationException:
  - NOT caught in Process.xaml
  - Bubbles to Main.xaml
  - SetTransactionStatus → Failed (Application)
  - Triggers retry (up to MaxRetryNumber)
```

---

## Log Message Format

```
[ProcessName] State - Message

Examples:
[InvoiceProcessing] Init - Loading configuration
[InvoiceProcessing] GetTx - Transaction retrieved: INV-001
[InvoiceProcessing] Process - Step completed
[InvoiceProcessing] SetStatus - INV-001 → Successful
[InvoiceProcessing] Close - Closing WebApp
```
