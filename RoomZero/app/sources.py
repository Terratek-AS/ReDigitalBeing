from __future__ import annotations

import json
from pathlib import Path

from app.models import SourceSubmissionModel


class SourceStore:
    def __init__(self, source_queue_file: Path, approved_sources_file: Path) -> None:
        self.source_queue_file = source_queue_file
        self.approved_sources_file = approved_sources_file

    def _read_json_list(self, path: Path) -> list[dict]:
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("[]", encoding="utf-8")
            return []
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(raw, list):
                return raw
            return []
        except Exception:
            return []

    def _write_json_list(self, path: Path, items: list[dict]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(items, indent=2), encoding="utf-8")

    def score_source_reliability(self, url_or_reference: str, title: str = "") -> int:
        text = f"{url_or_reference} {title}".lower()
        if "doi.org" in text or "arxiv.org" in text or "peer-reviewed" in text:
            return 9
        if ".gov" in text or ".edu" in text or "official documentation" in text:
            return 8
        if "university" in text or "research institute" in text:
            return 8
        if "medium.com" in text or "dev.to" in text:
            return 6
        if "blog" in text or "opinion" in text:
            return 4
        return 3

    def submit_source(self, source: SourceSubmissionModel) -> SourceSubmissionModel:
        source.reliability_score = self.score_source_reliability(source.url_or_reference, source.title)
        source.status = "submitted"

        queue = self._read_json_list(self.source_queue_file)
        queue.append(source.model_dump())
        self._write_json_list(self.source_queue_file, queue)
        return source

    def list_source_queue(self, status: str | None = None) -> list[SourceSubmissionModel]:
        queue = [SourceSubmissionModel.model_validate(item) for item in self._read_json_list(self.source_queue_file)]
        if status is None:
            return queue
        return [item for item in queue if item.status == status]

    def approve_source(self, source_id: str, reviewer_notes: str | None = None) -> SourceSubmissionModel:
        queue = self._read_json_list(self.source_queue_file)
        for i, item in enumerate(queue):
            source = SourceSubmissionModel.model_validate(item)
            if source.source_id == source_id:
                source.status = "approved"
                source.reviewer_notes = reviewer_notes
                queue[i] = source.model_dump()
                self._write_json_list(self.source_queue_file, queue)

                approved = self._read_json_list(self.approved_sources_file)
                approved.append(source.model_dump())
                self._write_json_list(self.approved_sources_file, approved)
                return source
        raise ValueError("Source not found.")

    def reject_source(self, source_id: str, reviewer_notes: str | None = None) -> SourceSubmissionModel:
        queue = self._read_json_list(self.source_queue_file)
        for i, item in enumerate(queue):
            source = SourceSubmissionModel.model_validate(item)
            if source.source_id == source_id:
                source.status = "rejected"
                source.reviewer_notes = reviewer_notes
                queue[i] = source.model_dump()
                self._write_json_list(self.source_queue_file, queue)
                return source
        raise ValueError("Source not found.")

    def list_approved_sources(self) -> list[SourceSubmissionModel]:
        return [SourceSubmissionModel.model_validate(item) for item in self._read_json_list(self.approved_sources_file)]
