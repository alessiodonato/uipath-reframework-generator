# XAML Lint Rules Reference

Complete reference for all validation rules in the XAML linter.

---

## Severity Levels

| Level | Description | Action Required |
|-------|-------------|-----------------|
| **ERROR** | Will crash Studio or cause compile failure | Must fix before opening in Studio |
| **WARN** | May cause runtime failure or silent data loss | Should fix before deployment |
| **INFO** | Best practice violation | Consider fixing |

---

## Hallucination Rules (HALL-*)

These rules detect patterns that LLMs commonly hallucinate when generating XAML.

### HALL-Version
**Severity:** ERROR

Wrong Version attribute on modern UI activities.

```xml
<!-- BAD -->
<uix:NClick Version="V3" ... />
<uix:NTypeInto Version="V4" ... />

<!-- GOOD -->
<uix:NClick Version="V5" ... />
<uix:NTypeInto Version="V5" ... />
```

### HALL-ElementType
**Severity:** ERROR

Invalid ElementType enum values for NExtractData.

```xml
<!-- BAD -->
<uix:NExtractData ElementType="DataGrid" ... />
<uix:NExtractData ElementType="ComboBox" ... />
<uix:NExtractData ElementType="InputBoxText" ... />

<!-- GOOD -->
<uix:NExtractData ElementType="Table" ... />
<uix:NExtractData ElementType="DropDown" ... />
<uix:NExtractData ElementType="InputBox" ... />
```

### HALL-NExtractData
**Severity:** ERROR

Wrong property names for NExtractData output.

```xml
<!-- BAD -->
<uix:NExtractData DataTable="[dtResult]" ... />
<uix:NExtractData Result="[dtResult]" ... />

<!-- GOOD -->
<uix:NExtractData ExtractedData="[dtResult]" ... />
```

### HALL-NGetText
**Severity:** ERROR

Wrong property name for NGetText output.

```xml
<!-- BAD -->
<uix:NGetText Result="[strText]" ... />

<!-- GOOD -->
<uix:NGetText Value="[strText]" ... />
```

### HALL-QueueProperty
**Severity:** ERROR

Wrong property name for GetQueueItem.

```xml
<!-- BAD -->
<ui:GetQueueItem QueueType="MyQueue" ... />

<!-- GOOD -->
<ui:GetQueueItem QueueName="[queueName]" ... />
```

### HALL-TargetElement
**Severity:** ERROR

Wrong child element for Target in modern UI activities.

```xml
<!-- BAD -->
<uix:NClick.TargetAnchorable>...</uix:NClick.TargetAnchorable>

<!-- GOOD -->
<uix:NClick.Target>...</uix:NClick.Target>
```

### HALL-InteractionMode
**Severity:** WARN

InteractionMode property on activities that don't support it.

```xml
<!-- BAD - NSelectItem doesn't have InteractionMode -->
<uix:NSelectItem InteractionMode="Simulate" ... />

<!-- GOOD -->
<uix:NSelectItem ... />
```

---

## Namespace Rules (NS-*)

### NS-001
**Severity:** ERROR

DataTable used without sd: namespace declaration.

```xml
<!-- BAD -->
<Variable x:TypeArguments="DataTable" Name="dt" />

<!-- GOOD -->
<Activity xmlns:sd="clr-namespace:System.Data;assembly=System.Data">
  <Variable x:TypeArguments="sd:DataTable" Name="dt" />
</Activity>
```

### NS-002
**Severity:** ERROR

Modern UI activities (uix:) used without namespace declaration.

```xml
<!-- BAD -->
<uix:NClick ... />  <!-- Missing xmlns:uix -->

<!-- GOOD -->
<Activity xmlns:uix="clr-namespace:UiPath.UIAutomationNext.Activities;assembly=UiPath.UIAutomationNext.Activities">
  <uix:NClick ... />
</Activity>
```

---

## Type Rules (TYPE-*)

### TYPE-001
**Severity:** ERROR

Unqualified DataTable type in TypeArguments.

```xml
<!-- BAD -->
<Variable x:TypeArguments="DataTable" Name="dt" />
<ForEach x:TypeArguments="DataTable" ... />

<!-- GOOD -->
<Variable x:TypeArguments="sd:DataTable" Name="dt" />
<ForEach x:TypeArguments="sd:DataTable" ... />
```

### TYPE-002
**Severity:** ERROR

Unqualified DataRow type in TypeArguments.

```xml
<!-- BAD -->
<ForEach x:TypeArguments="DataRow" ... />

<!-- GOOD -->
<ForEach x:TypeArguments="sd:DataRow" ... />
```

### TYPE-003
**Severity:** WARN

Empty Out/InOut argument binding causes silent data loss.

```xml
<!-- BAD - value is lost -->
<OutArgument x:TypeArguments="x:String">[]</OutArgument>
<InOutArgument x:TypeArguments="x:String" />

<!-- GOOD -->
<OutArgument x:TypeArguments="x:String">[strResult]</OutArgument>
```

---

## Activity Rules (ACT-*)

### ACT-InvalidProperty
**Severity:** ERROR

Activity has a property that doesn't exist.

Common invalid properties by activity:
- `NClick`: `Selector`, `Element`, `WaitForReady`
- `NTypeInto`: `Selector`, `Element`, `EmptyField`, `RetryOnError`
- `NGetText`: `Selector`, `Element`, `Result`, `DataTable`
- `NSelectItem`: `InteractionMode`
- `NApplicationCard`: `Url=` (use `Url` without `=`)
- `GetQueueItem`: `QueueType`, `Queue`

---

## Enum Rules (ENUM-*)

### ENUM-EmptyFieldMode
**Severity:** ERROR

Invalid EmptyFieldMode value.

```xml
<!-- BAD -->
<uix:NTypeInto EmptyFieldMode="Clear" ... />
<uix:NTypeInto EmptyFieldMode="Delete" ... />

<!-- GOOD -->
<uix:NTypeInto EmptyFieldMode="SingleLine" ... />
<uix:NTypeInto EmptyFieldMode="MultiLine" ... />
<uix:NTypeInto EmptyFieldMode="None" ... />
```

### ENUM-OpenMode
**Severity:** ERROR

Invalid OpenMode value for NApplicationCard.

Valid values: `Always`, `IfNotOpen`, `Never`

### ENUM-InputMode
**Severity:** ERROR

Invalid InputMode value.

Valid values: `Simulate`, `HardwareEvents`, `ChromiumApi`, `WindowMessages`

### ENUM-LogLevel
**Severity:** ERROR

Invalid log level.

Valid values: `Trace`, `Info`, `Warn`, `Error`, `Fatal`

---

## Architecture Rules (ARCH-*)

### ARCH-RestrictedActivity
**Severity:** INFO

Activity used in wrong workflow file.

| Activity | Allowed Files |
|----------|---------------|
| `CreateFormTask` | Main.xaml |
| `WaitForFormTaskAndResume` | Main.xaml |
| `GetQueueItem` | Framework/GetTransactionData.xaml |
| `SetTransactionStatus` | Framework/SetTransactionStatus.xaml, Process.xaml |

### ARCH-URL
**Severity:** INFO

Hardcoded URL found. Should use Config().

```xml
<!-- BAD -->
<uix:NGoToUrl Url="https://example.com/login" ... />

<!-- GOOD -->
<uix:NGoToUrl Url="[in_Config(&quot;AppUrl&quot;).ToString()]" ... />
```

---

## Cross-File Rules (CROSS-*)

### CROSS-001
**Severity:** WARN

InvokeWorkflowFile target not found in project.

```xml
<!-- BAD - file doesn't exist -->
<ui:InvokeWorkflowFile WorkflowFileName="Business\NonExistent.xaml" ... />

<!-- GOOD -->
<ui:InvokeWorkflowFile WorkflowFileName="Business\Step1.xaml" ... />
```

---

## XML Rules (XML-*)

### XML-001
**Severity:** ERROR

XML is not well-formed.

Common causes:
- Unescaped `&` (should be `&amp;`)
- Unescaped `<` (should be `&lt;`)
- Unescaped `>` (should be `&gt;`)
- Unescaped `"` in attributes (should be `&quot;`)
- Missing closing tags
- Mismatched tag names

---

## Naming Rules (NAME-*)

### NAME-001
**Severity:** INFO

Workflow file name should be PascalCase.

```
BAD:  my_workflow.xaml, myWorkflow.xaml
GOOD: MyWorkflow.xaml, ProcessInvoice.xaml
```

### NAME-002
**Severity:** INFO

Generic DisplayName - should be descriptive.

```xml
<!-- BAD -->
<Sequence DisplayName="Sequence" ... />
<If DisplayName="If" ... />

<!-- GOOD -->
<Sequence DisplayName="Process invoice data" ... />
<If DisplayName="Check if amount is valid" ... />
```

---

## Exception Rules

### Exception-FullyQualified
**Severity:** WARN

Use short form for exceptions.

```vb
' BAD
New UiPath.Core.BusinessRuleException("message")
New System.ApplicationException("message")

' GOOD
New BusinessRuleException("message")
New ApplicationException("message")
```

### Exception-SystemException
**Severity:** WARN

Don't use generic System.Exception.

```vb
' BAD
New System.Exception("message")

' GOOD
New BusinessRuleException("message")  ' For business rules
New ApplicationException("message")   ' For system errors
```

---

## Auto-Fixable Rules

The following rules can be automatically fixed with `--fix`:

| Rule | Fix Applied |
|------|-------------|
| HALL-Version | Change V3/V4 to V5 |
| HALL-ElementType | Change to valid enum value |
| TYPE-001 | Add sd: prefix to DataTable |
| TYPE-002 | Add sd: prefix to DataRow |
| HALL-NExtractData | Change DataTable=/Result= to ExtractedData= |
| HALL-NGetText | Change Result= to Value= |
| HALL-QueueProperty | Change QueueType= to QueueName= |
| Exception-FullyQualified | Use short form |

---

## Running Validation

```bash
# Basic validation (XML well-formedness only)
python -m scripts.validate_xaml ./MyProject

# Full validation with lint rules
python -m scripts.validate_xaml ./MyProject --lint

# Strict mode (includes naming conventions)
python -m scripts.validate_xaml ./MyProject --lint --strict

# Auto-fix issues
python -m scripts.validate_xaml ./MyProject --lint --fix

# Output as JSON
python -m scripts.validate_xaml ./MyProject --lint --json

# Quiet mode (errors only)
python -m scripts.validate_xaml ./MyProject --lint --quiet
```
