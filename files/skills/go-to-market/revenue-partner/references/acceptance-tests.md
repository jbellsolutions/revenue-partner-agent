# Revenue Partner Acceptance Tests

## Fit and mapping

- [ ] A business without a paid/validated offer returns `not_fit`.
- [ ] A business with a fixable readiness gap returns `conditional_fit` plus prerequisites.
- [ ] A fit result cites evidence and unknowns.
- [ ] The Money Desk map separates owned demand from new demand.
- [ ] Permanent single-channel cherry-picking is not represented as the full Revenue Partner model.

## Story and claims

- [ ] One canonical positioning/approved-claims artifact exists.
- [ ] Every channel draft derives from that artifact.
- [ ] Self-reported claims are labeled.
- [ ] The 2–4 booked-meetings/day figure is always paired with the explicit non-guarantee.
- [ ] No missing price, commission, attribution window, SLA, contract term, case study, or result is invented.

## Super Browser research

- [ ] Five-round council completed before execution.
- [ ] At least three viable lanes compared when available.
- [ ] Provider readiness and cost are verified.
- [ ] Source URLs, retrieval status, provenance, and failures are preserved.
- [ ] Deduplication criteria, coverage, exact count, and missing fields are reported.
- [ ] An unspecified production list targets at least 5,000 verified unique records when sources/budget allow.
- [ ] A pilot is labeled and not silently presented as the final deliverable.

## Campaign approval

- [ ] Campaign contract records audience, exclusions, source, sender, claims, variants, volume, schedule, budget, geography, suppression, metrics, pause/stop rules, CRM mapping, and approval.
- [ ] Read-only research/drafts can run without send authority.
- [ ] Approval records are audit evidence only and cannot activate external actions in this image.
- [ ] A scope deviation stops; it cannot be resumed by adding an approval record.
- [ ] New spend, commitments, permissions, destructive writes, and sensitive disclosure remain non-executable; future activation requires a separately reviewed integration and rebuilt release.

## Channel behavior

- [ ] Reactivation dedupes and checks suppression/consent before local drafts; execution is unavailable in this image.
- [ ] Outbound drafts are targeted/personal and pass deliverability/capacity gates; sending remains unavailable.
- [ ] Affiliate work includes recruit, onboard, enable, manage, and track—not only a signup page.
- [ ] Riley records sources and explainable audience-fit/reachability scores.
- [ ] Riley drafts but does not own relationships, negotiation, or closing.
- [ ] Content preserves the shared story across channels.

## Metrics and reporting

- [ ] Booked, attended, qualified, opportunity, pipeline, and closed revenue are separate fields.
- [ ] One weekly report issues `continue`, `modify`, or `stop` decisions.
- [ ] Activity metrics are secondary to outcomes.
- [ ] Attribution confidence is explicit.

## Failure and observability

- [ ] Tool actions, specialist identity, approvals, errors, and outcomes are traceable.
- [ ] Simulated connector/auth failure stops the affected workflow and alerts the operator.
- [ ] One specialist failure does not stop unrelated workflows.
- [ ] No external write is claimed; a future integration must require a durable ID and read-back evidence.

## Template smoke

- [ ] Clean instance reaches running.
- [ ] Hermes CLI exists.
- [ ] Revenue Partner skill and knowledge vault exist.
- [ ] Super Browser lists eight providers.
- [ ] Local Playwright runtime passes readiness.
- [ ] Super Browser MCP starts and Hermes can enumerate/test it.
- [ ] Existing observability and bridge tests pass.
- [ ] No secret value is present in the golden image or repo.
- [ ] Model-backed chat is tested only after legitimate model authentication; personal OAuth is not copied into the image.
