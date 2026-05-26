# Template 06 — Gold Records

**Mode:** Async homework (no meeting required for the export itself; a brief call to frame the ask is recommended)
**Duration:** ~30 minutes for the client to export and annotate; 2–4 hours for the FDE to review and normalize
**Attendees:** Whoever administers the client's CRM — often an ops person or the head of sales

---

## Why this matters (share this with the client)

We can build a generic AI extractor in a day. To make it work specifically for your business — tuned to the leads you actually close, the signals that actually predict your conversion, the accounts that are actually your ICP — we need labeled examples from your real history.

Your CRM has this. Every B2B firm with a working sales process has a history of prospects that were qualified, nurtured, or disqualified — and the notes or activities that drove those decisions. We need 50–100 of those records, marked with the disposition.

**This is the single most valuable thing you will provide in this entire engagement.** Without it, the calibration of the AI system is generic — it will work roughly as well as any off-the-shelf GTM tool. With it, the system knows your ICP, your qualification logic, and your signal patterns. The benchmark calibration becomes *yours*.

The export takes about 30 minutes. We have laid out exactly what to export below.

---

## What to export

### Minimum viable export (required)

A CSV or spreadsheet with one row per prospect record, including:

| Column | Description | Example |
|---|---|---|
| `record_id` | Any unique identifier (CRM ID, row number, etc.) | `opp-10042` |
| `company_name` | Company name | `Acme Corp` |
| `company_size_employees` | Headcount band or number | `51-200` or `87` |
| `industry` | Industry or vertical | `Professional services` |
| `contact_title` | Title of the primary contact | `VP of Engineering` |
| `contact_seniority` | Seniority level | `VP`, `Director`, `C-suite` |
| `deal_source` | Channel the record came from | `LinkedIn inbound`, `referral`, `cold email` |
| `disposition` | Your team's verdict on this record | `qualified`, `nurture`, `disqualified` |
| `disposition_reason` | One sentence: why this disposition | `Budget confirmed, project live in Q3` |
| `raw_notes` | The actual CRM notes, activity log, or email snippet that led to the disposition | Paste or export the raw text |

**The `raw_notes` column is the most important.** It is the source document the AI system extracts signals from. Even a few sentences of real CRM notes are more valuable than perfectly formatted firmographic data.

### Preferred export (adds significant calibration value)

If your CRM tracks it, also include:

| Column | Description |
|---|---|
| `deal_size_usd` | Deal size if the record became a client |
| `sales_cycle_days` | Days from first contact to close/disqualify |
| `num_touches_before_close` | Number of calls, emails, or meetings before a decision |
| `champion_identified` | Yes/No: was an internal champion identified? |
| `budget_confirmed` | Yes/No: was budget confirmed during the cycle? |
| `timeline_stated` | Yes/No: did the prospect state a target start date? |
| `competitor_mentioned` | Yes/No and which competitor, if known |
| `trigger_event` | What event triggered their engagement, if known |

---

## How to pull this from common CRMs

### HubSpot

1. Go to **Contacts** or **Deals** (deals preferred if you track disposition there)
2. Create a filtered view: last 18 months, include all lifecycle stages
3. Export → CSV, selecting the columns above
4. If CRM notes are in the Activity feed rather than a column: export the **Activity** log separately (Reports → Activity → Export), join on contact or deal ID

### Salesforce

1. Reports → New Report → Opportunities + Activities
2. Filter: CloseDate in last 18 months, include all stages (Closed Won, Closed Lost, Disqualified)
3. Add columns: Account Name, Account Size, Industry, Primary Contact Title, Lead Source, StageName (disposition), Description (notes)
4. Export to CSV

### Pipedrive / Attio / Close

Use the built-in export function (usually under Settings → Data → Export) and select Deals with notes. Include the loss reason field if you track it.

### Clay / Apollo (if your source of truth is there rather than a CRM)

Export your People or Leads list, filtered to "contacted in last 18 months," including the status field and any notes you have added.

### No CRM or scattered notes

If you do not have a CRM or your notes are in email threads and Google Docs: that is fine. Export what you have — even 20–30 records with disposition and a paragraph of context per record is enough to run a meaningful calibration. We can work with imperfect data.

---

## Disposition guidance

If your team does not already use a consistent three-way disposition, use these definitions:

| Disposition | Definition |
|---|---|
| `qualified` | You believed this was a real buying opportunity — right fit, real budget, real timeline. Include deals that became clients AND deals that were qualified but stalled or went dark. |
| `nurture` | You believed this was a potential fit but not ready now — no active project, early in their buying cycle, or budget not available yet. |
| `disqualified` | You determined this was not a fit — wrong size, wrong industry, wrong problem, no budget path, or a "fake yes" pattern. |

If you already have more granular stage data (e.g., Closed Won, Closed Lost, No Decision, Churned), export it as-is — we will normalize it.

---

## Privacy and data handling

All records are used solely for calibrating your engagement artifacts. We will:

- Strip any PII not needed for the calibration (personal email addresses, personal phone numbers) before the records enter any automated processing
- Store the records only in the engagement directory on infrastructure you control or have approved
- Not use your records to train any general model or share them with any other engagement

If your firm has a data-handling policy that requires a DPA or NDA to cover this export, let us know before you send — we will arrange the appropriate agreement.

---

## FDE: what to do with the records once received

### Step 1 — Validate completeness

- [ ] At least 50 records received (push for 100 if < 50)
- [ ] `disposition` column present and populated for all records
- [ ] `raw_notes` column has content for at least 80% of records
- [ ] Distribution of dispositions: at least 20% qualified, at least 20% disqualified (a skewed export biases calibration)

If the export is thin (< 50 records, < 80% notes coverage), go back to the client before normalizing. A thin gold set produces a misleadingly confident calibration.

### Step 2 — Normalize dispositions

Map any non-standard disposition values to `qualified` / `nurture` / `disqualified`:

| Client's value | Normalize to |
|---|---|
| Closed Won | qualified |
| Closed Lost (fit issue) | disqualified |
| Closed Lost (timing) | nurture |
| No Decision | nurture |
| Disqualified | disqualified |
| (empty) | flag for review |

### Step 3 — Convert to JSONL

Each record becomes one line in `06_gold_records.jsonl`. Format:

```json
{
  "record_id": "opp-10042",
  "source_text": "<paste raw_notes here>",
  "metadata": {
    "company_name": "Acme Corp",
    "company_size_employees": "51-200",
    "industry": "Professional services",
    "contact_title": "VP of Engineering",
    "deal_source": "LinkedIn inbound"
  },
  "disposition": "qualified",
  "disposition_reason": "Budget confirmed, project live in Q3",
  "gold_labels": []
}
```

The `gold_labels` field starts empty. It is populated by the `extract-overrides` step, which runs the schema against the `source_text` and produces entity extractions the FDE then reviews against the `disposition` to check coherence.

### Step 4 — Spot-check 10 records manually

Before running the automated extraction:

1. Read the `source_text` of 10 random records
2. For each, note which `gtm@v1` labels you would expect to find in the text
3. Confirm the `disposition` matches what the text would suggest

If more than 2 of 10 dispositions feel mismatched to the text, flag it with the client — the CRM data may be stale or the dispositions may have been entered inconsistently. A 20% mismatch rate in the gold set will produce calibration noise that is hard to diagnose later.

---

## FDE notes

**Number of records received:** _______________

**Disposition distribution (qualified / nurture / disqualified):** _______________

**Notes coverage (% of records with meaningful raw notes):** _______________

**Any data quality issues found during spot-check:** _______________________________________________

**Normalization decisions made (document any non-obvious mapping):** _______________________________________________
