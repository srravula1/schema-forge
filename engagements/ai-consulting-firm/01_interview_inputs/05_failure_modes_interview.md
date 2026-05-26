# Template 05 — Failure Modes Interview
# FILLED — AI Consulting Firm Engagement, 2026-05-25
# Completed async by head of sales, reviewed and expanded in a 20-minute follow-up call.

**Mode:** Async (written) + short live follow-up
**Duration:** 20 minutes async + 20 minutes live review
**Attendees:** Head of Sales (primary), Founder (follow-up review)

---

## Section 1 — Prospects who looked great but were not

**False positive FP-1**

- Prospect descriptor: Series B enterprise SaaS (HR workflow), 180 employees, Atlanta
- What made them look like a great fit? Right size, right industry (SaaS with technical team), CTO engaged and knowledgeable, referenced a specific AI use case (automating workflow classification). Had budget language ("$100k approved for AI tooling this year").
- What was the false signal? They had budget approved but the budget was for a different project — headcount tooling. The AI project was a "nice to have" the CTO wanted to do after the headcount tool shipped. We interpreted "budget approved for AI tooling" as "budget approved for us" when it was actually "we spend money on tooling generally."
- At what point in your process did the truth become clear? After 3 discovery calls and a proposal. The SVP of Engineering went silent, then came back 3 weeks later saying "we're not moving forward at this time."
- What was the cost? 12 hours of sales time across 3 calls + proposal writing. Opportunity cost: we were slower to pursue other leads during this period.
- If you saw the same pattern again, what would you check earlier? Ask directly: "Is this project in the current quarter's budget, or is it in the plan for a future quarter?" The distinction matters. Also: "Can you send us the approved project brief or scope?" If they don't have one, the project isn't real yet.

**False positive FP-2**

- Prospect descriptor: Seed-stage AI startup (document processing), 12 employees, San Francisco (this became regret R-1 — but it looked like a great fit pre-sale)
- What made them look like a great fit? Founder was technically sophisticated, knew the problem precisely ("our RAG system has a citation accuracy problem"), had funding, described a clear use case.
- What was the false signal? They said "we have all our documents in S3" — which we interpreted as "the data is ready." It wasn't. S3 is just storage; the data was unstructured, untagged, and incomplete. We confused "has data" with "has usable data."
- At what point did the truth become clear? Week 3 of a 6-week engagement, when we got access to S3 and found 40k PDFs with no metadata, inconsistent naming conventions, and no ground truth.
- What was the cost? 4 weeks of additional data preparation work, a late delivery, an unhappy client, and a tarnished reference.
- What would you check earlier? Require a sample of 50 representative documents during scoping. "Here's a sample that represents what we'll work with" is the correct answer. "We'll get you access when we start" is a disqualification signal.

**False positive FP-3**

- Prospect descriptor: VC-backed competitor (AI governance advisory), 25 employees
- What made them look like a great fit? CEO was enthusiastic, deal size was attractive ($90k), use case was in our exact wheelhouse (LLM eval for client-facing AI systems).
- What was the false signal? The CEO was a buyer; the team was not. The CEO overrode internal skepticism to work with us. We interpreted CEO enthusiasm as organizational alignment. It wasn't.
- At what point did the truth become clear? Week 2 of the engagement, when every deliverable got contested by the senior ML engineer who had wanted to build it internally.
- What was the cost? 6 weeks of difficult engagement, a politically fraught delivery, a bad reference, and a founder relationship that ended awkwardly.
- What would you check earlier? Require a meeting with the skeptical internal stakeholder before signing. If the champion mentions "the team has mixed feelings" at any point, that phrase must trigger a follow-up: "Can we meet the team before we propose?" If the answer is no, don't sign.

---

## Section 2 — Prospects you nearly missed

**False negative FN-1**

- Client descriptor: Bootstrapped HR tech advisory firm (Chicago, 40 employees) — became Deal W-3
- What made you initially hesitant? Bootstrapped, 40 employees — smaller than our typical footprint. No VC backing, so the "funding stage as budget proxy" heuristic flagged them as low priority.
- What changed your mind? They were a newsletter subscriber who sent a very specific, project-ready email: "We have 8 years of client deliverables in Notion and Google Drive. We want our team to query them naturally. We've budgeted $60–80k for this project this quarter." That email was a higher-quality signal than most Series B inbounds.
- What was the signal you almost missed? Profitability and operational specificity. A bootstrapped company with cash and a specific project is often a better client than a VC-backed company that's spending because it has budget. The financial discipline of a bootstrapped company often translates to better project management.
- What would you tell a junior rep to look for? Don't disqualify on funding stage alone. Look for evidence of project readiness and available budget. "We've budgeted X for this project this quarter" beats "we have VC money and want to do something with AI."

**False negative FN-2**

- Client descriptor: PE-backed insurance vertical SaaS company (claims workflow), 95 employees
- What made you initially hesitant? Insurance vertical — we hadn't worked in insurance before and were uncertain about the regulatory complexity. Initial outreach came through a generic "partner intro" rather than a specific referral.
- What changed your mind? The VP of Engineering's email described a very specific, solvable problem: "we're using an LLM to classify claims documents and getting 25% misclassification on edge cases. We need someone who knows how to build evaluation infrastructure to identify which edge cases are systematic vs. random." That is exactly the problem we solve.
- What was the signal you almost missed? Industry-specific framing that masked a universal AI engineering problem. The problem wasn't "insurance AI" — it was "LLM evaluation," which is our core competency. We almost filtered on industry rather than problem type.
- What would you tell a junior rep? Filter on problem type, not industry. If the problem is "LLM evaluation," "RAG system underperforming," or "AI outputs are unreliable," that's our problem to solve regardless of vertical.

**False negative FN-3**

- Client descriptor: Bootstrapped legal research tools company (20 employees), New York
- What made you initially hesitant? Very small (20 employees), no VC backing, relatively small deal size projection.
- What changed your mind? They could articulate exactly what success looked like, had a sample corpus ready, and had a named internal owner before the first call. Perfect project readiness despite small size.
- What was the signal you almost missed? Team competence as a proxy for project success. A small, competent technical team can execute a well-scoped project better than a large, disorganized one. The scoping call was the fastest we've done — they answered every question precisely.
- What would you tell a junior rep? Prioritize project readiness signals over company size. A 20-person company with a named owner, a clean data sample, and a clear success criterion will be a better engagement than a 100-person company that can't answer basic scoping questions.

---

## Section 3 — The "fake yes"

> _What a fake yes does (that a real buyer also does):_ Engages enthusiastically with content, asks smart questions on LinkedIn posts and in calls, books calls readily, seems knowledgeable about AI, expresses strong interest in working together, says things like "this is exactly what we need" and "I want to move forward on this."

> _What a fake yes never does (that a real buyer always does):_ Never introduces us to other internal stakeholders (a real buyer always loops in the CTO, the relevant engineer, or the CFO at some point). Never provides a sample of their data when asked ("we'll sort that out when we start"). Never gives a specific timeline with accountability ("we're targeting Q3" is vague; "we need this shipped by September 15 because our board review is on the 20th" is specific). Never answers the question "what does success look like at the end of this engagement?" with specifics — fake yeses always give outcomes like "we want to see what AI can do for us" or "we want to be more AI-enabled."

> _At what point in your process do you typically realize it is a fake yes?_ Usually at the second or third call, when we start asking scoping questions (sample data, internal owner, success criteria). A real buyer has answers or can get them quickly. A fake yes deflects or says "we'll figure that out as we go."

> _Is there an earlier signal you can now identify in retrospect?_ Yes: they never respond to direct questions with direct answers. "Who would own this internally?" gets "it would probably be a shared responsibility." "What does the data situation look like?" gets "we have lots of data, we'd have to figure out what's most useful." Real buyers have thought about these things; fake yeses haven't because they're interested in the idea, not the project.

---

## Section 4 — What not to do

> 1. **Do not count LinkedIn engagement as a buying signal.** A prospect who likes 10 posts and comments "great insights!" is showing you they follow you, not that they're buying. The signal worth tracking is content-specific comments that reveal a specific problem ("we're struggling with exactly this in our RAG setup") or a direct DM with a business context. Enthusiasm without specificity is noise.

> 2. **Do not start a discovery call without knowing the prospect's employee count and funding stage.** These two data points can be researched in 5 minutes. Walking into a discovery call with someone who turns out to be a 4-person seed-stage startup is a waste of everyone's time. Filter first.

> 3. **Do not accept "we'll get you data access when we start" as a satisfactory answer to a data question.** If they can't show you 50 representative documents during scoping, you cannot scope the project accurately. Data unavailability during scoping predicts data problems during execution. Require a data sample before you write a proposal.

> 4. **Do not mistake enthusiasm for project readiness.** Some prospects are genuinely excited about AI but have no project, no owner, no data, and no budget allocated to a specific initiative. They want the education and the thought partnership, not the engagement. The tell: they can't answer "what does success look like in 90 days?" with a specific, measurable answer. Push for specificity; the enthusiastic non-buyers will deflect.

> 5. **Do not close a deal if the internal champion mentions team skepticism without resolving it.** "Some of my team has mixed feelings about working with external consultants" is not an acceptable open item to carry into a signed engagement. Require a conversation with the skeptics before the contract. If the champion won't facilitate that conversation, the deal will be politically difficult regardless of how good the work is.

---

## FDE post-session notes

**Failure modes that are specific to this client (not already in the baseline library):**

> 1. **AI tire-kicker / fake yes** — prospect engaged enthusiastically in LinkedIn content, says all the right things, but has no specific project, no named owner, no data sample, and can't articulate success criteria. Distinguished from a real buyer by specificity of answers to scoping questions.
> 2. **Budget language misinterpretation** — prospect uses budget language ("$100k approved for AI tooling") that sounds like it applies to the specific project but is actually general budget language. Check: "Is this project specifically budgeted for Q[current]?" not "is there general AI budget?"
> 3. **Champion-without-team-alignment** — the champion is bought in but the team is skeptical. Champion override creates politically difficult engagements. Detection: team members who weren't introduced before contract signing.

**False-signal patterns worth encoding as detection assertions:**

> 1. High LinkedIn engagement + no specific problem statement = fake yes candidate
> 2. Budget language without specific project + no timeline = budget may not be allocated to this
> 3. No sample data provided during scoping + "we'll figure it out when we start" = data readiness failure mode
> 4. "Mixed feelings" team signal with no follow-up meeting = team alignment failure mode

**The "fake yes" pattern in the client's specific language (quote if possible):**

> "Half my discovery calls last quarter were people who wanted free AI education, not buyers." (Founder, channel interview follow-up)
> "The word 'explore' is a red flag. Real buyers say 'we have X problem and we need to solve it by Y date.' The explorers say 'I want to see what's possible.'" (Founder, ICP interview)

**Proposed `failure_mode_additions/` files to create:**

```
# Failure mode: fake_yes_ai_curiosity
# Source: Failure-modes interview, AI consulting client, 2026-05-25
# Description: Prospect engages enthusiastically with AI content and says right things in discovery,
#              but has no specific project, no named internal owner, no data sample, no timeline.
# Detection trigger: Q_NEED_ARTICULATED entity present + Q_BUDGET_CONFIRMED absent + Q_TIMELINE_STATED absent
#                    + engagement history shows multiple S_PAIN_POINT_MENTION but no budget/authority evidence
# Test fixture: Discovery call transcript with 5+ pain mentions, no budget confirmed, no timeline, no named owner
```
