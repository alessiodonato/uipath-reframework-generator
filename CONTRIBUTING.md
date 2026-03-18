# Contributing to UiPath ReFramework Generator

First off — thank you for taking the time to contribute! 🎉  
This project aims to save RPA developers hours of boilerplate work, and every improvement matters.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How to contribute](#how-to-contribute)
- [Reporting bugs](#reporting-bugs)
- [Suggesting features](#suggesting-features)
- [Submitting a Pull Request](#submitting-a-pull-request)
- [Development setup](#development-setup)
- [Coding standards](#coding-standards)
- [What we accept](#what-we-accept)
- [What we don't accept](#what-we-dont-accept)

---

## Code of Conduct

Be respectful, constructive, and welcoming. We don't tolerate harassment of any kind.  
If something feels off, open an issue or contact the maintainer directly.

---

## How to contribute

There are several ways to help, not just writing code:

- 🐛 **Report a bug** — something broke? Tell us
- 💡 **Suggest a feature** — have an idea? Open a discussion
- 📄 **Improve documentation** — typos, unclear sections, missing examples
- 🧪 **Add test PDDs** — real-world PDD examples that improve extraction quality
- 🔧 **Fix a bug** — pick an open issue and submit a PR
- ✨ **Implement a feature** — check the roadmap in README first

---

## Reporting bugs

Before opening an issue, please:
1. Search existing issues to avoid duplicates
2. Make sure you're on the latest version

When opening a bug report, include:
- Python version (`python --version`)
- How you ran the script (CLI args used)
- The error message or unexpected output (full traceback)
- A sanitized/anonymized version of the input PDD if possible
- What you expected to happen vs. what actually happened

> ⚠️ **Never attach real PDDs with sensitive business information.** Anonymize or use a synthetic document.

---

## Suggesting features

Open a [GitHub Issue](../../issues/new) with the label `enhancement` and describe:
- What problem does this solve?
- What should the output look like?
- Are there UiPath-specific constraints to consider?

For large changes (new transaction sources, new XAML activity types, new output formats), please **open an issue before writing code** so we can align on the approach.

---

## Submitting a Pull Request

1. **Fork** the repository and clone your fork locally
2. **Create a branch** from `main` with a descriptive name:
   ```bash
   git checkout -b fix/pdf-extraction-encoding
   git checkout -b feat/add-email-activity-stubs
   ```
3. **Make your changes** (see [Development setup](#development-setup) below)
4. **Test your changes** manually with at least one PDF and one DOCX input
5. **Commit** with a clear message following [Conventional Commits](https://www.conventionalcommits.org/):
   ```
   fix: handle empty paragraphs in DOCX extraction
   feat: add stub for Send Email activity in Business workflows
   docs: clarify API key setup in README
   refactor: extract XAML generation into separate module
   ```
6. **Push** to your fork and open a Pull Request against `main`
7. Fill in the PR template — describe what changed and why
8. Wait for review. We aim to respond within a few days.

### PR checklist

Before submitting, confirm:
- [ ] The script runs end-to-end without errors on a sample PDD
- [ ] Generated XAML is well-formed XML (no unclosed tags, no unescaped `&`)
- [ ] No API keys, credentials, or real PDD content included
- [ ] `requirements.txt` updated if you added a new dependency
- [ ] Documentation updated if behavior changed

---

## Development setup

```bash
# Clone your fork
git clone https://github.com/alessiodonato/uipath-reframework-generator.git
cd uipath-reframework-generator

# Install dependencies
pip install -r requirements.txt

# Set your API key
export ANTHROPIC_API_KEY=sk-ant-...

# Run against the sample PDD included in the repo
python scripts/generate_reframework.py \
  --input examples/SampleInvoiceProcessing_PDD.md \
  --output ./test-output/

# Preview extracted metadata without generating files
python scripts/generate_reframework.py \
  --input examples/SampleInvoiceProcessing_PDD.md \
  --metadata-only
```

Inspect the output in `./test-output/` and open the generated XAML files in a text editor to verify correctness before submitting.

---

## Coding standards

- **Python 3.8+ compatible** — no walrus operators, no `match` statements
- **No external dependencies beyond `requirements.txt`** without discussion
- **Functions must be focused** — one responsibility per function
- **New XAML templates** must include `sap2010:Annotation.AnnotationText` on every activity
- **All TODO comments** in generated XAML must use the `<!-- TODO: ... -->` format
- **Log messages** in generated XAML must follow the convention: `[ProcessName] Step - Action`
- **No hardcoded values** in generated files — everything must come from Config.xlsx or be a placeholder
- Code style: follow the existing style in `generate_reframework.py` (no formatter enforced, just be consistent)

---

## What we accept

| Type | Examples |
|------|---------|
| Bug fixes | PDF extraction failures, malformed XAML, wrong Config.xlsx values |
| New transaction sources | SAP BAPIs, REST API pagination, Database stored procedures |
| New activity stubs | Send Email, HTTP Request, Document Understanding, OCR |
| Better pseudocode generation | Richer prompts that extract more detail from PDDs |
| New XAML templates | Linear process template, Attended robot template |
| Sample PDDs | Anonymized real-world examples that test edge cases |
| Documentation | Clearer README, better inline comments, usage examples |
| CI/CD | GitHub Actions for XML validation, Python linting |

---

## What we don't accept

- Changes that remove the `<!-- TODO: -->` markers from generated stubs (they are intentional)
- Dependencies that require paid licenses or API keys other than Anthropic
- Generated XAML that targets a specific UiPath version and breaks others
- PRs that include real PDD documents with company/client data
- Breaking changes to the CLI interface without a deprecation path
- Code that calls external services other than the Anthropic API

---

## Questions?

Open a [GitHub Discussion](../../discussions) — we're happy to help you get started.

---

*Thanks again for contributing. Every PR, issue, and suggestion makes this tool better for the entire RPA community.* 🤖
