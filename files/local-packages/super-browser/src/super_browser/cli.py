from __future__ import annotations

import argparse
import json
import sys

from .bundle import build_bundle_manifest, write_bundle_manifest
from .env_checklist import environment_checklist

from .models import RUN_STATUS_VALUES
from .profiles import ProfileStore
from .production import production_readiness
from .providers import PROVIDERS, list_providers, provider_readiness
from .redaction import redact_text, safe_json_dumps
from .router import build_plan, infer_task
from .runtime import create_run, deny_run, resume_run
from .setup_walkthrough import launch_setup
from .store import RunStore
from .handoff import build_handoff
from .live_tests import WORKFLOW_CLASSES, run_live_tests
from .verifier import verify_run



def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="super-browser", description="Plan and route browser/computer automation tasks.")
    sub = parser.add_subparsers(dest="command", required=True)

    plan_p = sub.add_parser("plan", help="Plan a browser automation task.")
    plan_p.add_argument("--goal", required=True)
    plan_p.add_argument("--url")
    plan_p.add_argument("--optimize", choices=["balanced", "cost", "reliability"], default="balanced")
    plan_p.add_argument("--allow-provider", action="append", choices=list(PROVIDERS.keys()), default=[])
    plan_p.add_argument("--max-cost-usd", type=float)
    plan_p.add_argument("--timeout-seconds", type=_positive_int)
    plan_p.add_argument("--profile", help="Named persistent browser profile from ProfileStore.")

    plan_p.add_argument(
        "--deliberation-rounds",
        type=_deliberation_rounds,
        help="Planner deliberation loops (3-5). Default: 3 direct, 5 council.",
    )

    run_p = sub.add_parser("run", help="Create and execute a durable browser automation run when policy allows.")
    run_p.add_argument("--goal", required=True)
    run_p.add_argument("--url")
    run_p.add_argument("--optimize", choices=["balanced", "cost", "reliability"], default="balanced")
    run_p.add_argument("--allow-provider", action="append", choices=list(PROVIDERS.keys()), default=[])
    run_p.add_argument("--max-cost-usd", type=float)
    run_p.add_argument("--timeout-seconds", type=_positive_int)
    run_p.add_argument("--profile", help="Named persistent browser profile from ProfileStore.")


    run_p.add_argument("--plan-only", action="store_true", help="Create the durable run plan without executing the provider.")
    run_p.add_argument(
        "--deliberation-rounds",
        type=_deliberation_rounds,
        help="Planner deliberation loops (3-5). Default: 3 direct, 5 council.",
    )

    profiles_p = sub.add_parser("profiles", help="Read named persistent browser profiles.")
    profiles_sub = profiles_p.add_subparsers(dest="profiles_command", required=True)
    profiles_sub.add_parser("list", help="List saved browser profiles.")
    profiles_get = profiles_sub.add_parser("get", help="Return one browser profile by name.")
    profiles_get.add_argument("name")

    resume_p = sub.add_parser("resume", help="Resume a planned, blocked, or failed read-only run when policy allows.")
    resume_p.add_argument("run_id")

    get_p = sub.add_parser("get", help="Return a saved run by id without executing it.")
    get_p.add_argument("run_id")

    handoff_p = sub.add_parser("handoff", help="Return a compact handoff package for another agent.")
    handoff_p.add_argument("run_id")

    runs_p = sub.add_parser("runs", aliases=["list-runs"], help="List saved runs without executing them.")
    runs_p.add_argument("--status", choices=RUN_STATUS_VALUES)
    runs_p.add_argument("--limit", type=_positive_int, default=20)
    runs_p.add_argument("--details", action="store_true", help="Include full run payloads instead of compact summaries.")

    verify_p = sub.add_parser("verify", help="Verify a run report.")
    verify_p.add_argument("run_id")


    deny_p = sub.add_parser("deny", help="Deny a run that is awaiting approval.")
    deny_p.add_argument("run_id")
    deny_p.add_argument("--by", default="user")
    deny_p.add_argument("--reason", required=True)

    sub.add_parser("providers", help="List known browser/computer providers.")
    sub.add_parser("doctor", help="Check provider environment readiness.")
    prod_p = sub.add_parser("production-readiness", help="Fail unless required providers have production-ready live evidence.")
    prod_p.add_argument("--require-provider", action="append", choices=list(PROVIDERS.keys()), default=[])
    manifest_p = sub.add_parser("bundle-manifest", help="Print or write a hashed Super Browser handoff manifest.")
    manifest_p.add_argument("--root", help="Repository or installed bundle root to inspect.")
    manifest_p.add_argument("--path", help="Write manifest JSON to this path instead of only printing it.")
    sub.add_parser("env-checklist", help="Print required and optional Super Browser environment variables without values.")
    setup_p = sub.add_parser(
        "setup",
        help="Return the baked-runtime verification, credential, doctor, and read-only fixture walkthrough.",
    )
    setup_p.add_argument(
        "--client",
        choices=["cursor", "codex", "claude"],
        help="Optional agent client label for the non-mutating baked-runtime report.",
    )
    live_p = sub.add_parser("live-test", help="Run gated local/provider live tests.")
    live_p.add_argument("--provider", choices=["local", "fixtures", "all", *PROVIDERS.keys()], default="local")
    live_p.add_argument("--workflow-class", choices=list(WORKFLOW_CLASSES), default="default")

    args = parser.parse_args(argv)
    try:
        if args.command == "providers":
            return _print(list_providers())
        if args.command == "doctor":
            return _print({"providers": provider_readiness()})
        if args.command == "production-readiness":
            payload = production_readiness(required_providers=args.require_provider or None)
            _print(payload)
            return 0 if payload["production_ready"] else 1
        if args.command == "bundle-manifest":
            if args.path:
                return _print(write_bundle_manifest(root=args.root, path=args.path))
            return _print(build_bundle_manifest(root=args.root))
        if args.command == "env-checklist":
            return _print(environment_checklist())
        if args.command == "setup":
            return _print(launch_setup(client=args.client))
        if args.command == "live-test":
            payload = run_live_tests(args.provider, workflow_class=args.workflow_class)
            _print(payload)
            return _live_test_exit_code(payload)
        if args.command == "plan":
            task = infer_task(
                args.goal,
                url=args.url,
                optimize=args.optimize,
                providers_allowed=args.allow_provider,
                max_cost_usd=args.max_cost_usd,
                timeout_seconds=args.timeout_seconds,
                profile=args.profile,
            )
            return _print(build_plan(task, deliberation_rounds=args.deliberation_rounds).to_dict())
        if args.command == "profiles":
            store = ProfileStore(create=False)
            if args.profiles_command == "list":
                return _print([item.to_dict() for item in store.list()])
            if args.profiles_command == "get":
                profile = store.get(args.name)
                if not profile:
                    return _error(f"Profile not found: {args.name}")
                return _print(profile.to_dict())

        if args.command == "run":

            run = create_run(
                args.goal,
                url=args.url,
                optimize=args.optimize,
                execute=not args.plan_only,
                providers_allowed=args.allow_provider,
                max_cost_usd=args.max_cost_usd,
                timeout_seconds=args.timeout_seconds,
                profile=args.profile,
                deliberation_rounds=args.deliberation_rounds,
            )
            return _print(run.to_dict())
        if args.command == "resume":
            return _print(resume_run(args.run_id).to_dict())
        if args.command == "get":
            run = RunStore(create=False).get(args.run_id)
            if not run:
                return _error(f"Run not found: {args.run_id}")
            return _print(run)
        if args.command == "handoff":
            return _print(build_handoff(args.run_id))
        if args.command in ("runs", "list-runs"):
            return _print(RunStore(create=False).list(status=args.status, limit=args.limit, include_details=args.details))
        if args.command == "verify":
            return _print(verify_run(args.run_id))

        if args.command == "deny":
            return _print(deny_run(args.run_id, denied_by=args.by, reason=args.reason).to_dict())

        return _error("Unknown command")
    except Exception as exc:
        return _error_from_exception(exc)


def _print(payload: object) -> int:
    print(safe_json_dumps(payload))
    return 0


def _live_test_exit_code(payload: dict[str, object]) -> int:
    """Treat anything short of a completed pass as a failed readiness gate."""
    return 0 if payload.get("status") == "passed" else 1


def _error(message: str, *, error_type: str = "ValueError") -> int:
    print(json.dumps({"error": redact_text(message), "error_type": error_type}), file=sys.stderr)
    return 1


def _error_from_exception(exc: Exception) -> int:
    return _error(str(exc), error_type=exc.__class__.__name__)


def _positive_int(value: str) -> int:
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("must be >= 1")
    return parsed



def _deliberation_rounds(value: str) -> int:
    parsed = int(value)
    if parsed < 3 or parsed > 5:
        raise argparse.ArgumentTypeError("deliberation rounds must be between 3 and 5")
    return parsed


if __name__ == "__main__":
    raise SystemExit(main())
