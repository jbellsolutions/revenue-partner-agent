# Revenue Partner Campaign Contract

This image cannot execute an external campaign. A completed contract and human approval are audit evidence for a future separately reviewed integration; they do not create send, publish, write, spend, schedule, authenticated-profile, or production authority here.

## Contract Header

```yaml
campaign_id:
name:
owner:
created_at:
approved_at:
approved_by:
status: draft | approved | paused | stopped | completed
channel:
sender_identity:
geography:
budget_limit:
start_condition:
end_condition:
```

## Audience and exclusions

- ICP/account criteria:
- Contact/relationship criteria:
- Included segments:
- Excluded segments:
- Jurisdiction restrictions:
- Existing-customer/account-owner conflicts:

## Source and evidence

- Data source(s):
- Retrieval date:
- Provenance fields:
- Verification method:
- Deduplication key:
- Coverage and exact count:
- Missing/unknown fields:

## Approved claims

- Canonical positioning:
- Approved proof:
- Self-reported claims and required labels:
- Target language and non-guarantees:
- Prohibited claims:

## Message and channel bounds

- Approved variants:
- Personalization inputs:
- Sender identity:
- Daily/weekly volume:
- Schedule and timezone:
- Follow-up count/cadence:
- Landing/booking destination:

## Suppression and consent

- Suppression source:
- Opt-out handling:
- Complaint handling:
- Consent/lawful-basis notes:
- Bounce/invalid-recipient policy:
- Data retention/deletion rule:

## CRM and attribution

- Source of truth:
- Allowed fields/stages:
- Attribution window:
- Existing vs created opportunity rule:
- Booked/attended/qualified/opportunity/revenue definitions:
- Read-back verification method:

## Success thresholds

- Minimum evidence to continue:
- Scale threshold:
- Capacity constraint:
- Review cadence:

## Pause rules

Pause immediately on:

- Unknown or conflicting consent/suppression status.
- Authentication, sender, domain, or integration changes.
- Volume or geography outside the approved contract.
- Bounce/complaint thresholds reached.
- Reputation, legal, privacy, or platform-policy risk.
- Missing source provenance or a verification regression.
- Operator capacity exceeded.

## Stop rules

Stop when:

- The approved end condition is reached.
- Evidence rejects the hypothesis.
- The offer/positioning materially changes.
- The operator revokes approval.
- A serious complaint, policy, privacy, or security event occurs.
- Results fail the pre-agreed stopping rule.

## Fresh approval required

Fresh approval is mandatory for:

- New audience, geography, channel, sender, message claim, or major variant.
- Volume, schedule, budget, or follow-up increases outside bounds.
- Pricing, discount, contract, affiliate, sponsorship, or other commitments.
- New account/integration/permission.
- Destructive or bulk CRM updates.
- Paid placement, purchase, or budget increase.
- Sensitive-data disclosure.

## Execution hard stop

After the operator approves this contract, the agent may continue only policy-eligible read-only research and local drafting. Approval cannot activate send/publish/write authority in this image. Any future execution requires a separately reviewed external integration and rebuilt release; ambiguity resolves to stop and escalate.

## Approval Record

```text
Decision: approve | revise | reject
Approver:
Timestamp:
Approved scope:
Explicit exclusions:
Evidence/artifact link:
```
