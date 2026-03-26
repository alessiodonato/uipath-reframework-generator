<p align="center">
  <img src="https://img.shields.io/badge/UiPath-ReFramework%20Generator-ff6c37?style=for-the-badge&logo=uipath&logoColor=white" alt="ReFramework Generator"/>
</p>

<h3 align="center">Generate production-ready UiPath projects from a PDD in seconds</h3>

<p align="center">
  <a href="#quick-start">Quick Start</a> •
  <a href="#features">Features</a> •
  <a href="#how-it-works">How it Works</a> •
  <a href="#contributing">Contributing</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-3776ab?style=flat-square&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/UiPath-24.10+-fa4616?style=flat-square&logo=uipath&logoColor=white" alt="UiPath"/>
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat-square" alt="License"/>
  <img src="https://img.shields.io/badge/Tests-55%20passed-success?style=flat-square" alt="Tests"/>
</p>

---

## The Problem

Setting up a UiPath ReFramework project takes **hours** of repetitive work:
- Wiring the State Machine
- Configuring exception handling
- Creating workflow stubs
- Setting up Config.xlsx
- Writing boilerplate code

## The Solution

Upload a PDD → Get a **fully-wired, compilable UiPath project** in seconds.

```
📄 Your PDD (PDF/DOCX)  →  🤖 AI Extraction  →  📦 Ready-to-open UiPath Project
```

---

## Quick Start

```bash
# Clone & setup
git clone https://github.com/alessiodonato/uipath-reframework-generator.git
cd uipath-reframework-generator
export ANTHROPIC_API_KEY=sk-ant-...

# Generate project
python scripts/generate_reframework.py --input MyProcess_PDD.pdf --output ./output/

# Open in UiPath Studio → project.json
```

<details>
<summary><b>More options</b></summary>

```bash
# Interactive mode
python scripts/generate_reframework.py

# Preview metadata only
python scripts/generate_reframework.py --input PDD.pdf --metadata-only

# Different project variants
python scripts/generate_reframework.py --input PDD.pdf --variant sequence

# Validate generated XAML
python scripts/generate_reframework.py --input PDD.pdf --validate
```

</details>

---

## Features

| Feature | Description |
|---------|-------------|
| **State Machine** | Complete Init → GetTx → Process → End flow with retry logic |
| **Exception Handling** | BusinessRuleException vs ApplicationException done right |
| **Config.xlsx** | Pre-filled settings, constants, and credential placeholders |
| **Business Workflows** | Rich pseudo-code stubs from your PDD |
| **XAML Validation** | 30+ lint rules to catch common errors |
| **Multiple Variants** | ReFramework, Dispatcher, Performer, or Sequence |

### Generated Output

```
YourProcess/
├── project.json              # Open in UiPath Studio
├── Main.xaml                 # ✅ Complete State Machine
├── Process.xaml              # ✅ All steps wired
├── Data/
│   └── Config.xlsx           # ⚙️ Add URLs & credentials
├── Framework/
│   ├── InitAllSettings.xaml
│   ├── GetTransactionData.xaml
│   └── SetTransactionStatus.xaml
└── Business/
    └── {YourSteps}.xaml      # 🔧 Add UI selectors
```

---

## How it Works

1. **Extract** — AI reads your PDD and extracts: process steps, applications, exceptions, config values, transaction fields

2. **Generate** — Creates all XAML files with proper namespaces, annotations, and framework wiring

3. **Validate** — Runs 30+ lint rules to catch hallucinations and ensure Studio compatibility

4. **Package** — Outputs a ZIP ready to open in UiPath Studio

---

## Transaction Sources

| Source | Status |
|--------|--------|
| Orchestrator Queue | ✅ Full support |
| Excel / DataTable | ✅ Stub included |
| Database | ✅ Stub included |
| REST API | ✅ Stub included |

---

## Additional Tools

<details>
<summary><b>XAML Validation</b></summary>

```bash
python -m validate_xaml path/to/project/ --lint --strict
python -m validate_xaml path/to/project/ --fix  # Auto-fix issues
```

</details>

<details>
<summary><b>Config Manager</b></summary>

```bash
python scripts/config_manager.py list path/to/Config.xlsx
python scripts/config_manager.py add path/to/Config.xlsx --name "Setting" --value "value"
```

</details>

<details>
<summary><b>Framework Wiring</b></summary>

```bash
python scripts/modify_framework.py wire-uielement path/to/project/
python scripts/modify_framework.py insert-invoke path/to/Process.xaml --workflow "Business/Step.xaml"
```

</details>

---

## Testing

```bash
python -m unittest discover tests/ -v  # 55 tests
```

---

## Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

**Open tasks:**
- [ ] Orchestrator deployment scripts
- [ ] Document Understanding stubs
- [ ] More activity generators

---

## License

[MIT](LICENSE) — free to use, modify, and distribute.

---

<p align="center">
  <i>Designed for UiPath Studio 24.10+</i>
</p>
