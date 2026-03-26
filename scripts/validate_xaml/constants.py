"""
Constants for XAML validation - enum values, known activities, namespaces.

These are locked down to prevent LLM hallucinations. If an activity uses
an enum value not in these lists, it will be flagged as an error.
"""

# ═══════════════════════════════════════════════════════════════════════════════
# VALID ENUM VALUES
# ═══════════════════════════════════════════════════════════════════════════════

VALID_ENUMS = {
    # NTypeInto.EmptyFieldMode - CRITICAL: LLMs often hallucinate wrong values
    "EmptyFieldMode": {"SingleLine", "MultiLine", "None"},

    # NTypeInto/NClick Version - Must be V5 for modern activities
    "Version": {"V5"},  # V3 crashes Studio

    # ClickBeforeMode for NTypeInto
    "ClickBeforeMode": {"None", "Single", "Double"},

    # InteractionMode for UI activities
    "InteractionMode": {"Simulate", "HardwareEvents", "ChromiumApi", "WindowMessages"},

    # InputMode for NClick
    "InputMode": {"Simulate", "HardwareEvents", "ChromiumApi", "WindowMessages"},

    # OpenMode for NApplicationCard
    "OpenMode": {"Always", "IfNotOpen", "Never"},

    # AttachMode for NApplicationCard
    "AttachMode": {"SingleWindow", "AllWindows"},

    # NExtractData ElementType - LLMs often use wrong values
    "ElementType": {"Table", "DropDown", "InputBox", "TextArea", "Custom"},
    # WRONG: DataGrid, ComboBox, InputBoxText (these crash Studio)

    # QueueItem status
    "QueueItemStatus": {"New", "InProgress", "Failed", "Successful", "Abandoned", "Retried", "Deleted"},

    # SetTransactionStatus ErrorType
    "ErrorType": {"Business", "Application"},

    # Log levels - attribute name is "Level" in ui:LogMessage
    "Level": {"Trace", "Info", "Warn", "Error", "Fatal"},

    # Retry scope retry strategy
    "RetryStrategy": {"Fixed", "Exponential"},
}

# ═══════════════════════════════════════════════════════════════════════════════
# KNOWN ACTIVITIES AND THEIR VALID PROPERTIES
# ═══════════════════════════════════════════════════════════════════════════════

KNOWN_ACTIVITIES = {
    # Modern UI Automation (uix: namespace)
    "uix:NClick": {
        "valid_props": {"DisplayName", "Target", "ClickType", "InputMode", "Version",
                       "VerifyOptions", "ScopeIdentifier", "Timeout", "DelayAfter",
                       "DelayBefore", "ContinueOnError"},
        "invalid_props": {"Selector", "Element", "WaitForReady"},  # Hallucination patterns
        "required_children": {"uix:NClick.Target"},
    },
    "uix:NTypeInto": {
        "valid_props": {"DisplayName", "Target", "Text", "SecureText", "ActivateBefore",
                       "ClickBeforeMode", "EmptyFieldMode", "Version", "VerifyOptions",
                       "ScopeIdentifier", "Timeout", "DelayAfter", "DelayBefore"},
        "invalid_props": {"Selector", "Element", "EmptyField", "RetryOnError"},
        "required_children": {"uix:NTypeInto.Target"},
    },
    "uix:NGetText": {
        "valid_props": {"DisplayName", "Target", "Value", "Version", "ScopeIdentifier",
                       "Timeout", "UseFullText"},
        "invalid_props": {"Selector", "Element", "Result", "DataTable"},
        "required_children": {"uix:NGetText.Target"},
    },
    "uix:NSelectItem": {
        "valid_props": {"DisplayName", "Target", "Item", "Version", "ScopeIdentifier",
                       "Timeout"},
        "invalid_props": {"Selector", "Element", "InteractionMode"},  # InteractionMode doesn't exist
        "required_children": {"uix:NSelectItem.Target"},
    },
    "uix:NCheckState": {
        "valid_props": {"DisplayName", "Target", "Version", "ScopeIdentifier", "Timeout",
                       "Result", "VerifyOptions"},
        "invalid_props": {"Selector", "Element", "Appears", "WaitForVisible"},
        "required_children": {"uix:NCheckState.Target"},
    },
    "uix:NApplicationCard": {
        "valid_props": {"DisplayName", "OpenMode", "AttachMode", "Url", "BrowserType",
                       "OutUiElement", "Body", "IsIncognito", "WindowSelector"},
        "invalid_props": {"Selector", "Application", "Url="},  # Url= is wrong syntax
        "required_children": {"uix:NApplicationCard.Body"},
    },
    "uix:NGoToUrl": {
        "valid_props": {"DisplayName", "Url", "NavigationDelay", "Timeout"},
        "invalid_props": {"Browser", "Element"},
    },
    "uix:NExtractData": {
        "valid_props": {"DisplayName", "Target", "ExtractedData", "ExtractMetadata",
                       "Version", "ScopeIdentifier", "Timeout", "MaxNumberOfResults"},
        "invalid_props": {"DataTable", "Result", "Output"},  # Common hallucinations
        "required_children": {"uix:NExtractData.Target", "uix:NExtractData.ExtractMetadata"},
    },

    # Classic UI activities
    "ui:Click": {
        "valid_props": {"DisplayName", "Selector", "Target", "ClickType", "KeyModifiers",
                       "Timeout", "DelayAfter", "DelayBefore", "ContinueOnError"},
    },
    "ui:TypeInto": {
        "valid_props": {"DisplayName", "Selector", "Target", "Text", "EmptyField",
                       "Timeout", "DelayAfter", "DelayBefore", "Activate"},
    },

    # Orchestrator activities
    "ui:GetQueueItem": {
        "valid_props": {"DisplayName", "QueueName", "Result", "TimeoutMS", "FilterStrategy",
                       "ReferenceFilter", "OutputStatus"},
        "invalid_props": {"QueueType", "Queue"},  # QueueType doesn't exist
    },
    "ui:AddQueueItem": {
        "valid_props": {"DisplayName", "QueueName", "ItemInformation", "Reference",
                       "Priority", "DeferDate", "DueDate", "Result"},
        "invalid_props": {"QueueType"},
    },
    "ui:SetTransactionStatus": {
        "valid_props": {"DisplayName", "QueueItem", "Status", "Reason", "ErrorType",
                       "Output", "Analytics"},
        "invalid_props": {"TransactionItem", "Exception"},
    },
    "ui:GetRobotCredential": {
        "valid_props": {"DisplayName", "AssetName", "Username", "Password", "Folder"},
        "invalid_props": {"CredentialName", "Asset"},
    },
    "ui:GetRobotAsset": {
        "valid_props": {"DisplayName", "AssetName", "Value", "Folder"},
    },

    # Control flow
    "If": {
        "valid_props": {"DisplayName", "Condition"},
        "required_children": {"If.Then"},
    },
    "Switch": {
        "valid_props": {"DisplayName", "Expression"},
        "required_children": {"Switch.Cases"},
    },
    "ForEach": {
        "valid_props": {"DisplayName", "Values"},
        "required_children": {"ForEach.Body"},
    },
    "While": {
        "valid_props": {"DisplayName", "Condition"},
        "required_children": {"While.Body"},
    },
    "TryCatch": {
        "valid_props": {"DisplayName"},
        "required_children": {"TryCatch.Try"},
    },
    "Sequence": {
        "valid_props": {"DisplayName"},
    },
    "Flowchart": {
        "valid_props": {"DisplayName", "StartNode"},
    },

    # Error handling
    "Throw": {
        "valid_props": {"DisplayName", "Exception"},
    },
    "Rethrow": {
        "valid_props": {"DisplayName"},
    },
    "ui:RetryScope": {
        "valid_props": {"DisplayName", "NumberOfRetries", "RetryInterval", "Action",
                       "Condition"},
    },

    # Invoke
    "ui:InvokeWorkflowFile": {
        "valid_props": {"DisplayName", "WorkflowFileName", "Arguments", "UnSafe",
                       "Isolated", "ContinueOnError"},
        "required_children": set(),  # Arguments is optional
    },
    "ui:InvokeCode": {
        "valid_props": {"DisplayName", "Code", "Language", "Arguments"},
    },

    # Logging
    "ui:LogMessage": {
        "valid_props": {"DisplayName", "Level", "Message"},
    },
    "ui:AddLogFields": {
        "valid_props": {"DisplayName", "Fields"},
    },
    "ui:RemoveLogFields": {
        "valid_props": {"DisplayName", "FieldNames"},
    },

    # Data operations
    "Assign": {
        "valid_props": {"DisplayName"},
        "required_children": {"Assign.To", "Assign.Value"},
    },
    "ui:BuildDataTable": {
        "valid_props": {"DisplayName", "DataTable", "TableInfo"},
    },
    "ui:FilterDataTable": {
        "valid_props": {"DisplayName", "DataTable", "FilterConditions", "OutputDataTable",
                       "SelectColumns", "KeepColumns"},
    },
    "ui:SortDataTable": {
        "valid_props": {"DisplayName", "DataTable", "SortColumn", "OutputDataTable",
                       "OrderByDirection"},
    },

    # File operations
    "ui:ReadTextFile": {
        "valid_props": {"DisplayName", "FileName", "Content", "Encoding"},
    },
    "ui:WriteTextFile": {
        "valid_props": {"DisplayName", "FileName", "Text", "Encoding", "Append"},
    },
    "ui:PathExists": {
        "valid_props": {"DisplayName", "Path", "PathType", "Exists"},
    },

    # Excel
    "ui:ExcelApplicationScope": {
        "valid_props": {"DisplayName", "WorkbookPath", "Body", "Visible", "Password",
                       "EditPassword", "AutoSave"},
    },
    "ui:ReadRange": {
        "valid_props": {"DisplayName", "SheetName", "Range", "DataTable", "AddHeaders"},
    },
    "ui:WriteRange": {
        "valid_props": {"DisplayName", "SheetName", "StartingCell", "DataTable", "AddHeaders"},
    },

    # HTTP
    "ui:HttpClient": {
        "valid_props": {"DisplayName", "EndPoint", "Method", "Body", "Result", "Headers",
                       "StatusCode", "Timeout", "AcceptFormat"},
    },
}

# ═══════════════════════════════════════════════════════════════════════════════
# REQUIRED NAMESPACES
# ═══════════════════════════════════════════════════════════════════════════════

REQUIRED_NAMESPACES = {
    # Core namespaces
    "xmlns": "http://schemas.microsoft.com/netfx/2009/xaml/activities",
    "xmlns:x": "http://schemas.microsoft.com/winfx/2006/xaml",
    "xmlns:sap2010": "http://schemas.microsoft.com/netfx/2010/xaml/activities/presentation",

    # UiPath namespaces
    "xmlns:ui": "http://schemas.uipath.com/workflow/activities",

    # System namespaces
    "xmlns:s": "clr-namespace:System;assembly=mscorlib",
    "xmlns:scg": "clr-namespace:System.Collections.Generic;assembly=mscorlib",
}

# Namespace prefixes for DataTable/DataRow - LLMs often forget these
DATA_NAMESPACES = {
    "xmlns:sd": "clr-namespace:System.Data;assembly=System.Data",
}

# Modern UI automation namespace
UIX_NAMESPACE = {
    "xmlns:uix": "clr-namespace:UiPath.UIAutomationNext.Activities;assembly=UiPath.UIAutomationNext.Activities",
}

# ═══════════════════════════════════════════════════════════════════════════════
# HALLUCINATION PATTERNS TO DETECT
# ═══════════════════════════════════════════════════════════════════════════════

HALLUCINATION_PATTERNS = [
    # Wrong enum values that crash Studio
    (r'Version="V3"', "ERROR", "Version must be V5, not V3"),
    (r'Version="V4"', "ERROR", "Version must be V5, not V4"),
    (r'ElementType="DataGrid"', "ERROR", "ElementType must be Table, not DataGrid"),
    (r'ElementType="ComboBox"', "ERROR", "ElementType must be DropDown, not ComboBox"),
    (r'ElementType="InputBoxText"', "ERROR", "ElementType must be InputBox, not InputBoxText"),

    # Properties that don't exist
    (r'NApplicationCard\.Url=', "ERROR", "NApplicationCard uses Url attribute, not Url="),
    (r'NCheckState\.Appears=', "ERROR", "NCheckState has no Appears property"),
    (r'NTypeInto\.EmptyField=', "ERROR", "Use EmptyFieldMode, not EmptyField"),
    (r'NSelectItem.*InteractionMode=', "WARN", "NSelectItem has no InteractionMode property"),
    (r'NExtractData.*DataTable=', "ERROR", "Use ExtractedData, not DataTable"),
    (r'NExtractData.*Result=', "ERROR", "Use ExtractedData, not Result"),
    (r'NGetText.*Result=', "ERROR", "Use Value, not Result"),
    (r'GetQueueItem.*QueueType=', "ERROR", "Use QueueName, not QueueType"),

    # Wrong child elements
    (r'\.TargetAnchorable>', "ERROR", "Use .Target, not .TargetAnchorable"),
    (r'\.Selector>', "WARN", "Modern activities use .Target, not .Selector"),

    # Wrong argument patterns
    (r'<x:String[^>]*>.*</x:String>\s*</InArgument>', "WARN", "InArgument should contain expression, not x:String"),
    (r'OutArgument[^>]*>\s*\[\]', "WARN", "Empty OutArgument binding - silent data loss"),
    (r'InOutArgument[^>]*>\s*\[\]', "WARN", "Empty InOutArgument binding - silent data loss"),

    # Type issues
    (r'x:TypeArguments="DataTable"', "ERROR", "Use sd:DataTable, not DataTable"),
    (r'x:TypeArguments="DataRow"', "ERROR", "Use sd:DataRow, not DataRow"),
    (r'Type="DataTable"', "ERROR", "Use Type=\"sd:DataTable\""),

    # Exception patterns
    (r'New System\.Exception\(', "WARN", "Use BusinessRuleException or ApplicationException, not System.Exception"),
    (r'UiPath\.Core\.BusinessRuleException', "WARN", "Use short form: New BusinessRuleException(...)"),
    (r'System\.ApplicationException', "WARN", "Use short form: New ApplicationException(...)"),
]

# ═══════════════════════════════════════════════════════════════════════════════
# ARCHITECTURE RULES
# ═══════════════════════════════════════════════════════════════════════════════

ARCHITECTURE_RULES = {
    # Files that should NOT be modified in standard ReFramework
    "immutable_files": {
        "Framework/SetTransactionStatus.xaml": "SetTransactionStatus should use default implementation",
    },

    # Activities that should only appear in specific files
    "restricted_activities": {
        "CreateFormTask": ["Main.xaml"],  # Persistence only in Main
        "WaitForFormTaskAndResume": ["Main.xaml"],
        "GetQueueItem": ["Framework/GetTransactionData.xaml"],
        "SetTransactionStatus": ["Framework/SetTransactionStatus.xaml", "Process.xaml"],
    },

    # Log message format validation
    "log_format": r"\[{process_name}\]\s+(Init|GetTx|SetStatus|Close|Kill|Process)\s+-\s+.+",
}
