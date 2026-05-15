from __future__ import annotations

import json
from pathlib import Path

from app.models import ResearchJobModel, ResearchQuestionModel, utc_now_iso


class ResearchJobsStore:
    def __init__(self, research_jobs_file: Path, research_questions_file: Path) -> None:
        self.research_jobs_file = research_jobs_file
        self.research_questions_file = research_questions_file

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

    def create_research_job(self, job: ResearchJobModel) -> ResearchJobModel:
        jobs = self._read_json_list(self.research_jobs_file)
        jobs.append(job.model_dump())
        self._write_json_list(self.research_jobs_file, jobs)
        return job

    def list_research_jobs(self) -> list[ResearchJobModel]:
        return [ResearchJobModel.model_validate(item) for item in self._read_json_list(self.research_jobs_file)]

    def pause_research_job(self, job_id: str) -> ResearchJobModel:
        jobs = self._read_json_list(self.research_jobs_file)
        for i, item in enumerate(jobs):
            job = ResearchJobModel.model_validate(item)
            if job.job_id == job_id:
                job.status = "paused"
                jobs[i] = job.model_dump()
                self._write_json_list(self.research_jobs_file, jobs)
                return job
        raise ValueError("Research job not found.")

    def activate_research_job(self, job_id: str) -> ResearchJobModel:
        jobs = self._read_json_list(self.research_jobs_file)
        for i, item in enumerate(jobs):
            job = ResearchJobModel.model_validate(item)
            if job.job_id == job_id:
                job.status = "active"
                jobs[i] = job.model_dump()
                self._write_json_list(self.research_jobs_file, jobs)
                return job
        raise ValueError("Research job not found.")

    def update_job_timestamp(self, job_id: str, *, last_run: str | None = None, next_run: str | None = None) -> ResearchJobModel:
        jobs = self._read_json_list(self.research_jobs_file)
        for i, item in enumerate(jobs):
            job = ResearchJobModel.model_validate(item)
            if job.job_id == job_id:
                if last_run is not None:
                    job.last_run = last_run
                if next_run is not None:
                    job.next_run = next_run
                jobs[i] = job.model_dump()
                self._write_json_list(self.research_jobs_file, jobs)
                return job
        raise ValueError("Research job not found.")

    def generate_research_questions_from_topic(self, topic: str, category: str = "other") -> list[ResearchQuestionModel]:
        low = topic.lower()
        if "memory" in low:
            prompts = [
                "What are the best architectures for long-term AI memory?",
                "How can episodic and semantic memory be separated?",
                "How should memory decay be implemented safely?",
                "What are risks of memory poisoning?",
                "What sources should be reviewed?",
            ]
        else:
            prompts = [
                f"What is the current research baseline for {topic}?",
                f"What are leading architectures or methods for {topic}?",
                f"What are known safety/ethics risks in {topic}?",
                f"What benchmark datasets and evaluations are used for {topic}?",
                f"What high-reliability sources should be reviewed for {topic}?",
            ]

        questions: list[ResearchQuestionModel] = []
        for q in prompts:
            questions.append(
                ResearchQuestionModel(
                    question=q,
                    category=category,  # type: ignore[arg-type]
                    submitted_by="research_job_system",
                    status="submitted",
                    priority=5,
                    tags=["research_job_generated", topic],
                    linked_sources=[],
                )
            )
        return questions

    def run_manual_research_job(self, job_id: str) -> dict:
        jobs = self._read_json_list(self.research_jobs_file)
        matched: ResearchJobModel | None = None
        for item in jobs:
            job = ResearchJobModel.model_validate(item)
            if job.job_id == job_id:
                matched = job
                break
        if matched is None:
            raise ValueError("Research job not found.")
        if matched.status != "active":
            raise ValueError("Research job is not active.")

        generated_questions = self.generate_research_questions_from_topic(
            topic=matched.topic,
            category=matched.category,
        )

        existing_questions = self._read_json_list(self.research_questions_file)
        existing_questions.extend([q.model_dump() for q in generated_questions])
        self._write_json_list(self.research_questions_file, existing_questions)

        now = utc_now_iso()
        self.update_job_timestamp(job_id, last_run=now)

        return {
            "job_id": matched.job_id,
            "mode": "manual_placeholder",
            "created_questions": [q.model_dump() for q in generated_questions],
            "note": "Generated structured placeholder research tasks; no external API research executed.",
        }
