# Local Security Patches

The vendor baseline is pinned by `UPSTREAM_COMMIT`. The Revenue Partner template applies this narrowly scoped, reviewable delta:

## Ad/campaign approval classification

- File: `src/super_browser/policy.py`
- Reason: the upstream keyword-only classifier recognized `launch ad` but missed common article-bearing variants such as `launch an ad campaign` and `create an ad`.
- Change: ad/campaign requests fail closed to the approval flow unless the whole request matches a narrow read-only or bounded public-search form. Clause-level action/object patterns additionally make common activation language explicit; grammar between the action and object is not restricted to a modifier whitelist.
- Draft boundary: internal campaign drafting remains autonomous in Hermes as local text work, but a campaign-draft request sent to Super Browser is approval-gated. No draft-language exception can authorize provider execution.
- Exception integrity: campaign-related local-output requests cannot bypass the protected gate, and campaign-related local-delivery or public-search requests must match a strict whole-request grammar. The protected object family includes `ad`, `advert`, `advertisement`, `advertising`, and `campaign` singular/plural forms.
- Safety effect: matching requests are external writes and create runs in `awaiting_approval`; they cannot execute until the durable approval flow succeeds.
- Regression coverage: `tests/test_revenue_partner_template.py::test_super_browser_ad_campaign_phrases_require_approval`.

This patch does not change provider routing, credentials, network behavior, dependency locks, or the pinned source identity.