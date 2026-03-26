# 🤖 UiPath ReFramework Generator

> An open-source Claude AI skill that generates a **complete, production-ready UiPath ReFramework project** from a Process Definition Document (PDD) in PDF or DOCX format.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![UiPath Studio 24.10](https://img.shields.io/badge/UiPath-24.10+-orange.svg)](https://uipath.com)
[![Powered by Claude](https://img.shields.io/badge/AI-Claude%20Sonnet-blueviolet.svg)](https://anthropic.com)

---

## What it does

Upload a PDD (Process Definition Document) — formal or informal, PDF or DOCX — and the tool:

1. **Extracts** all process metadata using Claude AI: applications, steps, sub-steps, exceptions, transaction fields, config values
2. **Generates** a full UiPath project with every XAML file pre-wired
3. **Delivers** a ZIP you extract and open directly in UiPath Studio

**The generated project compiles immediately in UiPath Studio.** The developer only needs to add UI selectors inside `Business/*.xaml` stubs.

---

## Generated output

```
YourProcessName/
├── project.json                       ← Open this in UiPath Studio
├── Main.xaml                          ← ✅ Complete State Machine
├── Process.xaml                       ← ✅ All steps wired via InvokeWorkflowFile
├── README.md                          ← ✅ Full implementation checklist
├── Data/
│   ├── Config.xlsx                    ← ⚠️  Pre-filled, add real URLs/credentials
│   └── extracted_metadata.json       ← Reference: AI extraction output
├── Framework/
│   ├── InitAllSettings.xaml           ← ⚠️  Reads Config.xlsx → Config dictionary
│   ├── InitAllApplications.xaml       ← ✅ Stub per application
│   ├── GetTransactionData.xaml        ← ✅ Queue/Excel/Database/API pre-configured
│   ├── SetTransactionStatus.xaml      ← ✅ Complete: Success/Business/System logic
│   ├── CloseAllApplications.xaml      ← ⚠️  Add Close Browser/App selectors
│   └── KillAllProcesses.xaml         ← ⚠️  Add OS process names to kill
└── Business/
    ├── Open{AppName}.xaml             ← ⚠️  Login stub with credential + URL hints
    └── {StepName}.xaml               ← 🔧 Rich pseudocode — add UI selectors
```

`✅ Ready` | `⚠️ Configure` | `🔧 Implement`

---

## What gets auto-generated vs what needs manual work

| Component | Auto-generated | Manual work needed |
|-----------|---------------|-------------------|
| State Machine (Init/GetTx/Process/End) | ✅ Complete | — |
| Retry logic + ConsecutiveSystemExceptions | ✅ Complete | — |
| BusinessRuleException vs ApplicationException split | ✅ Complete | — |
| Orchestrator log fields + log conventions | ✅ Complete | — |
| SetTransactionStatus (Success/Business/System) | ✅ Complete | — |
| Process step invocations in Process.xaml | ✅ Wired | — |
| Business step pseudo-steps from PDD | ✅ Executable structure | Add UI selectors |
| Output variables declared per step | ✅ Typed | — |
| Application open/login stubs | ✅ With hints | Add selectors |
| Config.xlsx Settings + Constants | ✅ Pre-filled | Add real URLs/creds |
| project.json with NuGet dependencies | ✅ Complete | Studio installs on open |
| Transaction source (Queue/Excel/DB/API) | ✅ Configured | — |

---

## Key features

### Exception handling

The generator implements correct UiPath ReFramework exception handling:

| Exception Type | Caught in | Action | Retry? |
|----------------|-----------|--------|--------|
| `BusinessRuleException` | `Process.xaml` | `SetTransactionStatus → Failed` | ❌ No |
| `ApplicationException` | `Main.xaml` | Rethrown, retry logic applies | ✅ Yes |

- **BusinessRuleException**: Caught in Process.xaml, calls SetTransactionStatus with "BusinessException" status, does NOT rethrow
- **ApplicationException**: NOT caught in Process.xaml, bubbles to Main.xaml for retry handling

### Rich annotations

Every XAML activity includes standardized annotations:

```
Reads: Config('AppName_URL'), Config('AppName_CredentialAsset')
Output: confirmationNumber (String)
Throws: ApplicationException if login fails
```

### Executable pseudo-steps

Business steps from PDD are generated as executable structure (not just comments):

```xml
<!-- For each pseudo-step: -->
<LogMessage Message="[ProcessName] StepName - Step 1: Navigate to URL" Level="Trace" />
<Sequence DisplayName="Navigate to URL from Config('App_URL')">
  <!-- TODO: implement - Navigate to URL from Config('App_URL') -->
</Sequence>
```

### Standardized log messages

All framework files use consistent log templates:

| File | Log format |
|------|------------|
| InitAllSettings | `[ProcessName] Init - Loading configuration` |
| GetTransactionData | `[ProcessName] GetTx - Transaction retrieved: {TxRef}` |
| SetTransactionStatus | `[ProcessName] SetStatus - {TxRef} → {Status}` |
| CloseAllApplications | `[ProcessName] Close - Closing {AppName}` |

---

## Quick start

### Option A — As a Claude Skill (claude.ai)

1. Add `SKILL.md` to your Claude skills
2. Upload your PDD in a conversation
3. Say: *"Generate a UiPath ReFramework project from this PDD"*
4. Download the ZIP → extract → open `project.json` in Studio

### Option B — Python CLI (standalone)

```bash
# Clone the repo
git clone https://github.com/alessiodonato/uipath-reframework-generator.git
cd uipath-reframework-generator

# Set your API key
export ANTHROPIC_API_KEY=sk-ant-...

# Install dependencies
pip install -r requirements.txt

# Run (interactive mode)
python scripts/generate_reframework.py

# Run (direct mode)
python scripts/generate_reframework.py \
  --input ./MyProcess_PDD.pdf \
  --output ./output/

# Preview extracted metadata only (no files generated)
python scripts/generate_reframework.py \
  --input ./MyProcess_PDD.pdf \
  --metadata-only

# Generate with specific variant
python scripts/generate_reframework.py \
  --input ./MyProcess_PDD.pdf \
  --variant sequence  # Options: reframework, dispatcher, performer, sequence

# Generate and validate XAML
python scripts/generate_reframework.py \
  --input ./MyProcess_PDD.pdf \
  --validate

# Resolve latest NuGet package versions
python scripts/generate_reframework.py \
  --input ./MyProcess_PDD.pdf \
  --resolve-nuget
```

Dependencies are **auto-installed** on first run if missing.

### Option C — pip install

```bash
pip install uipath-reframework-generator
reframework-gen --input MyProcess_PDD.pdf
```

---

## Requirements

| Requirement | Details |
|-------------|---------|
| Python | 3.8+ |
| Anthropic API key | [Get one here](https://console.anthropic.com/) |
| UiPath Studio | 24.10+ (to open generated project) |
| Input format | PDF (text-based) or DOCX |

---

## Example

Given a PDD describing an invoice processing robot, the generator produces:

```
InvoiceProcessing/
├── project.json
├── Main.xaml                          # State Machine with 3-retry logic
├── Process.xaml                       # 5 step invocations: Login, OpenInvoice,
│                                      #   ValidateAmount, PostToSAP, ArchiveDocument
├── Data/Config.xlsx                   # SAP_URL, SAP_CredentialAsset, Min/MaxAmount
└── Business/
    ├── OpenSAP.xaml                   # Hints: URL from Config, Get Credentials asset
    ├── LoginToEmailPortal.xaml        # Hints: IMAP settings, credential asset
    ├── OpenInvoice.xaml               # Pseudo: navigate mailbox, open attachment
    ├── ValidateAmount.xaml            # Pseudo: read Amount field, check range,
    │                                  #   throw InvalidAmountException if out of range
    ├── PostToSAP.xaml                 # Pseudo: navigate to transaction, fill form,
    │                                  #   click Post, verify confirmation number
    └── ArchiveDocument.xaml           # Pseudo: move to archive folder, log reference
```

---

## Supported transaction sources

| Source | Status | Notes |
|--------|--------|-------|
| Orchestrator Queue | ✅ Full | `GetQueueItem` pre-configured |
| Excel / DataTable | ✅ Stub | DataTable branch with row-index pattern |
| Database | ✅ Stub | Execute Query pattern with offset |
| REST API | ✅ Stub | HTTP Request pattern with page index |

---

## Additional tools

### XAML Validation

Validate generated XAML for common LLM hallucination patterns:

```bash
# Validate single file
python -m validate_xaml path/to/file.xaml --lint

# Validate entire project
python -m validate_xaml path/to/project/ --lint --strict

# Auto-fix common issues
python -m validate_xaml path/to/project/ --fix

# JSON output for CI/CD
python -m validate_xaml path/to/project/ --json
```

### Config.xlsx Manager

Manage Config.xlsx settings from CLI:

```bash
python scripts/config_manager.py list path/to/Config.xlsx
python scripts/config_manager.py add path/to/Config.xlsx --name "NewSetting" --value "value"
python scripts/config_manager.py validate path/to/Config.xlsx
```

### Framework Wiring

Wire UiElement chains and insert workflow invocations:

```bash
python scripts/modify_framework.py wire-uielement path/to/project/
python scripts/modify_framework.py insert-invoke path/to/Process.xaml --workflow "Business/NewStep.xaml"
```

---

## Project structure

```
uipath-reframework-generator/
├── SKILL.md                           ← Claude skill instructions
├── README.md                          ← This file
├── LICENSE                            ← MIT
├── requirements.txt
├── setup.py
├── scripts/
│   ├── generate_reframework.py        ← Main generator (1400+ lines)
│   ├── config_manager.py              ← Config.xlsx CLI manager
│   ├── modify_framework.py            ← Framework wiring CLI
│   ├── resolve_nuget.py               ← NuGet version resolution
│   ├── generators/                    ← Deterministic XAML generators
│   │   ├── core.py                    ← Sequence, If, ForEach, TryCatch, etc.
│   │   ├── logging.py                 ← LogMessage, Comment
│   │   ├── invoke.py                  ← InvokeWorkflowFile
│   │   ├── orchestrator.py            ← GetQueueItem, SetTransactionStatus
│   │   ├── ui_automation.py           ← NClick, NTypeInto, NGetText (V5)
│   │   ├── error_handling.py          ← Throw, Rethrow, RetryScope
│   │   └── data.py                    ← BuildDataTable, FilterDataTable
│   └── validate_xaml/                 ← XAML validation module
│       ├── validator.py               ← Core validation logic
│       ├── constants.py               ← Locked enums, known activities
│       └── fixer.py                   ← Auto-fix common issues
├── assets/
│   ├── xaml-templates/                ← ReFramework templates
│   │   ├── Main.xaml                  ← State Machine template
│   │   ├── Process.xaml               ← Process loop + BusinessRuleException catch
│   │   ├── InitAllApplications.xaml   ← App init template
│   │   └── GetTransactionData.xaml    ← Transaction retrieval template
│   └── sequence-template/             ← Simple sequence template
│       └── Main.xaml                  ← Linear automation (no transaction loop)
├── references/
│   ├── extraction-prompt.md           ← Claude API system prompt
│   ├── xaml-guide.md                  ← XAML patterns, type mappings, log templates
│   ├── config-template.md             ← Config.xlsx structure + openpyxl code
│   ├── lint-rules.md                  ← Complete lint rules documentation
│   ├── expressions.md                 ← VB.NET expression reference
│   ├── decomposition.md               ← Workflow decomposition patterns
│   └── cheat-sheet.md                 ← Quick reference for CLI and generators
└── tests/
    ├── test_generator.py              ← Generator validation tests
    ├── test_generators.py             ← XAML generator unit tests (55 tests)
    ├── test_validation.py             ← Validation module tests
    ├── test_pdd.txt                   ← Sample PDD for testing
    └── lint-test-cases/               ← XAML files for lint testing
        ├── valid_workflow.xaml
        ├── version_v3.xaml
        └── unqualified_datatable.xaml
```

---

## Testing

Run the complete test suite (55 tests):

```bash
python -m unittest discover tests/ -v
```

The tests cover:
- **XAML generators**: All deterministic generators produce valid XML
- **Validation module**: Hallucination detection, enum validation, type checking
- **Lint rules**: Version=V3 detection, ElementType=DataGrid, unqualified DataTable
- **Error handling**: BusinessRuleException vs ApplicationException patterns

Run individual test modules:

```bash
python -m unittest tests.test_generators -v    # Generator tests
python -m unittest tests.test_validation -v   # Validation tests
```

---

## Contributing

Contributions welcome! Open issues and PRs for:

- [x] ~~Additional XAML activity types~~ *(added deterministic generators)*
- [x] ~~Linear process template support~~ *(added --variant sequence)*
- [ ] Orchestrator deployment script generation (`publish.ps1`)
- [x] ~~XAML validation before packaging~~ *(added validate_xaml module with 30+ lint rules)*
- [x] ~~Sample PDD documents for testing~~ *(added test_pdd.txt)*
- [x] ~~NuGet version resolution~~ *(added --resolve-nuget flag)*
- [ ] Support for UiPath Document Understanding activity stubs
- [x] ~~Multi-language support~~ *(English + Italian PDD tested)*

Please open an issue before submitting large PRs.

---

## License

[MIT](LICENSE) — free to use, modify, and distribute.

---

*Built with [Claude AI](https://anthropic.com) · Designed for UiPath Studio 24.10+*
*Not affiliated with UiPath, Inc.*
