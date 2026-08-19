---
name: sb-agents-local
description: Plan reusable read-only browser workflows in the local Super Browser runtime.
---

# Saved-agent planning

This release has no hosted agent registry, HTTP bridge, or live saved-agent service. Use the local `super-browser` MCP server after the Orgo image is built to create auditable read-only run plans.

Do not claim an agent was saved, scheduled, published, or executed without a real provider response and readback. Production writes and approval-required work cannot execute inside this template runtime.
