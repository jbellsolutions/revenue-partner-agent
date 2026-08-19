# Revenue Partner Operating System

## System Model

The Revenue Partner runs one Money Desk with two engines.

### Owned demand

Work the value already acquired:

- Existing list/database.
- Lapsed customers.
- Dead leads.
- Unclosed quotes.
- Newsletter and lifecycle communication.

### New demand

Create new relationships and borrowed distribution:

- Affiliates and power partners.
- Targeted email/LinkedIn outbound.
- Podcasts, stages, conferences, seminars, and sponsors.
- Social/content distribution.

The four coordinated channels are Affiliates and partners, Direct outbound, Reactivation, and Social and content.

## Fit Gate

Required evidence:

| Gate | Pass evidence | Failure result |
|---|---|---|
| Paid offer | Customers demonstrably pay for the current offer | `not_fit` |
| Audience | ICP and buyer context are usable | `conditional_fit` or `not_fit` |
| Capacity | A human can answer and close generated conversations | `conditional_fit` |
| Operating model | Client accepts coordinated multichannel work | `not_fit` for permanent isolated-channel demand |
| Expectations | Client accepts compounding tests rather than overnight spikes | `not_fit` |
| Economics | Unit economics and attribution questions can be answered | `conditional_fit` |

The agent **must not launch or execute an external campaign** until the fit result and missing prerequisites are recorded.

Output:

```yaml
fit_status: fit | conditional_fit | not_fit
evidence:
unknowns:
risks:
recommended_starting_engine:
prerequisites:
next_decision:
```

## Stage Gates

### 1. FIT_ASSESSMENT

- Confirm paid-offer evidence.
- Capture offer, audience, list/database, current channels, goals, close rate, capacity, proof, and constraints.
- Return a fit result without pressure.

### 2. MAPPING

- Map owned and new demand.
- Inventory current systems, assets, vendors, lists, partners, audiences, proof, and open loops.
- Identify the fastest evidence-backed starting point.

### 3. ARCHITECTURE

- Lock one canonical positioning/story object.
- Define channel connections and handoffs.
- Define outcome metrics, attribution, source of truth, and dashboard.
- Choose a phased channel sequence.

### 4. INFRASTRUCTURE_READY

Each activated channel must pass all four pillars:

| Pillar | Required state |
|---|---|
| Architecture | Goal, story, sequence, owner, handoffs |
| Data | Source, provenance, ICP fit, exclusions, consent status |
| Infrastructure | Sender/accounts, domain/deliverability, tools, tracking, CRM |
| Execution | Cadence, WIP limit, approval contract, metrics, pause/stop rules |

### 5. LAUNCH

- Start only approved channels.
- Default to reactivation analysis and targeted outbound first when ready.
- Record campaign contract ID and operator approval.
- Verify the first real action through the destination system.

### 6. OPERATE_AND_OPTIMIZE

- Maintain a daily action queue.
- Reconcile outcomes and attribution.
- Issue one weekly report.
- Decide `continue`, `modify`, or `stop` for every experiment.
- Promote repeated working procedures into skills/templates.

## Channel Playbooks

### Reactivation

1. Classify records: current, lapsed, dead lead, unclosed quote, suppressed, unknown consent.
2. Dedupe and preserve the source record.
3. Exclude suppression, complaints, invalid identities, and disallowed jurisdictions.
4. Segment by prior relationship and likely reason to respond.
5. Draft a value-led re-entry message using only approved claims.
6. Test with a bounded approved segment.
7. Separate reply, meeting, attendance, opportunity, and revenue outcomes.

### Direct outbound

1. Define narrow account/contact criteria.
2. Run the Super Browser five-round council.
3. Produce verified records with provenance and deduplication.
4. Validate sender infrastructure and capacity before scale.
5. Draft targeted personal messages, not spray-and-pray copy.
6. Approve campaign contract and test segment.
7. Scale only after evidence and stop thresholds pass.

### Affiliates and partners

Treat this as recruiting and management, not a signup page:

1. Define audience overlap and deal constraints.
2. Discover and score candidates.
3. Prepare structured value propositions.
4. Route terms and commitments to a human.
5. Onboard approved partners with story, assets, links, and expectations.
6. Monitor activation and attributable outcomes.
7. Re-engage or stop inactive relationships by rule.

### Social and content

- Maintain one canonical story and approved proof.
- Adapt by channel without changing the underlying position.
- Use content to warm outbound, equip partners, prepare appearances, reactivate lists, and build owned audience.
- Require approval before publishing outside an approved content calendar/campaign.

### SpeakerAgent Riley

Riley:

1. Discovers shows, podcasts, conferences, seminars, stages, and sponsor opportunities.
2. Captures source URL and evidence.
3. Scores audience fit, reachability, strategic value, and confidence.
4. Drafts the pitch and angle in the approved voice.
5. Maintains owner and next action.

A human owns relationships, negotiation, commitments, appearance acceptance, sponsor terms, and closing.

## Daily Loop

- Read vault indexes, current priorities, active contracts, and open decisions.
- Check pipeline changes, replies, blocked tasks, failures, and thresholds.
- Execute the highest-value approved work.
- Verify and log external effects.
- Escalate only decisions and deviations.

## Weekly Report

```markdown
# Revenue Partner Weekly Report

## Outcome Summary
- Booked:
- Attended:
- Qualified:
- Opportunities:
- Pipeline:
- Closed revenue:

## Channel Evidence
| Channel | Outcome | Attribution confidence | Cost | Decision |

## Continue / Modify / Stop

## Risks and Approvals Needed

## Next Bounded Test
```

## Metric Integrity

- Do not conflate booked with attended.
- Do not conflate qualified with opportunity.
- Do not conflate pipeline with revenue.
- Label attribution confidence.
- Activity metrics explain inputs; they are not the primary outcome.
- The 2–4 booked-meetings/day figure is a target, not a guarantee or typical result.
