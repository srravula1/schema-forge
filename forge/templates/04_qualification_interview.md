# Template 04 — Qualification Interview

**Mode:** Live call
**Duration:** 45 minutes
**Attendees:** Head of Sales (required); founder optional but welcome)

---

## FDE pre-call checklist

- [ ] Templates 01–03 complete; review the won-deal and lost-deal summaries before this call
- [ ] Identify which `Q_*` evidence labels from `gtm@v1` are likely to appear (see baseline schema)
- [ ] Recording consent confirmed

**FDE note:** This session maps the client's actual qualification process to the schema's `Q_*` evidence labels. Come in with the baseline `Q_*` labels printed or visible — you will be mapping responses to them in real time. The goal is not a theoretical description of their process; it is the real process their reps follow, including the informal rules that are never written down.

Baseline `Q_*` labels for reference:
- `Q_NEED_ARTICULATED` — prospect has explicitly described their problem
- `Q_BUDGET_CONFIRMED` — budget or budget range has been confirmed
- `Q_AUTHORITY_IDENTIFIED` — decision-maker(s) identified and accessible
- `Q_TIMELINE_STATED` — prospect has stated a target start or go-live date
- `Q_CURRENT_STATE_DESCRIBED` — prospect has described their current process or tooling
- `Q_DESIRED_STATE_DESCRIBED` — prospect has described their target outcome
- `Q_EVALUATION_CRITERIA_KNOWN` — you know how they will decide between vendors
- `Q_CHAMPION_CONFIRMED` — an internal advocate who will push the deal forward is identified
- `Q_DISPOSITION` — the overall qualification verdict (qualified / nurture / disqualify)

---

## Agenda (share with attendees beforehand)

| Time | Topic |
|---|---|
| 0–3 min | Framing |
| 3–20 min | Walk through 3 SQLs that closed won |
| 20–33 min | Evidence gates: what is required at each stage |
| 33–40 min | The deal-breaker question |
| 40–45 min | AI consulting specific: what kills deals |

---

## Section 1 — Walk through 3 SQLs that became closed-won

**FDE prompt:** "Walk me through your last three SQLs that became closed-won deals, one at a time. For each, I want you to tell me: what evidence did you have at the point of discovery call, what evidence did you have before you sent the proposal, and what evidence did you have before you sent the contract?"

**FDE note:** For each stage, ask them to be specific about what the evidence looked like in practice — not "we confirmed budget" but "they told us they had $X approved in Q3" or "the CFO was on the call." The specifics map to extraction guidance for each `Q_*` label.

---

**SQL S-1**

- Client descriptor: _______________________________________________
- Evidence at discovery call:
  - Need articulated? (What did they say?) _______________________________________________
  - Budget signal? _______________________________________________
  - Authority identified? _______________________________________________
  - Timeline stated? _______________________________________________
  - Anything else that stood out? _______________________________________________
- Evidence at proposal stage:
  - What new evidence appeared between discovery and proposal? _______________________________________________
  - What evidence was still missing that you accepted the ambiguity on? _______________________________________________
- Evidence at contract stage:
  - What confirmed for you that this was ready to close? _______________________________________________

**SQL S-2**

- Client descriptor: _______________________________________________
- Evidence at discovery call:
  - Need articulated? _______________________________________________
  - Budget signal? _______________________________________________
  - Authority identified? _______________________________________________
  - Timeline stated? _______________________________________________
  - Anything else that stood out? _______________________________________________
- Evidence at proposal stage:
  - What new evidence appeared between discovery and proposal? _______________________________________________
  - What evidence was still missing? _______________________________________________
- Evidence at contract stage:
  - What confirmed for you that this was ready to close? _______________________________________________

**SQL S-3**

- Client descriptor: _______________________________________________
- Evidence at discovery call:
  - Need articulated? _______________________________________________
  - Budget signal? _______________________________________________
  - Authority identified? _______________________________________________
  - Timeline stated? _______________________________________________
  - Anything else that stood out? _______________________________________________
- Evidence at proposal stage:
  - What new evidence appeared between discovery and proposal? _______________________________________________
  - What evidence was still missing? _______________________________________________
- Evidence at contract stage:
  - What confirmed for you that this was ready to close? _______________________________________________

---

## Section 2 — Evidence gates at each stage

**FDE prompt:** "I want to establish what evidence is required — not what is nice to have — at each stage of your process. Let's go stage by stage."

### Before a discovery call

"What evidence must exist before you or your team will book a discovery call with a prospect? Not 'would be nice to have' — what is required? If that evidence is missing, what happens to the prospect?"

> _Required evidence:_ _______________________________________________

> _What happens if it is missing?_ _______________________________________________

### Before sending a proposal

"After discovery, what evidence must be present before you send a proposal? Again, required, not preferred."

> _Required evidence:_ _______________________________________________

> _What happens if it is missing?_ _______________________________________________

### Before sending a contract

"After the proposal, what must be true before you send the contract? Who has to have said what, and what has to have been confirmed?"

> _Required evidence:_ _______________________________________________

> _What happens if it is missing?_ _______________________________________________

---

## Section 3 — The deal-breaker

**FDE prompt (read verbatim):** "Here is a specific question: what is the single piece of missing evidence that kills a deal even when everything else is there? Meaning — budget is there, the problem is real, the champion is engaged, but one thing is missing and you walk away or the deal dies. What is that thing?"

**FDE note:** This question surfaces the dominant deal-breaker for this client's business. For AI consulting specifically, the spec notes it tends to break on "do they have a real project ready" rather than budget — but do not lead toward that answer. Let them tell you.

> _Primary deal-breaker:_ _______________________________________________

> _Follow-up — has this changed in the last year?_ _______________________________________________

**FDE prompt:** "Now think about the second-most-common deal-breaker — the one that comes up when that first thing is not the issue. What is it?"

> _Secondary deal-breaker:_ _______________________________________________

---

## Section 4 — AI consulting specific

**FDE prompt:** "For your specific business — AI consulting, implementation, advisory, whatever form it takes — I want to understand the mix of what kills deals. When you lose a deal or a deal stalls, is the blocker more often: (a) budget — they don't have the money or can't free it up; (b) authority — the right person isn't in the room or can't move without approvals you haven't found; or (c) timing — the project isn't real yet, the internal readiness isn't there, or they're 'exploring.' Which of these three kills the most deals for you?"

> _Answer — rank or describe:_ _______________________________________________

**Follow-up — timing specifically:** "When you say a deal died on timing, what does that look like exactly? What did the prospect say or do, and what was the signal that this was a real project that was early versus a project that would never happen?"

> _Notes:_ _______________________________________________

**Follow-up — internal readiness:** "For AI consulting specifically, is there an 'internal readiness' check you do? Something that tells you whether the client's organization can actually absorb and use what you build, even if they have the budget and the authority?"

> _Notes:_ _______________________________________________

---

## FDE post-call notes

To be completed within 30 minutes of the call.

**Primary deal-breaker (specific language from the client):**

> _Notes:_ _______________________________________________

**Evidence gates that matched or diverged from the baseline `Q_*` schema:**

> _Notes:_ _______________________________________________

**Any `Q_*` labels that need to be added for this client (things they check that the baseline does not capture):**

> _Notes:_ _______________________________________________

**Proposed `policy_overrides.yaml` edits (rough draft):**

```yaml
# Draft — review and edit before running generate
disqualification_rules:
  - condition: ""   # e.g. "Q_TIMELINE_STATED is null AND A_INDUSTRY in ['Enterprise']"
    rationale: ""

auto_pass_rules:
  - condition: ""   # e.g. "Q_BUDGET_CONFIRMED AND Q_AUTHORITY_IDENTIFIED AND confidence > 0.7"
    rationale: ""

hil_rules:
  - condition: ""
    rationale: ""
```
