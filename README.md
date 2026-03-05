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
| Business step pseudo-steps from PDD | ✅ As comments | Add UI selectors |
| Output variables declared per step | ✅ Typed | — |
| Application open/login stubs | ✅ With hints | Add selectors |
| Config.xlsx Settings + Constants | ✅ Pre-filled | Add real URLs/creds |
| project.json with NuGet dependencies | ✅ Complete | Studio installs on open |
| Transaction source (Queue/Excel/DB/API) | ✅ Configured | — |

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
git clone https://github.com/YOUR_ORG/uipath-reframework-generator.git
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

## Project structure

```
uipath-reframework-generator/
├── SKILL.md                           ← Claude skill instructions
├── README.md                          ← This file
├── LICENSE                            ← MIT
├── requirements.txt
├── setup.py
├── scripts/
│   └── generate_reframework.py        ← Main generator (500+ lines)
├── assets/
│   └── xaml-templates/
│       ├── Main.xaml                  ← State Machine template
│       ├── Process.xaml               ← Process loop template
│       ├── InitAllApplications.xaml   ← App init template
│       └── GetTransactionData.xaml    ← Transaction retrieval template
└── references/
    ├── extraction-prompt.md           ← Claude API system prompt
    ├── xaml-guide.md                  ← XAML patterns + type mappings
    └── config-template.md             ← Config.xlsx structure + openpyxl code
```

---

## Contributing

Contributions welcome! Open issues and PRs for:

- [ ] Additional XAML activity types (Send Email, HTTP Request, DB Query)
- [ ] Linear process template support (non-transactional)
- [ ] Orchestrator deployment script generation (`publish.ps1`)
- [ ] XAML validation before packaging
- [ ] Sample PDD documents for testing
- [ ] Support for UiPath Document Understanding activity stubs
- [ ] Multi-language support (English + Italian PDD tested)

Please open an issue before submitting large PRs.

---

## License

[MIT](LICENSE) — free to use, modify, and distribute.

---

*Built with [Claude AI](https://anthropic.com) · Designed for UiPath Studio 24.10+*
*Not affiliated with UiPath, Inc.*
