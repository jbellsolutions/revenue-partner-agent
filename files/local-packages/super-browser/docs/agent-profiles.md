# Operator-provisioned browser profiles

Revenue Partner can inspect named browser-profile metadata that an operator baked into the reviewed image. Profiles are local routing records; they are not hosted sessions, do not prove authenticated provider readiness, and cannot be created, changed, bound, or deleted through the shipped CLI or MCP surface.

## Read-only inspection

```bash
super-browser profiles list
super-browser profiles get research
```

The local stdio MCP server exposes only matching list/get operations. A missing profile requires a separately reviewed image rebuild; agents must not create profile state or edit the profile database in place.

A preferred provider is only a planning hint. `super-browser doctor` must show current readiness for the selected lane, and credentials remain operator-controlled connectivity rather than authorization.

Any profile-backed or otherwise authenticated task requires external operator approval before execution. Because agent-side production approval is disabled in this image, these plans persist as `awaiting_approval` and cannot dispatch to a provider.
