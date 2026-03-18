---
name: uipath-reframework-generator
description: >
  Generate a complete, production-ready UiPath ReFramework project (all XAML files +
  project.json + Config.xlsx) from a Process Definition Document (PDD) in PDF or DOCX format.
  Use this skill whenever the user mentions UiPath, ReFramework, RPA, PDD, robot, automation
  scaffolding, workflow generation, or asks to generate/scaffold a UiPath project from a document.
  Also trigger when the user uploads a PDF/DOCX and mentions robot, transaction, automation,
  workflow, or process. This skill generates ALL framework files ready to open in UiPath Studio.
---

# UiPath ReFramework Generator Skill

Generates a **complete, production-ready UiPath Studio project** from a Process Definition Document
(PDD) in PDF or DOCX format. The output ZIP opens directly in UiPath Studio with no setup required
beyond filling in credentials and adding UI selectors.

## What gets generated

```
{ProcessName}/
├── project.json                      ← Open this in UiPath Studio
├── Main.xaml                         ← Complete State Machine (all 4 states, retry logic)
├── Process.xaml                      ← InvokeWorkflowFile per step, mapped from PDD
├── README.md                         ← Checklist with every TODO item
├── Data/
│   ├── Config.xlsx                   ← Settings + Constants, pre-filled from PDD
│   └── extracted_metadata.json      ← Full AI extraction output for reference
├── Framework/
│   ├── InitAllSettings.xaml          ← Reads Config.xlsx → populates Config dictionary
│   ├── InitAllApplications.xaml      ← One stub per app identified in PDD
│   ├── GetTransactionData.xaml       ← Queue/Excel/Database/API branch, pre-configured
│   ├── SetTransactionStatus.xaml     ← Complete: Success/Business/System handling
│   ├── CloseAllApplications.xaml     ← TryCatch per app, graceful close
│   └── KillAllProcesses.xaml        ← TryCatch per app, force kill
└── Business/
    ├── {StepName}.xaml               ← One per process step: executable pseudo-steps + variables
    └── Open{AppName}.xaml            ← One per app: credential hints + login guide
```

## Workflow

### Step 1 — Read the document

Check `/mnt/user-data/uploads/` for uploaded files. Use bash to extract text:

```bash
# Install deps if needed
pip install pdfminer.six python-docx --break-system-packages -q

# PDF extraction
python3 -c "
from pdfminer.high_level import extract_text
text = extract_text('/mnt/user-data/uploads/YOUR_FILE.pdf')
print(text[:500])  # preview
print(f'Total: {len(text)} chars')
"

# DOCX extraction
python3 -c "
import docx
doc = docx.Document('/mnt/user-data/uploads/YOUR_FILE.docx')
text = '\n'.join(p.text for p in doc.paragraphs if p.text.strip())
print(text[:500])
print(f'Total: {len(text)} chars')
"
```

If no file is uploaded: ask the user to upload a PDD (PDF or DOCX).

### Step 2 — Extract metadata via Claude API

Call the Anthropic API using the extraction prompt in `references/extraction-prompt.md`.
The API returns a rich JSON with steps, pseudo-steps, exceptions, variables, and config keys.

Key fields to extract:
- `process_steps[].pseudo_steps` — concrete numbered sub-steps referencing Config keys
- `process_steps[].config_keys_used` — list of Config keys read in this step
- `process_steps[].output_variables` — variables needed by downstream steps
- `process_steps[].throws` — list of {exception_type, condition} for exceptions
- `business_exceptions[].suggested_step` — which step throws the exception
- `transaction_item_fields[]` — typed fields with descriptions
- `config_settings[]` — with type (Setting/Constant/Asset) and description

### Step 3 — Run the generator script

The Python script at `scripts/generate_reframework.py` handles all generation.
Copy it to the work directory and run:

```bash
cp -r /path/to/skill/* /home/claude/skill/
pip install pdfminer.six python-docx openpyxl anthropic --break-system-packages -q

python3 /home/claude/skill/scripts/generate_reframework.py \
  --input /mnt/user-data/uploads/YOUR_FILE.pdf \
  --output /home/claude/ \
  --api-key $ANTHROPIC_API_KEY
```

The script auto-installs missing dependencies and produces a project directory.

### Step 4 — ZIP and deliver

```bash
cd /home/claude
zip -r "{ProcessName}_ReFramework.zip" "{ProcessName}/"
cp "{ProcessName}_ReFramework.zip" /mnt/user-data/outputs/
```

Then use `present_files` to share the ZIP.

### Step 5 — Tell the user what to do next

Always tell the user:
1. Extract the ZIP, open `project.json` in UiPath Studio
2. Studio installs NuGet packages automatically on first open
3. Open `Data/Config.xlsx` → fill in all `TODO: add URL` cells
4. Verify credential asset names match what's in Orchestrator
5. For each `Business/*.xaml` — search `<!-- TODO:` to find implementation points
6. The generated `README.md` inside the ZIP has a full checklist

## Quality standards for generated XAML

- Every activity must have `DisplayName` and `sap2010:Annotation.AnnotationText`
- **Rich annotations** use format: `Reads: Config('key') | Output: varName (Type) | Throws: ExceptionType if condition`
- **Pseudo-steps** are generated as executable structure (LogMessage + Sequence placeholder), not just comments
- **Exception handling**:
  - BusinessRuleException: caught in `Process.xaml`, calls `SetTransactionStatus` with "BusinessException", does NOT rethrow → no retry
  - ApplicationException: NOT caught in `Process.xaml`, bubbles to `Main.xaml` → retry logic applies
- **Log message templates** (standardized across all files):
  - InitAllSettings: `[ProcessName] Init - Loading configuration`
  - GetTransactionData: `[ProcessName] GetTx - Transaction retrieved: {TxRef}`
  - SetTransactionStatus: `[ProcessName] SetStatus - {TxRef} → {Status}`
  - CloseAllApplications: `[ProcessName] Close - Closing {AppName}`
  - KillAllProcesses: `[ProcessName] Kill - Terminating {ProcessExecutable}`
- All `TODO` items must be inside `<!-- TODO: ... -->` XML comments or as annotation text
- XAML must be valid well-formed XML (escape `&` as `&amp;`, `<` as `&lt;` in attributes)
- Arguments must be explicitly typed — `scg:Dictionary(x:String, x:Object)` is allowed for Config

## Error handling during generation

- No document uploaded → ask user to upload PDD (PDF or DOCX)
- Empty or scanned PDF → inform user, ask for text-based version
- API returns malformed JSON → retry once with stricter prompt
- Missing transaction source → default to Queue, inform user
- Missing process steps → generate single placeholder step, add warning in README

## Reference files

Read these when needed:
- `references/extraction-prompt.md` — Full system prompt for metadata extraction
- `references/xaml-guide.md` — XAML injection patterns, type mappings, and log templates
- `references/config-template.md` — Config.xlsx structure and openpyxl code
- `tests/test_generator.py` — Validation test suite (validates XML, checks Object types, verifies logs)
