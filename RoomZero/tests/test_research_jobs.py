from pathlib import Path

from app.models import ResearchJobModel
from app.research_jobs import ResearchJobsStore


def test_create_and_list_jobs(tmp_path: Path) -> None:
    jobs_file = tmp_path / "research_jobs.json"
    questions_file = tmp_path / "questions.json"
    store = ResearchJobsStore(jobs_file, questions_file)

    created = store.create_research_job(
        ResearchJobModel(
            name="Memory job",
            topic="persistent memory in AI agents",
            category="memory_systems",
            query="persistent memory in AI agents",
            schedule="manual",
            created_by="tester",
        )
    )

    listed = store.list_research_jobs()
    assert len(listed) == 1
    assert listed[0].job_id == created.job_id
    assert listed[0].status == "active"


def test_pause_and_activate_job(tmp_path: Path) -> None:
    jobs_file = tmp_path / "research_jobs.json"
    questions_file = tmp_path / "questions.json"
    store = ResearchJobsStore(jobs_file, questions_file)

    job = store.create_research_job(
        ResearchJobModel(
            name="Safety job",
            topic="memory safety",
            category="ethics",
            query="memory safety",
            schedule="manual",
            created_by="tester",
        )
    )

    paused = store.pause_research_job(job.job_id)
    assert paused.status == "paused"

    active = store.activate_research_job(job.job_id)
    assert active.status == "active"


def test_run_manual_job_generates_placeholder_questions(tmp_path: Path) -> None:
    jobs_file = tmp_path / "research_jobs.json"
    questions_file = tmp_path / "questions.json"
    store = ResearchJobsStore(jobs_file, questions_file)

    job = store.create_research_job(
        ResearchJobModel(
            name="Memory architecture job",
            topic="persistent memory in AI agents",
            category="memory_systems",
            query="persistent memory in AI agents",
            schedule="manual",
            created_by="tester",
        )
    )

    result = store.run_manual_research_job(job.job_id)

    assert result["mode"] == "manual_placeholder"
    assert "no external api" in result["note"].lower()
    assert len(result["created_questions"]) >= 5
