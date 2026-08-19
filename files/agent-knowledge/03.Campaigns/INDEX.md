# Campaigns Index

## Purpose

Contains draft, approved, paused, completed, and stopped campaign contracts plus source/suppression evidence.

## Folder Convention

```text
03.Campaigns/
  INDEX.md
  YYYY-MM-DD-<campaign-id>/
    contract.md
    sources.csv
    suppression.csv
    decisions.md
    results.md
```

## Rules

- Contracts and approvals are audit evidence only; no external action can execute in this image.
- Preserve approval identity/timestamp and exact bounds.
- Record provenance, deduplication, coverage, exact counts, and failures.
- Pause on deviations; do not silently expand scope.
- Archive completed/stopped campaigns without deleting their evidence.
