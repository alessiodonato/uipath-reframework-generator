# XAML Injection Guide

Patterns and rules for injecting extracted metadata into XAML template files.

## Placeholder syntax

All placeholders use `{{PLACEHOLDER}}` format, replaced via Python `.replace()`.

## Common replacements (applied to all files)

| Placeholder | Source | Notes |
|-------------|--------|-------|
| `{{PROCESS_NAME}}` | `metadata["process_name"]` | PascalCase |
| `{{PROCESS_DESCRIPTION}}` | `metadata["process_description"]` | Escaped in XML attributes |
| `{{MAX_RETRY_NUMBER}}` | `metadata["max_retry_number"]` | Integer as string |
| `{{QUEUE_NAME}}` | `metadata["queue_name"]` | May be empty |
| `{{TRANSACTION_SOURCE}}` | `metadata["transaction_source"]` | Queue/Excel/Database/API |
| `{{APPLICATIONS_LIST}}` | `", ".join(apps)` | Comma-separated |
| `{{CURRENT_DATE}}` | `datetime.now().strftime("%Y-%m-%d")` | |
| `{{VERSION}}` | Script constant | |

## VB.NET type mappings

| Simple type | XAML x:TypeArguments |
|-------------|---------------------|
| String | `x:String` |
| Integer | `x:Int32` |
| Boolean | `x:Boolean` |
| DateTime | `s:DateTime` |
| DataTable | `sd:DataTable` |
| Double | `x:Double` |
| QueueItem | `ui:QueueItem` |
| Dictionary | `scg:Dictionary(x:String, x:Object)` |

## XML attribute escaping rules

When injecting text into XML attributes (e.g., `Annotation.AnnotationText`):
- `&` → `&amp;`
- `<` → `&lt;`
- `>` → `&gt;`
- `"` inside attribute → `&quot;`
- Newline in annotation → `&#xA;`

Example:
```xml
sap2010:Annotation.AnnotationText="Step 1: Navigate to URL&#xA;Step 2: Enter credentials&#xA;Rule: Amount &gt; 0"
```

## Process.xaml — step invocation pattern

```xml
<!-- Step {id}: {name} -->
<ui:InvokeWorkflowFile
  DisplayName="{id} - {name}"
  sap2010:Annotation.AnnotationText="{description}&#xA;Steps: {first_3_pseudo_steps}"
  WorkflowFileName="Business\{name}.xaml"
  UnSafe="False">
  <ui:InvokeWorkflowFile.Arguments>
    <InArgument x:TypeArguments="ui:QueueItem" x:Key="in_TransactionItem">[in_TransactionItem]</InArgument>
    <InArgument x:TypeArguments="scg:Dictionary(x:String, x:Object)" x:Key="in_Config">[in_Config]</InArgument>
    <!-- Output variables (from step.output_variables): -->
    <OutArgument x:TypeArguments="{vb_type}" x:Key="out_{varName}">[{varName}]</OutArgument>
  </ui:InvokeWorkflowFile.Arguments>
</ui:InvokeWorkflowFile>
```

## Business step XAML — variable declaration pattern

```xml
<Sequence.Variables>
  <Variable x:TypeArguments="x:String" Name="extractedValue" />
  <Variable x:TypeArguments="x:Boolean" Name="isValid" />
  <Variable x:TypeArguments="sd:DataTable" Name="resultTable" />
</Sequence.Variables>
```

## Exception handling patterns

### BusinessRuleException in Process.xaml
```xml
<Catch x:TypeArguments="uia:BusinessRuleException">
  <ActivityAction x:TypeArguments="uia:BusinessRuleException">
    <ActivityAction.Argument>
      <DelegateInArgument x:TypeArguments="uia:BusinessRuleException" Name="bizException" />
    </ActivityAction.Argument>
    <Sequence>
      <ui:LogMessage Level="Warn" Message="['[ProcessName] BRE: ' + bizException.Message]" />
      <!-- SetTransactionStatus → Failed (no retry) -->
    </Sequence>
  </ActivityAction>
</Catch>
```

### ApplicationException (system) — bubbles to Main.xaml
```xml
<!-- Do NOT catch ApplicationException in Process.xaml -->
<!-- Let it propagate to Main.xaml catch block -->
<!-- Main.xaml will: increment ConsecutiveSystemExceptions, go to Init state -->
```

## GetTransactionData — Queue vs DataTable

### Queue
```xml
<ui:GetQueueItem
  QueueName="[Config('OrchestratorQueueName').ToString()]"
  TimeoutMS="30000"
  Result="[out_TransactionItem]" />
```

### DataTable (Excel/DB)
```vb
' Row index = in_TransactionNumber - 1
' Access field: TransactionData.Rows(idx)("FieldName").ToString()
' Signal end: set out_TransactionItem = Nothing
```

## Log message conventions

```
[ProcessName] StateName - Action | TxRef: ref
[ProcessName] StepName - Started | TxRef: abc123
[ProcessName] StepName - Completed | OutputVar: value
[ProcessName] Transaction SUCCESSFUL | Ref: abc123
[ProcessName] Transaction FAILED (Business) | Ref: abc123 | Duplicate invoice
[ProcessName] Transaction FAILED (System) | Ref: abc123 | Timeout waiting for SAP
[ProcessName] Init Error: Could not load Config.xlsx
[ProcessName] Process completed. Total transactions: 42
```

## Config dictionary access in VB.NET

```vb
' Safe access (recommended):
in_Config("SettingName").ToString()

' With default fallback:
If(in_Config.ContainsKey("SettingName"), in_Config("SettingName").ToString(), "defaultValue")

' Integer setting:
CInt(in_Config("MaxRetryNumber"))

' Queue item specific content:
in_TransactionItem.SpecificContent("FieldName").ToString()
in_TransactionItem.Reference  ' Orchestrator reference string
```

## Namespace declarations required per XAML file

### Minimum (all files)
```xml
xmlns="http://schemas.microsoft.com/netfx/2009/xaml/activities"
xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006"
xmlns:sap2010="http://schemas.microsoft.com/netfx/2010/xaml/activities/presentation"
xmlns:ui="http://schemas.uipath.com/workflow/activities"
xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
```

### Additional (when needed)
```xml
xmlns:mva="clr-namespace:Microsoft.VisualBasic.Activities;assembly=System.Activities"
xmlns:s="clr-namespace:System;assembly=mscorlib"           <!-- DateTime, String[] -->
xmlns:scg="clr-namespace:System.Collections.Generic;assembly=mscorlib"  <!-- Dictionary, List -->
xmlns:sd="clr-namespace:System.Data;assembly=System.Data"  <!-- DataTable -->
xmlns:uia="clr-namespace:UiPath.Core;assembly=UiPath.Core" <!-- BusinessRuleException -->
```
