# Template 03 — Channel Interview

**Mode:** Live call
**Duration:** 45 minutes
**Attendees:** Whoever runs revenue — founder, head of sales, or head of marketing (at least one; ideally whoever owns the outbound motion)

---

## FDE pre-call checklist

- [ ] Template 01 (company overview) received; channel ranking in Section 5 reviewed
- [ ] Template 02 (ICP interview) complete; won-deal channel column reviewed
- [ ] Recording consent confirmed

**FDE note:** Come in knowing which channels the client ranked in Template 01. Use that list as the starting point rather than asking from scratch — it saves 5 minutes and signals that you did your homework.

---

## Agenda (share with attendees beforehand)

| Time | Topic |
|---|---|
| 0–3 min | Framing |
| 3–18 min | What channels actually work today |
| 18–30 min | What a good signal looks like per channel |
| 30–38 min | Channels that have not worked |
| 38–44 min | Warm-prospect definition |
| 44–45 min | LinkedIn deep-dive (if relevant) |

---

## Section 1 — What channels actually work

**FDE prompt:** "We saw in your overview that you ranked [list their channels]. Before we go deeper, I want to hear how you would rank them now — both by deal volume and by deal quality. Volume is how many deals came from that channel. Quality is the average deal size, retention, or ease of close — however you define a 'good' deal for your firm."

**FDE note:** Capture the ranking and any commentary. Ask them to separate volume from quality explicitly — sometimes the highest-volume channel produces the worst clients, and that tension is always useful to surface.

| Channel | Volume rank | Quality rank | Comments |
|---|---|---|---|
| | | | |
| | | | |
| | | | |
| | | | |
| | | | |

**Follow-up — has the channel mix changed in the last 12 months?** "Is the channel mix today meaningfully different from what it was a year ago? What changed and why?"

> _Notes:_ _______________________________________________

---

## Section 2 — What a good signal looks like per channel

Run through each working channel individually. The goal is to understand the *specific observable behavior* that tells the client a prospect is worth pursuing — not the abstract definition of a good lead.

**FDE prompt (per channel):** "For [channel], walk me through what a 'good signal' looks like to you — specifically what someone does or says or publishes that makes you or your team decide to prioritize this person. Not what they are in firmographic terms — what they *do* that catches your attention."

---

**Channel C-1 (fill in channel name): _______________________________________________**

- What does a good inbound signal look like? _______________________________________________
- What does a bad or fake signal look like in this channel? _______________________________________________
- How long after a good signal do you typically reach out? _______________________________________________
- Who on your team owns this channel? _______________________________________________

**Channel C-2: _______________________________________________**

- What does a good inbound signal look like? _______________________________________________
- What does a bad or fake signal look like in this channel? _______________________________________________
- How long after a good signal do you typically reach out? _______________________________________________
- Who on your team owns this channel? _______________________________________________

**Channel C-3: _______________________________________________**

- What does a good inbound signal look like? _______________________________________________
- What does a bad or fake signal look like in this channel? _______________________________________________
- How long after a good signal do you typically reach out? _______________________________________________
- Who on your team owns this channel? _______________________________________________

---

## Section 3 — Channels that have not worked

**FDE prompt:** "Tell me about channels you have tried that did not work. Not channels you have never tried — channels you invested real effort in and abandoned. What did you try, why did you try it, and what specifically made it fail for your business?"

**FDE note:** The failure signal matters as much as the success signal. If cold email never worked for them, that tells us something about their ICP (probably senior buyers who don't respond to cold). If events never worked, that says something different. Capture the specific failure mechanism, not just "we tried it and it didn't work."

---

**Channel that failed — F-1**

- Channel: _______________________________________________
- What did you try specifically? _______________________________________________
- How long / how much did you invest before stopping? _______________________________________________
- What was the failure mechanism? (Not enough replies? Replies but no conversions? Conversions but wrong clients?) _______________________________________________
- In retrospect, why did it fail? _______________________________________________

**Channel that failed — F-2**

- Channel: _______________________________________________
- What did you try specifically? _______________________________________________
- How long / how much did you invest before stopping? _______________________________________________
- What was the failure mechanism? _______________________________________________
- In retrospect, why did it fail? _______________________________________________

**Channel that failed — F-3**

- Channel: _______________________________________________
- What did you try specifically? _______________________________________________
- How long / how much did you invest before stopping? _______________________________________________
- What was the failure mechanism? _______________________________________________
- In retrospect, why did it fail? _______________________________________________

---

## Section 4 — LinkedIn deep-dive

**FDE note:** Run this section only if LinkedIn is a meaningful channel for this client. For AI consulting firms, founder-led LinkedIn thought leadership is often the primary inbound channel — but the signal type is very different from LinkedIn Sales Nav outbound. Make sure to distinguish which mode they use.

**FDE prompt:** "For LinkedIn specifically, I want to understand the mechanics. Do your deals start from founder posts getting engagement, from sponsored content, from Sales Navigator outbound, or from partner referrals that started on LinkedIn?"

> _Answer:_ _______________________________________________

**Follow-up — the mechanism in detail:** "Walk me through the last deal that started on LinkedIn. What specifically happened — what did the prospect do, what did you or your team do in response, and what moved it off LinkedIn and into a real conversation?"

> _Notes:_ _______________________________________________

**Follow-up — engagement patterns:** "When you look at a prospect's LinkedIn profile and activity, what tells you they are likely to be receptive right now — not eventually, but now? Describe a specific profile or post behavior that would make you prioritize an outreach today."

> _Notes:_ _______________________________________________

---

## Section 5 — Warm-prospect definition

**FDE prompt (read verbatim):** "Here is the question we care most about for this section: What does a warm prospect look like to you 30 days before they are ready to buy? Not what they look like when they are ready — what are the early signals that tell you something is starting to move?"

**FDE note:** This is the question that produces the intent-signal modifier overrides. Push past vague answers ("they seem interested") to behavioral specifics ("they commented on my post three times in two weeks" or "their company just posted two AI engineer roles"). Probe with: "What would you literally look for — what would you go look at to confirm this person is warming up?"

> _First answer:_ _______________________________________________

> _Probe — what would you literally look at to confirm?_ _______________________________________________

> _Second signal (if they surface one):_ _______________________________________________

**Follow-up — timing triggers:** "Is there a specific life event or company event that tends to happen 30–90 days before a deal kicks off? Something like a leadership change, a funding round, a product launch, a team hire, a missed quarter?"

> _Notes:_ _______________________________________________

---

## FDE post-call notes

To be completed within 30 minutes of the call.

**Top 2–3 channels by quality (not just volume):**

> _Notes:_ _______________________________________________

**Most specific good-signal descriptions (quote the client if possible):**

> _Notes:_ _______________________________________________

**Intent signals worth adding to the schema (things they look for that are not in the baseline):**

> _Notes:_ _______________________________________________

**Proposed `channel_overrides.yaml` edits (rough draft):**

```yaml
# Draft — review and edit before running generate
signal_weights:
  S_HIRING_TRIGGER: null      # fill in: 0.0–1.0
  S_TECH_ADOPTION: null
  S_FUNDING_TRIGGER: null
  S_PAIN_POINT_MENTION: null
  rationale: ""

custom_signals:
  - name: S_CUSTOM_SIGNAL_NAME   # rename appropriately
    definition: ""
    rationale: ""
    add_to_schema: true
```
