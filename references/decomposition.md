# Workflow Decomposition Patterns

Best practices for structuring UiPath ReFramework projects.

---

## Core Principles

1. **One workflow = one responsibility**
2. **One UI scope per workflow** (don't mix apps)
3. **150 lines max** per workflow
4. **Navigation separate from action**
5. **Extraction returns ALL data** (filtering is separate)

---

## Folder Structure

```
MyProject/
├── Main.xaml                    # Entry point (State Machine)
├── Process.xaml                 # Process state logic
├── Framework/                   # ReFramework files (don't modify)
│   ├── InitAllSettings.xaml
│   ├── InitAllApplications.xaml
│   ├── GetTransactionData.xaml
│   ├── SetTransactionStatus.xaml
│   ├── CloseAllApplications.xaml
│   └── KillAllProcesses.xaml
├── Business/                    # Business logic
│   ├── Step1_ExtractData.xaml
│   ├── Step2_ValidateData.xaml
│   └── Step3_UpdateSystem.xaml
├── Workflows/                   # App-specific workflows
│   ├── WebApp/
│   │   ├── WebApp_Launch.xaml
│   │   ├── WebApp_NavigateToSearch.xaml
│   │   ├── WebApp_SearchRecord.xaml
│   │   └── WebApp_Close.xaml
│   └── DesktopApp/
│       ├── DesktopApp_Launch.xaml
│       ├── DesktopApp_FillForm.xaml
│       └── DesktopApp_Close.xaml
├── Utils/                       # Reusable utilities
│   ├── Browser_NavigateToUrl.xaml
│   ├── App_Close.xaml
│   └── Data_ValidateRecord.xaml
└── Data/
    └── Config.xlsx
```

---

## Naming Conventions

### Workflow Files

```
{AppName}_{Action}.xaml

Examples:
WebApp_Launch.xaml
WebApp_SearchInvoice.xaml
SAP_PostDocument.xaml
Excel_LoadData.xaml
```

### Utility Workflows

```
{Category}_{Action}.xaml

Examples:
Browser_NavigateToUrl.xaml
App_Close.xaml
Data_ValidateRecord.xaml
File_ArchiveDocument.xaml
```

### Variables

```
{scope}{Type}{Name}

Scopes:
- str = String
- int = Int32
- dt = DataTable
- row = DataRow
- bool = Boolean
- sec = SecureString
- ui = UiElement

Examples:
strInvoiceNumber
intRetryCount
dtTransactions
rowCurrent
boolIsValid
secPassword
uiWebApp
```

### Arguments

```
{direction}_{Name}

Directions:
- in_ = InArgument
- out_ = OutArgument
- io_ = InOutArgument

Examples:
in_Config
in_TransactionItem
out_Result
io_uiWebApp
```

---

## Workflow Patterns

### Launch Pattern (Required Structure)

Every app launch workflow must follow this structure:

```
AppName_Launch.xaml
├── Arguments:
│   ├── in_strUrl (from Config)
│   ├── in_strCredentialAssetName
│   └── out_uiAppName (UiElement output)
│
├── Log: "[ProcessName] Init - Opening AppName"
├── NApplicationCard (OpenMode="Always")
│   ├── OutUiElement → out_uiAppName
│   └── Body:
│       ├── Variables: strUsername, secPassword
│       ├── RetryScope:
│       │   └── GetRobotCredential
│       ├── NTypeInto (username)
│       ├── NTypeInto (password, SecureText)
│       ├── NClick (login button)
│       └── Pick (login validation):
│           ├── Success: NCheckState → dashboard visible
│           └── Failure: NGetText → error, Throw BRE
│
└── Log: "[ProcessName] Init - AppName ready"
```

### Navigation Pattern

Separate navigation from action:

```
1. Browser_NavigateToUrl.xaml    # Generic URL navigation
2. WebApp_SearchInvoice.xaml     # App-specific action

# In Process:
Invoke Browser_NavigateToUrl (url from Config)
Invoke WebApp_SearchInvoice (perform action)
```

### Extraction Pattern

Return ALL data, filter separately:

```
WebApp_ExtractInvoices.xaml
├── NExtractData → dtAllInvoices
└── Return dtAllInvoices  # NO filtering here

Process.xaml
├── Invoke WebApp_ExtractInvoices → dtAllInvoices
├── FilterDataTable (dtAllInvoices → dtPendingInvoices)
└── ForEach row In dtPendingInvoices...
```

### Close Pattern

Generic close in Utils, specific close in app folder:

```
Utils/App_Close.xaml              # Generic: accepts UiElement
Workflows/WebApp/WebApp_Close.xaml  # Specific: knows WebApp details
```

---

## ReFramework Decomposition

### Dispatcher Pattern

```
Main.xaml (State Machine)
├── Init → InitAllSettings, InitAllApplications
│   └── Load source data (Excel/DB/API)
├── GetTransactionData → Return next DataRow
├── Process → Add to Orchestrator Queue
└── End → CloseAllApplications

GetTransactionData.xaml
├── If first call: already loaded
├── Return dtSourceData.Rows(in_TransactionNumber - 1)
└── Return Nothing when done

Process.xaml
├── Build QueueItem fields from DataRow
├── AddQueueItem
└── Log item added
```

### Performer Pattern

```
Main.xaml (State Machine)
├── Init → InitAllSettings, InitAllApplications
│   └── Open required apps
├── GetTransactionData → GetQueueItem
├── Process → Process transaction
└── End → CloseAllApplications

Process.xaml
├── Extract fields from QueueItem
├── Invoke business step workflows
├── Catch BusinessRuleException → SetTransactionStatus(Failed/Business)
└── Let ApplicationException bubble up for retry
```

---

## Architecture Rules

### A-1: Apps Open in Init
**Severity:** ERROR

All applications must be opened and ready in InitAllApplications.
Process workflows only attach (OpenMode="Never").

```
InitAllApplications.xaml
├── Invoke WebApp_Launch (OpenMode="Always")
│   └── OutUiElement → out_uiWebApp
├── Invoke DesktopApp_Launch
│   └── OutUiElement → out_uiDesktopApp
└── Pass UiElements to Process via Main.xaml variables

Process.xaml (and action workflows)
├── NApplicationCard (OpenMode="Never")
│   └── Attach to existing uiWebApp
└── Perform actions
```

### A-2: Persistence in Main Only
**Severity:** ERROR

CreateFormTask, WaitForFormTaskAndResume must be in Main.xaml only.

### A-3: Credentials Inside Using Workflow
**Severity:** ERROR

GetRobotCredential must be called inside the workflow that uses the credentials.
Never pass credentials as arguments.

```
# BAD
InitAllApplications.xaml
├── GetRobotCredential → username, password
└── Invoke WebApp_Launch (passing username, password)

# GOOD
WebApp_Launch.xaml
├── GetRobotCredential → username, password (inside workflow)
└── Use credentials immediately
```

### A-4: Don't Modify SetTransactionStatus
**Severity:** ERROR

SetTransactionStatus.xaml should use the default implementation.
Customization breaks exception handling patterns.

### A-5: Modular Decomposition
**Severity:** ERROR

Maximum 150 lines per workflow. Split larger workflows.

### A-6: Navigation Separate
**Severity:** ERROR

Navigation to a page = separate invoke.
Action on page = separate invoke.

```
# BAD
WebApp_SearchAndUpdate.xaml  # Does both navigation and action

# GOOD
Invoke Browser_NavigateToUrl (search page URL)
Invoke WebApp_Search (search action)
Invoke Browser_NavigateToUrl (update page URL)
Invoke WebApp_Update (update action)
```

### A-7: Log Bookends
**Severity:** WARN

Every workflow should have START and END log messages.

```
Log: "[ProcessName] WorkflowName - Started"
... workflow logic ...
Log: "[ProcessName] WorkflowName - Completed"
```

### A-8: URLs from Config
**Severity:** WARN

Never hardcode URLs. Always use Config().

```
# BAD
"https://example.com/login"

# GOOD
in_Config("WebApp_URL").ToString()
```

### A-9: Browser Defaults
**Severity:** WARN

Recommended browser settings:
- `IsIncognito="True"` - Clean session each run
- `InteractionMode="Simulate"` - Faster, more reliable
- `AttachMode="SingleWindow"` - Avoid tab confusion

### A-10: One Browser Per App
**Severity:** WARN

Don't share browser tabs across different apps.
Each web app gets its own browser instance.

### A-11: API in RetryScope
**Severity:** WARN

Wrap API/network calls in RetryScope.

```
RetryScope (3 retries, 5s interval)
└── HttpClient request
```

### A-12: Extraction Returns All
**Severity:** WARN

Extraction workflows return ALL data.
Filtering is done separately by caller.

---

## Exception Handling

### Business vs Application Exception

| Exception | When | Retry? | Caught Where |
|-----------|------|--------|--------------|
| BusinessRuleException | Invalid data, business rule violation | No | Process.xaml |
| ApplicationException | System error, app failure | Yes | Main.xaml |

### Pattern

```
Process.xaml
├── TryCatch
│   ├── Try: Invoke business steps
│   ├── Catch BusinessRuleException:
│   │   ├── SetTransactionStatus (Failed/Business)
│   │   └── Do NOT rethrow
│   └── Let ApplicationException pass through
└── Main.xaml handles retry via state machine
```

---

## UiElement Chain

Pass UiElement references through the workflow chain:

```
InitAllApplications.xaml
├── WebApp_Launch → out_uiWebApp
└── Return out_uiWebApp

Main.xaml
├── Variable: uiWebApp (UiElement)
├── Init: uiWebApp = out_uiWebApp from InitAllApplications
├── Process: pass io_uiWebApp to Process.xaml
└── End: pass in_uiWebApp to CloseAllApplications

Process.xaml
├── Argument: io_uiWebApp (InOutArgument)
└── Pass to action workflows

WebApp_SearchInvoice.xaml
├── Argument: io_uiWebApp (InOutArgument)
├── NApplicationCard (OpenMode="Never", attach to io_uiWebApp)
└── Perform actions
```

Wiring command:
```bash
python scripts/modify_framework.py wire-uielement ./MyProject WebApp
```
