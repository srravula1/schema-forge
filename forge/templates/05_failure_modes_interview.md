# Template 05 — Failure Modes Interview

**Mode:** Async or live (async preferred if the team is short on time; live produces richer answers)
**Duration:** 30 minutes (live) or ~20 minutes to complete in writing (async)
**Attendees:** Head of Sales; optionally the founder or a senior rep who has seen a high volume of deals

---

## FDE pre-call checklist (if running live)

- [ ] Templates 02–04 complete; review the regrets section from the ICP interview before this call
- [ ] Baseline failure-mode library reviewed — know what is already covered so you do not re-collect it
- [ ] Recording consent confirmed (if live)

**FDE note:** This session produces the buyer-specific failure-mode additions to the baseline library. The baseline already covers generic GTM failure modes (false-positive intent signals, enrichment errors, AI-SDR "explores not buyers"). What you are looking for here is the failure modes specific to *this client's* business — the ones that would not appear in any generic sales playbook. Push hard on specifics: the more precisely a client can describe the pre-sale signal they missed, the more useful the failure mode becomes as a detection assertion in the schema.

**If running async:** Send this document to the client via email or Notion with a 48-hour turnaround request. Note that written answers can be shorter than spoken answers — that is fine, as long as the specifics are there.

---

## Section 1 — Prospects who looked great but were not

**FDE prompt:** "Tell me about three prospects who looked great on paper — they had the right industry, the right size, the right title, they said all the right things in early conversations — and turned out to be terrible fits. Not deals you lost, but deals you won and regretted, or deals that got deep into your process and collapsed in a way that cost you real time."

**FDE note:** Ask for three, accept two if that is all they have. For each, the critical piece is the *false signal* — what specifically about this prospect made them look qualified when they were not. "They had a big budget" is not a false signal. "They had confirmed budget but no internal owner for the project, which we only discovered at contract stage" is a false signal.

---

**False positive FP-1**

- Prospect descriptor: _______________________________________________
- What made them look like a great fit? _______________________________________________
- What was the false signal — specifically what was true about them that you thought meant qualified, but didn't? _______________________________________________
- At what point in your process did the truth become clear? _______________________________________________
- What was the cost (time, dollars, opportunity cost)? _______________________________________________
- If you saw the same pattern again, what would you check earlier? _______________________________________________

**False positive FP-2**

- Prospect descriptor: _______________________________________________
- What made them look like a great fit? _______________________________________________
- What was the false signal? _______________________________________________
- At what point did the truth become clear? _______________________________________________
- What was the cost? _______________________________________________
- What would you check earlier? _______________________________________________

**False positive FP-3**

- Prospect descriptor: _______________________________________________
- What made them look like a great fit? _______________________________________________
- What was the false signal? _______________________________________________
- At what point did the truth become clear? _______________________________________________
- What was the cost? _______________________________________________
- What would you check earlier? _______________________________________________

---

## Section 2 — Prospects you nearly missed

**FDE prompt:** "Now the opposite. Tell me about three prospects you nearly passed on or nearly disqualified — you looked at them and thought they were not worth pursuing — but they turned out to be great clients. What was the signal you almost missed, and what made you decide to move forward despite initial hesitation?"

**FDE note:** This section produces the false-negative failure modes — cases where the schema would have routed a prospect to disqualified when the right answer was qualified. These are harder for clients to recall because they do not cause pain the way false positives do. Prompt them with: "Think about a client who came in through an unusual channel, or had an unusual title, or had a use case you had not seen before."

---

**False negative FN-1**

- Client descriptor: _______________________________________________
- What made you initially hesitant? _______________________________________________
- What changed your mind? _______________________________________________
- What was the signal you almost missed? _______________________________________________
- What would you tell a junior rep to look for that you would have told them to ignore before this deal? _______________________________________________

**False negative FN-2**

- Client descriptor: _______________________________________________
- What made you initially hesitant? _______________________________________________
- What changed your mind? _______________________________________________
- What was the signal you almost missed? _______________________________________________
- What would you tell a junior rep to look for? _______________________________________________

**False negative FN-3**

- Client descriptor: _______________________________________________
- What made you initially hesitant? _______________________________________________
- What changed your mind? _______________________________________________
- What was the signal you almost missed? _______________________________________________
- What would you tell a junior rep to look for? _______________________________________________

---

## Section 3 — The "fake yes"

**FDE prompt (read verbatim or paste into async form):** "What does a 'fake yes' look like in your sales process — a prospect who says all the right things, stays engaged, seems enthusiastic, asks smart questions, but never closes? What do they do that a real buyer also does, and what do they NOT do that a real buyer always does?"

**FDE note:** For AI consulting firms, the "fake yes" often takes the form of an executive who is genuinely curious about AI but has no active project, no internal mandate, and no budget cycle. They want the education; they do not want the engagement. The specific behavioral marker (e.g., "they never introduce us to their CFO or CTO, even after three calls") is what makes this a usable detection pattern.

> _What a fake yes does (that a real buyer also does):_ _______________________________________________

> _What a fake yes never does (that a real buyer always does):_ _______________________________________________

> _At what point in your process do you typically realize it is a fake yes?_ _______________________________________________

> _Is there an earlier signal you can now identify in retrospect?_ _______________________________________________

---

## Section 4 — What not to do

**FDE prompt:** "If you had to train a new SDR or junior sales hire on the top five things NOT to do — the mistakes you have seen made repeatedly that cost deals — what would you put on that list? These can be process mistakes, bad signals to chase, wrong assumptions, anything."

**FDE note:** This section is the highest-leverage async section. The "what not to do" list often contains the most actionable failure-mode additions because clients have thought about onboarding junior reps before and have crystallized the patterns. Capture verbatim language where possible — the client's exact phrasing often becomes the failure-mode description.

> 1. _______________________________________________

> 2. _______________________________________________

> 3. _______________________________________________

> 4. _______________________________________________

> 5. _______________________________________________

---

## FDE post-session notes

To be completed immediately after the session or after reading the async responses.

**Failure modes that are specific to this client (not already in the baseline library):**

> _Notes:_ _______________________________________________

**False-signal patterns worth encoding as detection assertions:**

> _Notes:_ _______________________________________________

**The "fake yes" pattern in the client's specific language (quote if possible):**

> _Notes:_ _______________________________________________

**Proposed `failure_mode_additions/` files to create:**

List the failure mode names and the detection logic stub for each:

```
# Failure mode: [name]
# Source: Client interview, [date]
# Description: [one sentence]
# Detection trigger: [what entity + what condition]
# Test fixture: [one sentence description of the case that triggers it]

# Failure mode: [name]
# Source: ...
```
