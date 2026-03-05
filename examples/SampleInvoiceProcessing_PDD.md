# Process Definition Document
## Process: Invoice Processing Automation
### Version 1.0 — For Testing the ReFramework Generator

---

## 1. Process Overview

**Process Name:** Invoice Processing  
**Department:** Finance / Accounts Payable  
**Robot Type:** Unattended  
**Transaction Source:** Orchestrator Queue (Queue name: `InvoiceProcessing_Queue`)

The robot automatically processes incoming supplier invoices received by email.
For each invoice, it opens the ERP system (SAP), validates the invoice data against
purchase orders, posts the invoice if valid, and archives the original email.

---

## 2. Applications Used

- **Outlook Web App (OWA)** — URL: `https://mail.company.com`
- **SAP GUI** — URL/Transaction: `SE80`, main transaction `FB60`
- **SharePoint** — URL: `https://company.sharepoint.com/finance/archive`

---

## 3. Transaction Item Fields

Each queue item represents one invoice email and contains:

| Field | Type | Description |
|-------|------|-------------|
| EmailID | String | Unique email identifier in OWA |
| SenderEmail | String | Supplier email address |
| InvoiceNumber | String | Invoice number from subject/body |
| InvoiceDate | DateTime | Date on the invoice |
| InvoiceAmount | Double | Total amount on the invoice |
| Currency | String | EUR, USD, GBP |
| PurchaseOrderNumber | String | Referenced PO number |

---

## 4. Process Steps

### Step 1: Open Invoice Email
1. Navigate to OWA using URL from configuration
2. Search inbox for email by EmailID from transaction item
3. Open the email and download the PDF attachment
4. Save PDF to temp folder: `C:\Temp\Invoices\{InvoiceNumber}.pdf`
5. If email not found: throw `InvoiceEmailNotFoundException`

### Step 2: Extract Invoice Data
1. Open the saved PDF using Document Understanding or manual reading
2. Extract: invoice number, date, amount, currency, supplier VAT number
3. Cross-check extracted invoice number with InvoiceNumber from queue item
4. If mismatch: throw `InvoiceDataMismatchException`
5. Store extracted data in output variables for downstream steps

### Step 3: Validate Against Purchase Order
1. Navigate to SAP transaction `ME23N`
2. Enter PurchaseOrderNumber from transaction item
3. Read PO total amount and currency
4. Compare invoice amount with PO amount — allowed tolerance: 5%
5. If amount exceeds tolerance: throw `AmountExceedsToleranceException`
6. If PO not found in SAP: throw `PurchaseOrderNotFoundException`
7. Verify currency matches

### Step 4: Post Invoice in SAP
1. Navigate to SAP transaction `FB60`
2. Enter vendor invoice details: amount, date, currency, reference number
3. Assign cost center from PO
4. Click Post button
5. Capture confirmation document number
6. If SAP times out or returns error: throw ApplicationException to trigger retry

### Step 5: Archive Email and Update Status
1. Move original email in OWA to "Processed" folder
2. Upload PDF copy to SharePoint archive folder: `/finance/archive/{Year}/{Month}/`
3. Add confirmation document number as metadata on SharePoint file
4. Delete temp PDF from `C:\Temp\Invoices\`

---

## 5. Business Rules

- Invoices with amount = 0 or negative must be rejected (BusinessRuleException)
- Invoices older than 90 days from today must be flagged and skipped
- Maximum invoice amount without manual approval: 50,000 EUR equivalent
- PO must be in "Open" or "Partially Delivered" status — "Closed" POs are rejected
- Duplicate invoices (same InvoiceNumber already posted): throw `DuplicateInvoiceException`

---

## 6. Exception Handling

### Business Exceptions (no retry)
| Exception | Condition |
|-----------|-----------|
| `InvoiceEmailNotFoundException` | Email with given ID not found in OWA |
| `InvoiceDataMismatchException` | Extracted invoice number ≠ queue item invoice number |
| `AmountExceedsToleranceException` | Invoice amount > PO amount + 5% tolerance |
| `PurchaseOrderNotFoundException` | PO number not found in SAP |
| `DuplicateInvoiceException` | Invoice already posted in SAP |
| `InvalidAmountException` | Invoice amount is zero or negative |

### System Exceptions (trigger retry, max 3 times)
| Exception | Condition |
|-----------|-----------|
| `SAPTimeoutException` | SAP does not respond within 30 seconds |
| `OWAConnectionException` | OWA not reachable or session expired |
| `SharePointUploadException` | SharePoint upload fails |

---

## 7. Configuration

| Setting | Default | Type |
|---------|---------|------|
| OWA_URL | https://mail.company.com | Setting |
| SAP_Server | sap-prod.company.com | Setting |
| SharePoint_BaseURL | https://company.sharepoint.com/finance | Setting |
| MaxRetryNumber | 3 | Setting |
| InvoiceTolerance_Percent | 5 | Constant |
| MaxInvoiceAmount_EUR | 50000 | Constant |
| InvoiceMaxAgeDays | 90 | Constant |
| OWA_CredentialAsset | OWA_ServiceAccount | Asset |
| SAP_CredentialAsset | SAP_ServiceAccount | Asset |
| SharePoint_CredentialAsset | SharePoint_ServiceAccount | Asset |

---

*End of PDD — ReFramework Generator Test Document*
