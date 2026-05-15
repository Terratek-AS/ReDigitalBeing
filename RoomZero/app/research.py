from __future__ import annotations

import json
from pathlib import Path

from app.models import KnowledgeEntryModel, ResearchQuestionModel, ResearchStatus


class ResearchStore:
    def __init__(self, questions_file: Path, knowledge_base_file: Path, research_jobs_file: Path) -> None:
        self.questions_file = questions_file
        self.knowledge_base_file = knowledge_base_file
        self.research_jobs_file = research_jobs_file

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

    def submit_research_question(self, question: ResearchQuestionModel) -> ResearchQuestionModel:
        questions = self._read_json_list(self.questions_file)
        questions.append(question.model_dump())
        self._write_json_list(self.questions_file, questions)
        return question

    def list_research_questions(self, status: ResearchStatus | None = None) -> list[ResearchQuestionModel]:
        questions = [ResearchQuestionModel.model_validate(item) for item in self._read_json_list(self.questions_file)]
        if status is None:
            return questions
        return [q for q in questions if q.status == status]

    def get_research_question(self, question_id: str) -> ResearchQuestionModel | None:
        for item in self._read_json_list(self.questions_file):
            question = ResearchQuestionModel.model_validate(item)
            if question.question_id == question_id:
                return question
        return None

    def update_research_status(
        self,
        question_id: str,
        status: ResearchStatus,
        reviewer_notes: str | None = None,
    ) -> ResearchQuestionModel:
        questions = self._read_json_list(self.questions_file)
        for i, item in enumerate(questions):
            question = ResearchQuestionModel.model_validate(item)
            if question.question_id == question_id:
                question.status = status
                if reviewer_notes is not None:
                    question.reviewer_notes = reviewer_notes
                questions[i] = question.model_dump()
                self._write_json_list(self.questions_file, questions)
                return question
        raise ValueError("Research question not found.")

    def approve_research_question(
        self,
        question_id: str,
        reviewer_notes: str | None = None,
        approved_summary: str | None = None,
        approved_by: str = "reviewer",
    ) -> ResearchQuestionModel:
        questions = self._read_json_list(self.questions_file)
        for i, item in enumerate(questions):
            question = ResearchQuestionModel.model_validate(item)
            if question.question_id == question_id:
                question.status = "approved"
                question.reviewer_notes = reviewer_notes
                if approved_summary:
                    question.approved_summary = approved_summary
                questions[i] = question.model_dump()
                self._write_json_list(self.questions_file, questions)

                if question.eir_answer and question.approved_summary:
                    self.add_to_knowledge_base(
                        question_id=question.question_id,
                        category=question.category,
                        summary=question.approved_summary,
                        answer=question.eir_answer,
                        approved_by=approved_by,
                        tags=question.tags,
                        linked_sources=question.linked_sources,
                    )
                return question
        raise ValueError("Research question not found.")

    def reject_research_question(self, question_id: str, reviewer_notes: str | None = None) -> ResearchQuestionModel:
        return self.update_research_status(question_id=question_id, status="rejected", reviewer_notes=reviewer_notes)

    def add_research_answer(
        self,
        question_id: str,
        answer: str,
        reviewer_notes: str | None = None,
    ) -> ResearchQuestionModel:
        questions = self._read_json_list(self.questions_file)
        for i, item in enumerate(questions):
            question = ResearchQuestionModel.model_validate(item)
            if question.question_id == question_id:
                question.eir_answer = answer
                question.status = "answered"
                if reviewer_notes:
                    question.reviewer_notes = reviewer_notes
                questions[i] = question.model_dump()
                self._write_json_list(self.questions_file, questions)
                return question
        raise ValueError("Research question not found.")

    def add_to_knowledge_base(
        self,
        question_id: str,
        category: str,
        summary: str,
        answer: str,
        approved_by: str,
        tags: list[str] | None = None,
        linked_sources: list[str] | None = None,
    ) -> KnowledgeEntryModel:
        entry = KnowledgeEntryModel(
            question_id=question_id,
            category=category,  # type: ignore[arg-type]
            summary=summary,
            answer=answer,
            approved_by=approved_by,
            tags=tags or [],
            linked_sources=linked_sources or [],
        )
        entries = self._read_json_list(self.knowledge_base_file)
        entries.append(entry.model_dump())
        self._write_json_list(self.knowledge_base_file, entries)
        return entry

    def search_knowledge_base(self, query: str) -> list[KnowledgeEntryModel]:
        q = query.lower().strip()
        entries = [KnowledgeEntryModel.model_validate(item) for item in self._read_json_list(self.knowledge_base_file)]
        if not q:
            return entries
        result: list[KnowledgeEntryModel] = []
        for entry in entries:
            haystack = " ".join(
                [
                    entry.summary.lower(),
                    entry.answer.lower(),
                    " ".join(t.lower() for t in entry.tags),
                    entry.category.lower(),
                ]
            )
            if q in haystack:
                result.append(entry)
        return result

    def get_recent_knowledge(self, limit: int = 20) -> list[KnowledgeEntryModel]:
        entries = [KnowledgeEntryModel.model_validate(item) for item in self._read_json_list(self.knowledge_base_file)]
        entries.sort(key=lambda e: e.approved_at, reverse=True)
        return entries[:limit]
