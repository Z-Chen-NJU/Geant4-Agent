from __future__ import annotations

import threading
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Callable


ProgressCallback = Callable[[str, str, str | None], None]


@dataclass
class AsyncJob:
    job_id: str
    kind: str
    status: str = "queued"
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    progress: list[dict[str, Any]] = field(default_factory=list)
    result: dict[str, Any] | None = None
    error: str | None = None

    def snapshot(self) -> dict[str, Any]:
        return {
            "job_id": self.job_id,
            "kind": self.kind,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "progress": list(self.progress),
            "result": self.result,
            "error": self.error,
        }


_JOBS: dict[str, AsyncJob] = {}
_LOCK = threading.Lock()


def _append_progress(job: AsyncJob, stage: str, label: str, detail: str | None = None) -> None:
    with _LOCK:
        job.progress.append(
            {
                "ts": time.time(),
                "stage": stage,
                "label": label,
                "detail": detail or "",
            }
        )
        job.updated_at = time.time()


def create_step_job(payload: dict[str, Any], step_fn: Callable[..., dict[str, Any]]) -> dict[str, Any]:
    job = AsyncJob(job_id=str(uuid.uuid4()), kind="step")
    with _LOCK:
        _JOBS[job.job_id] = job

    def progress_cb(stage: str, label: str, detail: str | None = None) -> None:
        _append_progress(job, stage, label, detail)

    def run() -> None:
        with _LOCK:
            job.status = "running"
            job.updated_at = time.time()
        _append_progress(job, "queued", "Queued", "Waiting to start orchestration.")
        try:
            result = step_fn(payload, progress_cb=progress_cb)
            with _LOCK:
                job.status = "completed"
                job.result = result
                job.updated_at = time.time()
            _append_progress(job, "completed", "Completed", "Response is ready.")
        except Exception as exc:
            with _LOCK:
                job.status = "failed"
                job.error = str(exc)
                job.updated_at = time.time()
            _append_progress(job, "failed", "Failed", str(exc))

    thread = threading.Thread(target=run, name=f"step-job-{job.job_id[:8]}", daemon=True)
    thread.start()
    return {"job_id": job.job_id, "status": job.status}


def get_job(job_id: str) -> dict[str, Any] | None:
    with _LOCK:
        job = _JOBS.get(job_id)
        return None if job is None else job.snapshot()
