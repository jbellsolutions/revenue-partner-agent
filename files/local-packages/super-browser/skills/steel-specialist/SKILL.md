---
name: steel-specialist
description: "Planning reference for Steel; non-executable in this image."
---

# Steel planning reference

Steel is represented for capability and cost comparison only. This locked image cannot enforce the target DNS answer, redirects, or connected peer address inside a Steel-hosted Chromium session, so Steel execution is blocked before provider construction even when credentials or a CDP URL exist.

Do not create sessions, connect CDP, navigate, or run live tests through this image. Public Playwright navigation is also non-executable. The only public read lane is bounded direct raw HTTP for eligible public IPv4-literal targets; otherwise stop and report the enforcement blocker.
