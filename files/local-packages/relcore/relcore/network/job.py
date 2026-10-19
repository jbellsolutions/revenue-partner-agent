"""Real progress for a mapping run: one bar per source while connecting, one per stage while mapping.

The job file (<run>/job.json) is the spec's progress shape. Writers update it as work happens; the demo page and
Slack read it. Nothing here estimates or animates: `found` and `done` are counts of real work.
"""
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

STAGES = ("merge", "classify", "map", "spots")


class Job:
    def __init__(self, run: Path, sources: list[str]):
        self.path = Path(run) / "job.json"
        self.state = {"id": Path(run).name, "state": "connecting",
                      "sources": [{"source": s, "state": "queued", "found": 0, "total": None, "note": ""} for s in sources],
                      "stages": [{"stage": s, "done": 0, "total": 0} for s in STAGES]}
        self.save()

    def save(self) -> None:
        fd, tmp = tempfile.mkstemp(dir=str(self.path.parent), prefix=".job-")
        with os.fdopen(fd, "w") as f:
            json.dump(self.state, f)
        os.replace(tmp, self.path)

    def source(self, name: str, **kw) -> None:
        for s in self.state["sources"]:
            if s["source"] == name:
                s.update(kw)
        self.save()

    def stage(self, name: str, done: int, total: int) -> None:
        self.state["state"] = "mapping"
        for s in self.state["stages"]:
            if s["stage"] == name:
                s.update(done=done, total=total)
        self.save()

    def finish(self, state: str = "complete") -> None:
        self.state["state"] = state
        self.save()


def read(run: Path) -> dict:
    return json.loads((Path(run) / "job.json").read_text())
