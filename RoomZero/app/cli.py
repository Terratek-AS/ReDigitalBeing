from __future__ import annotations

import sys

from app.config import (
    APPROVED_SOURCES_FILE,
    CONVERSATIONS_FILE,
    EPISODIC_FILE,
    INVITES_FILE,
    KNOWLEDGE_BASE_FILE,
    PERSONA_FILE,
    PROCEDURAL_FILE,
    RESEARCH_JOBS_FILE,
    RESEARCH_QUESTIONS_FILE,
    SEMANTIC_FILE,
    SESSION_FEEDBACK_FILE,
    SOURCE_QUEUE_FILE,
    STATE_FILE,
    TESTERS_FILE,
    ensure_data_dirs,
    load_settings,
)
from app.llm import build_context, generate_reply
from app.feedback import FeedbackStore
from app.logger import ConversationLogger
from app.memory import MemoryStore
from app.models import ConversationLogItem, MemoryItem, ResearchJobModel, ResearchQuestionModel
from app.persona import PersonaStore
from app.research import ResearchStore
from app.research_jobs import ResearchJobsStore
from app.safety import evaluate_message, safe_refusal_message
from app.sources import SourceStore
from app.state import StateStore
from app.testers import TesterStore


def run_cli() -> None:
    settings = load_settings()
    ensure_data_dirs()

    persona_store = PersonaStore(PERSONA_FILE)
    state_store = StateStore(STATE_FILE)
    memory_store = MemoryStore(EPISODIC_FILE, SEMANTIC_FILE, PROCEDURAL_FILE)
    logger = ConversationLogger(CONVERSATIONS_FILE)
    tester_store = TesterStore(INVITES_FILE, TESTERS_FILE)
    research_store = ResearchStore(RESEARCH_QUESTIONS_FILE, KNOWLEDGE_BASE_FILE, RESEARCH_JOBS_FILE)
    feedback_store = FeedbackStore(SESSION_FEEDBACK_FILE)
    source_store = SourceStore(SOURCE_QUEUE_FILE, APPROVED_SOURCES_FILE)
    research_jobs_store = ResearchJobsStore(RESEARCH_JOBS_FILE, RESEARCH_QUESTIONS_FILE)

    persona = persona_store.load()
    print(f"RoomZero CLI started. You are now chatting with {persona.name}.")
    print("Type 'exit' to quit.\n")

    while True:
        try:
            user_message = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting RoomZero CLI.")
            break

        if not user_message:
            continue

        if user_message.lower() in {"exit", "quit"}:
            print("Session ended.")
            break

        if user_message.startswith("/invite "):
            role = user_message.split(" ", 1)[1].strip()
            invite = tester_store.create_invite_code(role=role)  # type: ignore[arg-type]
            print(f"[invite] role={invite.role} code={invite.invite_code}")
            continue

        if user_message == "/research":
            items = research_store.list_research_questions()[-10:]
            print(f"[research] recent={len(items)}")
            for item in items:
                print(f"- {item.question_id} [{item.status}] {item.question}")
            continue

        if user_message.startswith("/askresearch "):
            q = user_message.split(" ", 1)[1].strip()
            item = research_store.submit_research_question(
                ResearchQuestionModel(
                    question=q,
                    category="other",
                    submitted_by="admin_cli",
                    priority=5,
                    tags=["admin"],
                    linked_sources=[],
                )
            )
            print(f"[research] submitted question_id={item.question_id}")
            continue

        if user_message == "/knowledge":
            items = research_store.get_recent_knowledge(limit=10)
            print(f"[knowledge] recent={len(items)}")
            for item in items:
                print(f"- {item.knowledge_id} [{item.category}] {item.summary}")
            continue

        if user_message == "/feedback":
            stats = feedback_store.get_feedback_stats()
            print(f"[feedback] {stats}")
            continue

        if user_message == "/sources":
            queue = source_store.list_source_queue()
            print(f"[sources] queue_count={len(queue)}")
            for item in queue[:10]:
                print(f"- {item.source_id} [{item.status}] {item.title}")
            continue

        if user_message.startswith("/job "):
            topic = user_message.split(" ", 1)[1].strip()
            job = research_jobs_store.create_research_job(
                job=ResearchJobModel(
                    name=f"Manual Research Job: {topic}",
                    topic=topic,
                    category="other",
                    query=topic,
                    schedule="manual",
                    created_by="admin_cli",
                    notes="Created via CLI /job command.",
                )
            )
            print(f"[jobs] created job_id={job.job_id} topic={job.topic}")
            continue

        if user_message == "/jobs":
            jobs = research_jobs_store.list_research_jobs()
            print(f"[jobs] count={len(jobs)}")
            for item in jobs[-20:]:
                print(f"- {item.job_id} [{item.status}] topic={item.topic} last_run={item.last_run}")
            continue

        if user_message.startswith("/runjob "):
            job_id = user_message.split(" ", 1)[1].strip()
            try:
                result = research_jobs_store.run_manual_research_job(job_id)
                print(f"[jobs] ran job_id={job_id} generated={len(result['created_questions'])} placeholder tasks")
            except ValueError as exc:
                print(f"[jobs] error: {exc}")
            continue

        if user_message.startswith("/approvequestion "):
            qid = user_message.split(" ", 1)[1].strip()
            try:
                item = research_store.approve_research_question(
                    question_id=qid,
                    reviewer_notes="Approved via CLI",
                    approved_summary="Approved via CLI summary",
                    approved_by="admin_cli",
                )
                print(f"[research] approved question_id={item.question_id}")
            except ValueError as exc:
                print(f"[research] error: {exc}")
            continue

        if user_message.startswith("/rejectquestion "):
            qid = user_message.split(" ", 1)[1].strip()
            try:
                item = research_store.reject_research_question(
                    question_id=qid,
                    reviewer_notes="Rejected via CLI",
                )
                print(f"[research] rejected question_id={item.question_id}")
            except ValueError as exc:
                print(f"[research] error: {exc}")
            continue

        safety = evaluate_message(user_message)
        state = state_store.load()

        if not safety.allowed:
            reply = safe_refusal_message()
            print(f"{persona.name}: {reply}")
            logger.add(
                ConversationLogItem(
                    user_message=user_message,
                    assistant_message=reply,
                    mode="local_fallback",
                    safety_flagged=True,
                )
            )
            continue

        recent_memories = memory_store.get_recent(limit=settings.max_recent_memories)
        context = build_context(persona, state, recent_memories)

        reply, mode = generate_reply(
            user_message=user_message,
            context=context,
            openai_api_key=settings.openai_api_key,
            openai_model=settings.openai_model,
            persona=persona,
            state=state,
            memories=recent_memories,
        )

        updated_state = state_store.update_after_interaction(state, user_message)

        if "remember" in user_message.lower():
            if safety.requires_memory_consent:
                reply += (
                    "\n(Notice: Potentially sensitive content detected. "
                    "Please confirm explicit consent before storing.)"
                )
            else:
                memory_store.add_memory(
                    MemoryItem(
                        category="episodic",
                        content=user_message,
                        importance=0.65,
                        tags=["user_requested_memory"],
                        source="user",
                    )
                )

        logger.add(
            ConversationLogItem(
                user_message=user_message,
                assistant_message=reply,
                mode=mode,
                safety_flagged=False,
            )
        )

        print(f"{persona.name}: {reply}")
        print(
            f"[state] calm={updated_state.calm:.2f} curiosity={updated_state.curiosity:.2f} "
            f"focus={updated_state.focus:.2f} empathy={updated_state.empathy:.2f} "
            f"caution={updated_state.caution:.2f}"
        )


if __name__ == "__main__":
    try:
        run_cli()
    except Exception as exc:
        print(f"Fatal CLI error: {exc}", file=sys.stderr)
        raise
