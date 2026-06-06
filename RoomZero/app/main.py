from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import json
import os
import sys
import threading
import time
import webbrowser
from uuid import uuid4

import uvicorn
from fastapi import FastAPI, Header, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

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
from app.models import (
    ChatRequest,
    ChatResponse,
    ConversationLogItem,
    HealthResponse,
    MemoryCreateRequest,
    MemoryItem,
    ResearchAnswerRequest,
    ResearchJobCreateRequest,
    ResearchJobModel,
    ResearchReviewRequest,
    SessionFeedbackModel,
    SourceReviewRequest,
    SourceSubmissionModel,
    SubmitResearchQuestionRequest,
    SubmitSessionFeedbackRequest,
    SubmitSourceRequest,
    TesterInviteRequest,
    TesterRegisterRequest,
    PlatformActorRequest,
    PlatformCommentCreateRequest,
    PlatformInvitationAcceptRequest,
    PlatformInvitationCreateRequest,
    PlatformKnowledgeCreateRequest,
    PlatformResearchQuestionCreateRequest,
    PlatformResearchQuestionUpdateRequest,
    PlatformResearchStatusChangeRequest,
    PlatformScenarioConvertRequest,
    AgentCommand,
    AgentState,
    ObservationEvent,
    SimulationEvent,
    SimulationEventTrace,
    SimulationEventReviewNoteCreateRequest,
    SimulationEventReviewNoteUpdateRequest,
)
from app.persona import PersonaStore
from app.research import ResearchStore
from app.research_jobs import ResearchJobsStore
from app.safety import evaluate_message, safe_refusal_message
from app.sources import SourceStore
from app.state import StateStore
from app.testers import TesterStore
from app.platform_store import PlatformStore
from app.db import get_connection, json_dumps


class AdminToggleRequest(BaseModel):
    safe_mode: bool = True


settings = load_settings()
ensure_data_dirs()

persona_store = PersonaStore(PERSONA_FILE)
state_store = StateStore(STATE_FILE)
memory_store = MemoryStore(EPISODIC_FILE, SEMANTIC_FILE, PROCEDURAL_FILE)
conversation_logger = ConversationLogger(CONVERSATIONS_FILE)
tester_store = TesterStore(INVITES_FILE, TESTERS_FILE)
research_store = ResearchStore(RESEARCH_QUESTIONS_FILE, KNOWLEDGE_BASE_FILE, RESEARCH_JOBS_FILE)
feedback_store = FeedbackStore(SESSION_FEEDBACK_FILE)
source_store = SourceStore(SOURCE_QUEUE_FILE, APPROVED_SOURCES_FILE)
research_jobs_store = ResearchJobsStore(RESEARCH_JOBS_FILE, RESEARCH_QUESTIONS_FILE)
project_root = Path(__file__).resolve().parents[1]
def _resolve_platform_db_path() -> Path:
    env_path = os.getenv("ROOMZERO_PLATFORM_DB_PATH")
    if env_path:
        path = Path(env_path)
    else:
        path = project_root / "data" / "platform" / "platform.sqlite"
    return path if path.is_absolute() else project_root / path

platform_db_path = _resolve_platform_db_path()
platform_db_path.parent.mkdir(parents=True, exist_ok=True)
platform_store = PlatformStore(platform_db_path)

safe_mode = True

# --- Unreal bridge runtime (local in-memory MVP) ---
UNREAL_OBSERVATION_CAP = 500
UNREAL_SIMULATION_EVENT_CAP = 500
SIMULATION_EVENT_REVIEW_NOTE_MAX_LENGTH = 2000
SIMULATION_EVENT_REVIEW_AUDIT_DEFAULT_LIMIT = 50
SIMULATION_EVENT_REVIEW_AUDIT_MAX_LIMIT = 200
SIMULATION_EVENT_REVIEW_NOTE_ALLOWED_STATUSES = {"active", "resolved", "flagged", "archived"}
SIMULATION_EVENT_REVIEW_AUDIT_ACTIONS = {
    "simulation_event_review_note_created",
    "simulation_event_review_note_updated",
    "simulation_event_review_note_status_changed",
    "simulation_event_review_note_archived",
}
unreal_agent_states: dict[str, AgentState] = {}
unreal_agent_connections: dict[str, set[WebSocket]] = {}
unreal_observations: list[ObservationEvent] = []
unreal_simulation_events: list[SimulationEvent] = []
unreal_pending_commands: dict[str, list[AgentCommand]] = {}


def _get_real_unreal_token() -> str | None:
    token = os.getenv("ROOMZERO_UNREAL_TOKEN", "").strip()
    return token or None


def _extract_unreal_token(
    authorization: str | None = None,
    query_token: str | None = None,
    header_token: str | None = None,
) -> str | None:
    if query_token:
        token = query_token.strip()
        if token:
            return token
    if header_token:
        token = header_token.strip()
        if token:
            return token
    if authorization:
        auth = authorization.strip()
        if auth.lower().startswith("bearer "):
            bearer = auth[7:].strip()
            if bearer:
                return bearer
        elif auth:
            return auth
    return None


def _validate_unreal_token(token: str | None = None) -> None:
    expected = _get_real_unreal_token()
    if expected is None:
        return
    if token != expected:
        raise HTTPException(status_code=401, detail="Unauthorized")


def _validate_unreal_websocket_token(websocket: WebSocket) -> bool:
    expected = _get_real_unreal_token()
    if expected is None:
        return True
    token = _extract_unreal_token(
        authorization=websocket.headers.get("authorization"),
        query_token=websocket.query_params.get("token"),
        header_token=websocket.headers.get("x-roomzero-unreal-token"),
    )
    return token == expected


def _append_unreal_observation(obs: ObservationEvent) -> None:
    unreal_observations.append(obs)
    overflow = len(unreal_observations) - UNREAL_OBSERVATION_CAP
    if overflow > 0:
        del unreal_observations[0:overflow]


def _queue_unreal_command(agent_id: str, command: AgentCommand) -> None:
    queue = unreal_pending_commands.setdefault(agent_id, [])
    queue.append(command)


def _build_payload_summary(payload: dict) -> dict:
    return {
        "keys": sorted([str(k) for k in payload.keys()])[:10],
        "size": len(payload),
    }


def _append_simulation_event(event: SimulationEvent) -> None:
    unreal_simulation_events.append(event)
    overflow = len(unreal_simulation_events) - UNREAL_SIMULATION_EVENT_CAP
    if overflow > 0:
        del unreal_simulation_events[0:overflow]


def _normalize_observation_to_simulation_event(observation: ObservationEvent) -> SimulationEvent:
    normalized_event_name = observation.event.strip().lower().replace(" ", "_")
    event_type = f"unreal.observation.{normalized_event_name or 'unknown'}"
    payload_summary = _build_payload_summary(observation.payload)

    return SimulationEvent(
        event_type=event_type,
        source="unreal.websocket",
        payload=observation.payload,
        created_at=observation.created_at,
        agent_id=observation.agent_id,
        protocol_version=observation.protocol_version,
        status="accepted",
        severity="info",
        transport="websocket",
        correlation_id=f"{observation.agent_id}:{observation.created_at}",
        schema_version="roomzero.simulation-event.v1",
        metadata={
            "observation_event": observation.event,
            "normalization_rule": "strip+lower+space_to_underscore",
            "transport": "websocket",
            "payload_summary": payload_summary,
        },
    )


def _trace_simulation_event(event: SimulationEvent) -> None:
    print(
        "[simulation-event]"
        f" event_id={event.event_id}"
        f" event_type={event.event_type}"
        f" source={event.source}"
        f" agent_id={event.agent_id or '-'}"
        f" created_at={event.created_at}"
        f" status={event.status or '-'}"
        f" payload_summary={event.metadata.get('payload_summary', {})}"
    )


async def _drain_queued_unreal_commands(agent_id: str, websocket: WebSocket) -> None:
    queue = unreal_pending_commands.get(agent_id)
    if not queue:
        return

    while queue:
        command = queue[0]
        try:
            await websocket.send_json(command.model_dump())
        except Exception:
            break
        queue.pop(0)

    if not queue:
        unreal_pending_commands.pop(agent_id, None)


def _get_or_create_unreal_state(agent_id: str) -> AgentState:
    state = unreal_agent_states.get(agent_id)
    if state is None:
        state = AgentState(agent_id=agent_id)
        unreal_agent_states[agent_id] = state
    return state


def _build_greeting_command(agent_id: str) -> AgentCommand:
    return AgentCommand(
        agent_id=agent_id,
        command="speak",
        text="I am RZ-01. I observe, learn, and reflect.",
        emotion="curious",
        animation="Gesture_Explain",
        duration_seconds=4.0,
    )


def _register_unreal_socket(agent_id: str, websocket: WebSocket) -> None:
    sockets = unreal_agent_connections.setdefault(agent_id, set())
    sockets.add(websocket)


def _unregister_unreal_socket(agent_id: str, websocket: WebSocket) -> None:
    sockets = unreal_agent_connections.get(agent_id)
    if not sockets:
        return
    sockets.discard(websocket)
    if not sockets:
        unreal_agent_connections.pop(agent_id, None)


async def _broadcast_unreal_command(agent_id: str, command: AgentCommand) -> int:
    sockets = list(unreal_agent_connections.get(agent_id, set()))
    delivered = 0
    for sock in sockets:
        try:
            await sock.send_json(command.model_dump())
            delivered += 1
        except Exception:
            _unregister_unreal_socket(agent_id, sock)
    return delivered


app = FastAPI(title="RoomZero API", version="0.1.0")

# M2.1 CORS policy:
# Keep this allowlist minimal and explicit for known frontend origins.
# Tighten further in production by restricting to your exact deployed frontend domain(s).
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:8000",
        "http://localhost:8000",
        "https://knoksen.github.io",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)

def _resolve_static_dir() -> Path:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        candidate = Path(getattr(sys, "_MEIPASS")) / "app" / "static"
        if candidate.exists():
            return candidate
    return Path(__file__).resolve().parent / "static"


STATIC_DIR = _resolve_static_dir()
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/ui")
def ui_page() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    persona = persona_store.load()
    return HealthResponse(status="ok", name=persona.name, safe_mode=safe_mode)


@app.get("/persona")
def get_persona() -> dict:
    persona = persona_store.load()
    return persona.model_dump()


@app.get("/state")
def get_state() -> dict:
    state = state_store.load()
    return state.model_dump()


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    global safe_mode

    persona = persona_store.load()
    state = state_store.load()
    safety = evaluate_message(request.message)

    if safe_mode and not safety.allowed:
        refusal = safe_refusal_message()
        conversation_logger.add(
            ConversationLogItem(
                user_message=request.message,
                assistant_message=refusal,
                mode="local_fallback",
                safety_flagged=True,
            )
        )
        return ChatResponse(
            reply=refusal,
            mode="local_fallback",
            state=state,
            stored_memory=False,
        )

    recent_memories = memory_store.get_recent(limit=settings.max_recent_memories)
    approved_knowledge = research_store.get_recent_knowledge(limit=10)
    knowledge_context = "\n".join(
        [f"- {k.summary} (category={k.category})" for k in approved_knowledge]
    )
    context = (
        build_context(persona, state, recent_memories)
        + "\n\nApproved research knowledge base:\n"
        + (knowledge_context if knowledge_context else "No approved research knowledge yet.")
    )

    reply, mode = generate_reply(
        user_message=request.message,
        context=context,
        openai_api_key=settings.openai_api_key,
        openai_model=settings.openai_model,
        persona=persona,
        state=state,
        memories=recent_memories,
    )

    updated_state = state_store.update_after_interaction(state, request.message)

    should_store = "remember" in request.message.lower()
    stored_memory = False
    is_tester_chat = request.tester_id is not None

    if request.tester_id:
        tester = tester_store.get_tester(request.tester_id)
        if tester is None or not tester.active:
            raise HTTPException(status_code=404, detail="Tester not found or inactive.")
        if not tester_store.check_tester_permissions(request.tester_id, "chat"):
            raise HTTPException(status_code=403, detail="Tester does not have chat permission.")
        tester_store.touch_last_seen(request.tester_id)

    if should_store and not is_tester_chat:
        if safety.requires_memory_consent:
            reply += (
                "\n\nI detected potentially sensitive details. "
                "Please confirm explicit consent before I store this."
            )
        else:
            memory_store.add_memory(
                MemoryItem(
                    category="episodic",
                    content=request.message,
                    importance=0.65,
                    tags=["user_requested_memory"],
                    source="user",
                )
            )
            stored_memory = True

    if "research question" in request.message.lower():
        reply += "\n\nI can treat that as a research question and place it in the review queue."
    if "unapproved" in request.message.lower() or "queue" in request.message.lower():
        reply += "\nThis is not approved knowledge yet."
    if approved_knowledge:
        reply += "\nThis comes from the approved research knowledge base."

    conversation_logger.add(
        ConversationLogItem(
            user_message=request.message,
            assistant_message=reply,
            mode=mode,
            safety_flagged=(not safety.allowed or safety.flagged),
        )
    )

    return ChatResponse(reply=reply, mode=mode, state=updated_state, stored_memory=stored_memory)


@app.post("/testers/invite")
def create_tester_invite(request: TesterInviteRequest) -> dict:
    invite = tester_store.create_invite_code(request.role)
    return {"status": "created", "invite": invite.model_dump()}


@app.post("/testers/register")
def register_tester(request: TesterRegisterRequest) -> dict:
    try:
        tester = tester_store.register_tester(
            display_name=request.display_name,
            invite_code=request.invite_code,
            consent_accepted=request.consent_accepted,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"status": "registered", "tester": tester.model_dump()}


@app.get("/testers")
def list_testers() -> dict:
    testers = tester_store.list_testers(include_inactive=True)
    return {"count": len(testers), "items": [t.model_dump() for t in testers]}


@app.get("/testers/{tester_id}")
def get_tester(tester_id: str) -> dict:
    tester = tester_store.get_tester(tester_id)
    if tester is None:
        raise HTTPException(status_code=404, detail="Tester not found.")
    return tester.model_dump()


@app.post("/testers/{tester_id}/deactivate")
def deactivate_tester(tester_id: str) -> dict:
    try:
        tester = tester_store.deactivate_tester(tester_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"status": "deactivated", "tester": tester.model_dump()}


@app.post("/research/questions")
def submit_research_question(request: SubmitResearchQuestionRequest) -> dict:
    from app.models import ResearchQuestionModel

    question = research_store.submit_research_question(
        question=ResearchQuestionModel(
            question=request.question,
            category=request.category,
            submitted_by=request.submitted_by,
            priority=request.priority,
            tags=request.tags,
            linked_sources=request.linked_sources,
        )
    )
    return {"status": "submitted", "question": question.model_dump()}


@app.get("/research/questions")
def list_research_questions(status: str | None = None) -> dict:
    # Keep runtime behavior unchanged while satisfying static type checkers.
    items = research_store.list_research_questions(status=status) if status else research_store.list_research_questions()  # type: ignore[arg-type]
    return {"count": len(items), "items": [q.model_dump() for q in items]}


@app.get("/research/questions/{question_id}")
def get_research_question(question_id: str) -> dict:
    question = research_store.get_research_question(question_id)
    if question is None:
        raise HTTPException(status_code=404, detail="Research question not found.")
    return question.model_dump()


@app.post("/research/questions/{question_id}/answer")
def add_research_answer(question_id: str, request: ResearchAnswerRequest) -> dict:
    try:
        question = research_store.add_research_answer(
            question_id=question_id,
            answer=request.answer,
            reviewer_notes=request.reviewer_notes,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"status": "answered", "question": question.model_dump()}


@app.post("/research/questions/{question_id}/approve")
def approve_research_question(question_id: str, request: ResearchReviewRequest) -> dict:
    try:
        question = research_store.approve_research_question(
            question_id=question_id,
            reviewer_notes=request.reviewer_notes,
            approved_summary=request.approved_summary,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"status": "approved", "question": question.model_dump()}


@app.post("/research/questions/{question_id}/reject")
def reject_research_question(question_id: str, request: ResearchReviewRequest) -> dict:
    try:
        question = research_store.reject_research_question(
            question_id=question_id,
            reviewer_notes=request.reviewer_notes,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"status": "rejected", "question": question.model_dump()}


@app.get("/research/knowledge")
def get_recent_knowledge(limit: int = 20) -> dict:
    items = research_store.get_recent_knowledge(limit=limit)
    return {"count": len(items), "items": [k.model_dump() for k in items]}


@app.get("/research/knowledge/search")
def search_knowledge(query: str) -> dict:
    items = research_store.search_knowledge_base(query=query)
    return {"count": len(items), "items": [k.model_dump() for k in items]}


@app.post("/research/jobs")
def create_research_job(request: ResearchJobCreateRequest) -> dict:
    job = research_jobs_store.create_research_job(
        ResearchJobModel(
            name=request.name,
            topic=request.topic,
            category=request.category,
            query=request.query,
            schedule=request.schedule,
            created_by=request.created_by,
            notes=request.notes,
            status="active",
        )
    )
    return {"status": "created", "job": job.model_dump()}


@app.get("/research/jobs")
def list_research_jobs() -> dict:
    jobs = research_jobs_store.list_research_jobs()
    return {"count": len(jobs), "items": [j.model_dump() for j in jobs]}


@app.post("/research/jobs/{job_id}/run")
def run_research_job(job_id: str) -> dict:
    try:
        result = research_jobs_store.run_manual_research_job(job_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"status": "ran", "result": result}


@app.post("/research/jobs/{job_id}/pause")
def pause_research_job(job_id: str) -> dict:
    try:
        job = research_jobs_store.pause_research_job(job_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"status": "paused", "job": job.model_dump()}


@app.post("/research/jobs/{job_id}/activate")
def activate_research_job(job_id: str) -> dict:
    try:
        job = research_jobs_store.activate_research_job(job_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"status": "active", "job": job.model_dump()}


@app.post("/feedback/session")
def submit_session_feedback(request: SubmitSessionFeedbackRequest) -> dict:
    feedback = feedback_store.submit_session_feedback(
        SessionFeedbackModel(
            tester_id=request.tester_id,
            session_id=request.session_id,
            realism_score=request.realism_score,
            coherence_score=request.coherence_score,
            memory_score=request.memory_score,
            emotional_presence_score=request.emotional_presence_score,
            ethical_safety_score=request.ethical_safety_score,
            usefulness_score=request.usefulness_score,
            uncanny_score=request.uncanny_score,
            trust_score=request.trust_score,
            free_text=request.free_text,
            suggested_improvement=request.suggested_improvement,
        )
    )
    return {"status": "submitted", "feedback": feedback.model_dump()}


@app.get("/feedback")
def list_feedback(tester_id: str | None = None) -> dict:
    items = feedback_store.list_feedback(tester_id=tester_id)
    return {"count": len(items), "items": [f.model_dump() for f in items]}


@app.get("/feedback/stats")
def feedback_stats() -> dict:
    return feedback_store.get_feedback_stats()


@app.post("/sources/submit")
def submit_source(request: SubmitSourceRequest) -> dict:
    source = source_store.submit_source(
        SourceSubmissionModel(
            url_or_reference=request.url_or_reference,
            title=request.title,
            submitted_by=request.submitted_by,
            category=request.category,
            claimed_relevance=request.claimed_relevance,
        )
    )
    return {"status": "submitted", "source": source.model_dump()}


@app.get("/sources/queue")
def list_source_queue() -> dict:
    items = source_store.list_source_queue()
    return {"count": len(items), "items": [s.model_dump() for s in items]}


@app.post("/sources/{source_id}/approve")
def approve_source(source_id: str, request: SourceReviewRequest) -> dict:
    try:
        source = source_store.approve_source(source_id=source_id, reviewer_notes=request.reviewer_notes)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"status": "approved", "source": source.model_dump()}


@app.post("/sources/{source_id}/reject")
def reject_source(source_id: str, request: SourceReviewRequest) -> dict:
    try:
        source = source_store.reject_source(source_id=source_id, reviewer_notes=request.reviewer_notes)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"status": "rejected", "source": source.model_dump()}


@app.get("/sources/approved")
def list_approved_sources() -> dict:
    items = source_store.list_approved_sources()
    return {"count": len(items), "items": [s.model_dump() for s in items]}


@app.post("/memory")
def create_memory(request: MemoryCreateRequest) -> dict:
    if evaluate_message(request.content).requires_memory_consent:
        raise HTTPException(
            status_code=400,
            detail="Potentially sensitive information detected. Confirm consent before storing.",
        )

    item = MemoryItem(
        category=request.category,
        content=request.content,
        importance=request.importance,
        tags=request.tags,
        source=request.source,
    )
    memory_store.add_memory(item)
    return {"status": "stored", "memory": item.model_dump()}


@app.get("/memory/recent")
def memory_recent(limit: int = 20) -> dict:
    items = memory_store.get_recent(limit=limit)
    return {"count": len(items), "items": [m.model_dump() for m in items]}


@app.get("/logs/recent")
def logs_recent(limit: int = 50) -> dict:
    logs = conversation_logger.recent(limit=limit)
    return {"count": len(logs), "items": [log.model_dump() for log in logs]}


@app.post("/admin/shutdown-safe-mode")
def admin_shutdown_safe_mode(request: AdminToggleRequest) -> dict:
    global safe_mode
    safe_mode = request.safe_mode
    return {"safe_mode": safe_mode, "status": "updated"}


# --- M2 platform routes ---
@app.post("/platform/invitations")
def platform_create_invitation(request: PlatformInvitationCreateRequest) -> dict:
    try:
        platform_store.require_role(request.actor_id, {"admin", "reviewer"})
        invite = platform_store.create_invitation(
            role=request.role,
            invited_by=request.actor_id,
            expires_in_hours=request.expires_in_hours,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"status": "created", "invitation": invite}


@app.get("/platform/invitations")
def platform_list_invitations(actor_id: str) -> dict:
    try:
        platform_store.require_role(actor_id, {"admin", "reviewer"})
        items = platform_store.list_invitations()
    except ValueError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    return {"count": len(items), "items": items}


@app.post("/platform/invitations/accept")
def platform_accept_invitation(request: PlatformInvitationAcceptRequest) -> dict:
    try:
        user = platform_store.accept_invitation(
            invite_code=request.invite_code,
            display_name=request.display_name,
            accepted_by=request.accepted_by,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"status": "accepted", "user": user}


@app.get("/platform/users")
def platform_list_users(actor_id: str) -> dict:
    try:
        platform_store.require_role(actor_id, {"admin", "reviewer"})
        items = platform_store.list_users()
    except ValueError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    return {"count": len(items), "items": items}


@app.get("/platform/users/{user_id}")
def platform_get_user(user_id: str, actor_id: str) -> dict:
    try:
        platform_store.require_role(actor_id, {"admin", "reviewer"})
        user = platform_store.get_user(user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found.")
    except ValueError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    return user


@app.post("/platform/research/questions")
def platform_create_question(request: PlatformResearchQuestionCreateRequest) -> dict:
    try:
        question = platform_store.create_research_question(
            actor_id=request.actor_id,
            title=request.title,
            description=request.description,
            category=request.category,
            hypothesis=request.hypothesis,
            simulation_relevance=request.simulation_relevance,
            ethical_risk=request.ethical_risk,
            suggested_conditions=request.suggested_conditions,
            tags=request.tags,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"status": "created", "question": question}


@app.get("/platform/research/questions")
def platform_list_questions(actor_id: str) -> dict:
    try:
        platform_store.require_role(actor_id, {"admin", "reviewer", "researcher", "tester", "observer", "contributor"})
        items = platform_store.list_research_questions()
    except ValueError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    return {"count": len(items), "items": items}


@app.get("/platform/research/questions/{question_id}")
def platform_get_question(question_id: str, actor_id: str) -> dict:
    try:
        platform_store.require_role(actor_id, {"admin", "reviewer", "researcher", "tester", "observer", "contributor"})
        question = platform_store.get_research_question(question_id)
        if question is None:
            raise HTTPException(status_code=404, detail="Research question not found.")
    except ValueError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    return question


@app.patch("/platform/research/questions/{question_id}")
def platform_update_question(question_id: str, request: PlatformResearchQuestionUpdateRequest) -> dict:
    try:
        question = platform_store.update_research_question(
            actor_id=request.actor_id,
            question_id=question_id,
            title=request.title,
            description=request.description,
            hypothesis=request.hypothesis,
            simulation_relevance=request.simulation_relevance,
            ethical_risk=request.ethical_risk,
            suggested_conditions=request.suggested_conditions,
            tags=request.tags,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"status": "updated", "question": question}


@app.post("/platform/research/questions/{question_id}/status")
def platform_change_question_status(question_id: str, request: PlatformResearchStatusChangeRequest) -> dict:
    try:
        question = platform_store.change_research_status(
            actor_id=request.actor_id,
            question_id=question_id,
            status=request.status,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"status": "updated", "question": question}


@app.post("/platform/research/questions/{question_id}/comments")
def platform_add_comment(question_id: str, request: PlatformCommentCreateRequest) -> dict:
    try:
        comment = platform_store.add_comment(
            actor_id=request.actor_id,
            question_id=question_id,
            comment=request.comment,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"status": "created", "comment": comment}


@app.get("/platform/research/questions/{question_id}/comments")
def platform_list_comments(question_id: str, actor_id: str) -> dict:
    try:
        platform_store.require_role(actor_id, {"admin", "reviewer", "researcher", "tester", "observer", "contributor"})
        items = platform_store.list_comments(question_id)
    except ValueError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    return {"count": len(items), "items": items}


@app.post("/platform/research/questions/{question_id}/convert-scenario")
def platform_convert_scenario(question_id: str, request: PlatformScenarioConvertRequest) -> dict:
    try:
        scenario = platform_store.create_scenario_from_question(
            actor_id=request.actor_id,
            question_id=question_id,
            purpose=request.purpose,
            agent_type=request.agent_type,
            environment=request.environment,
            variables=request.variables,
            metrics=request.metrics,
            ethical_constraints=request.ethical_constraints,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"status": "created", "scenario": scenario}


@app.get("/platform/scenarios")
def platform_list_scenarios(actor_id: str) -> dict:
    try:
        platform_store.require_role(actor_id, {"admin", "reviewer", "researcher", "tester", "observer", "contributor"})
        items = platform_store.list_scenarios()
    except ValueError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    return {"count": len(items), "items": items}


@app.get("/platform/scenarios/{scenario_id}")
def platform_get_scenario(scenario_id: str, actor_id: str) -> dict:
    try:
        platform_store.require_role(actor_id, {"admin", "reviewer", "researcher", "tester", "observer", "contributor"})
        scenario = platform_store.get_scenario(scenario_id)
        if scenario is None:
            raise HTTPException(status_code=404, detail="Scenario not found.")
    except ValueError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    return scenario


@app.post("/platform/knowledge")
def platform_create_knowledge(request: PlatformKnowledgeCreateRequest) -> dict:
    try:
        item = platform_store.create_knowledge_entry(
            actor_id=request.actor_id,
            title=request.title,
            content=request.content,
            source_type=request.source_type,
            source_id=request.source_id,
            linked_question_id=request.linked_question_id,
            linked_scenario_id=request.linked_scenario_id,
            linked_observation_id=request.linked_observation_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"status": "created", "knowledge": item}


@app.get("/platform/knowledge")
def platform_list_knowledge(actor_id: str) -> dict:
    try:
        platform_store.require_role(actor_id, {"admin", "reviewer", "researcher", "tester", "observer", "contributor"})
        items = platform_store.list_knowledge_entries()
    except ValueError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    return {"count": len(items), "items": items}


@app.get("/platform/knowledge/{knowledge_id}")
def platform_get_knowledge(knowledge_id: str, actor_id: str) -> dict:
    try:
        platform_store.require_role(actor_id, {"admin", "reviewer", "researcher", "tester", "observer", "contributor"})
        item = platform_store.get_knowledge_entry(knowledge_id)
        if item is None:
            raise HTTPException(status_code=404, detail="Knowledge entry not found.")
    except ValueError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    return item


@app.post("/platform/audit")
def platform_recent_activity(request: PlatformActorRequest) -> dict:
    try:
        platform_store.require_role(request.actor_id, {"admin", "reviewer"})
        items = platform_store.recent_activity(limit=200)
    except ValueError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    return {"count": len(items), "items": items}


# --- Unreal WebSocket bridge routes (local in-memory MVP) ---
@app.get("/ws/unreal/state/{agent_id}")
def unreal_get_state(agent_id: str) -> dict:
    return _get_or_create_unreal_state(agent_id).model_dump()


@app.post("/ws/unreal/command/{agent_id}")
async def unreal_send_command(
    agent_id: str,
    request: AgentCommand,
    token: str | None = None,
    authorization: str | None = Header(None),
    x_roomzero_unreal_token: str | None = Header(None),
) -> dict:
    _validate_unreal_token(
        _extract_unreal_token(
            authorization=authorization,
            query_token=token,
            header_token=x_roomzero_unreal_token,
        )
    )
    if request.agent_id != agent_id:
        raise HTTPException(status_code=400, detail="agent_id path/body mismatch")

    delivered_count = await _broadcast_unreal_command(agent_id, request)
    delivered = delivered_count > 0
    queued = False
    if not delivered:
        _queue_unreal_command(agent_id, request)
        queued = True

    return {
        "queued": queued,
        "delivered": delivered,
        "agent_id": agent_id,
        "command": request.model_dump(),
        "protocol_version": request.protocol_version,
    }


@app.get("/ws/unreal/observations")
def unreal_list_observations() -> dict:
    return {"count": len(unreal_observations), "items": [o.model_dump() for o in unreal_observations]}


def _safe_simulation_event_view(event: SimulationEvent) -> dict:
    data = event.model_dump()
    metadata = data.get("metadata", {}) if isinstance(data.get("metadata"), dict) else {}
    payload_summary = metadata.get("payload_summary")
    if not isinstance(payload_summary, dict):
        payload = data.get("payload", {})
        if not isinstance(payload, dict):
            payload = {}
        payload_summary = _build_payload_summary(payload)

    risk_summary: dict = {}
    maybe_risk_summary = metadata.get("risk_summary")
    if isinstance(maybe_risk_summary, dict):
        risk_summary = maybe_risk_summary
    elif data.get("severity") or data.get("status"):
        risk_summary = {
            "severity": data.get("severity"),
            "status": data.get("status"),
        }

    return {
        "event_id": data["event_id"],
        "created_at": data["created_at"],
        "source": data["source"],
        "event_type": data["event_type"],
        "agent_id": data.get("agent_id"),
        "status": data.get("status"),
        "severity": data.get("severity"),
        "protocol_version": data.get("protocol_version"),
        "transport": data.get("transport"),
        "schema_version": data.get("schema_version"),
        "payload_summary": payload_summary,
        "risk_summary": risk_summary,
    }


def _simulation_event_trace_view(event: SimulationEvent) -> dict:
    safe = _safe_simulation_event_view(event)
    data = event.model_dump()
    metadata = data.get("metadata", {}) if isinstance(data.get("metadata"), dict) else {}
    trace = SimulationEventTrace(
        event_id=data["event_id"],
        event_type=data["event_type"],
        source=data["source"],
        agent_id=data.get("agent_id"),
        created_at=data["created_at"],
        status=data.get("status"),
        severity=data.get("severity"),
        protocol_version=data.get("protocol_version"),
        schema_version=data.get("schema_version") or "roomzero.simulation-event.v1",
        payload_summary=safe["payload_summary"],
        metadata={
            "normalization_rule": metadata.get("normalization_rule"),
            "observation_event": metadata.get("observation_event"),
            "transport": metadata.get("transport"),
            "correlation_id": data.get("correlation_id"),
            "trace_id": data.get("trace_id"),
            "parent_event_id": data.get("parent_event_id"),
        },
    )
    return trace.model_dump()


def _normalize_optional_filter(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip().lower()
    return normalized or None


def _matches_optional_filter(actual: str | None, expected: str | None) -> bool:
    if expected is None:
        return True
    return (actual or "").strip().lower() == expected


def _find_simulation_event(event_id: str) -> SimulationEvent | None:
    for event in reversed(unreal_simulation_events):
        if event.event_id == event_id:
            return event
    return None


def _coerce_events_limit(limit: int) -> int:
    if limit < 1:
        raise HTTPException(status_code=400, detail="limit must be >= 1")
    return min(limit, UNREAL_SIMULATION_EVENT_CAP)


def _filter_simulation_events(
    source: str | None = None,
    event_type: str | None = None,
    agent_id: str | None = None,
    status: str | None = None,
    severity: str | None = None,
) -> list[SimulationEvent]:
    source_filter = _normalize_optional_filter(source)
    event_type_filter = _normalize_optional_filter(event_type)
    agent_filter = _normalize_optional_filter(agent_id)
    status_filter = _normalize_optional_filter(status)
    severity_filter = _normalize_optional_filter(severity)

    filtered: list[SimulationEvent] = []
    for event in unreal_simulation_events:
        if not _matches_optional_filter(event.source, source_filter):
            continue
        if not _matches_optional_filter(event.event_type, event_type_filter):
            continue
        if not _matches_optional_filter(event.agent_id, agent_filter):
            continue
        if not _matches_optional_filter(event.status, status_filter):
            continue
        if not _matches_optional_filter(event.severity, severity_filter):
            continue
        filtered.append(event)
    return filtered


def _build_simulation_event_summary(events: list[SimulationEvent]) -> dict:
    by_source: dict[str, int] = {}
    by_event_type: dict[str, int] = {}
    by_status: dict[str, int] = {}
    by_severity: dict[str, int] = {}

    for event in events:
        by_source[event.source] = by_source.get(event.source, 0) + 1
        by_event_type[event.event_type] = by_event_type.get(event.event_type, 0) + 1
        status_key = event.status or "unknown"
        by_status[status_key] = by_status.get(status_key, 0) + 1
        severity_key = event.severity or "unknown"
        by_severity[severity_key] = by_severity.get(severity_key, 0) + 1

    return {
        "total_events": len(events),
        "by_source": by_source,
        "by_event_type": by_event_type,
        "by_status": by_status,
        "by_severity": by_severity,
    }


@app.get("/simulation/events")
def list_simulation_events(
    source: str | None = None,
    event_type: str | None = None,
    agent_id: str | None = None,
    status: str | None = None,
    severity: str | None = None,
    limit: int = 50,
) -> dict:
    bounded_limit = _coerce_events_limit(limit)
    filtered_events = _filter_simulation_events(
        source=source,
        event_type=event_type,
        agent_id=agent_id,
        status=status,
        severity=severity,
    )
    items = [_safe_simulation_event_view(e) for e in reversed(filtered_events[-bounded_limit:])]
    return {"count": len(filtered_events), "items": items}


@app.get("/simulation/events/summary")
def simulation_events_summary(
    source: str | None = None,
    event_type: str | None = None,
    agent_id: str | None = None,
    status: str | None = None,
    severity: str | None = None,
) -> dict:
    filtered_events = _filter_simulation_events(
        source=source,
        event_type=event_type,
        agent_id=agent_id,
        status=status,
        severity=severity,
    )
    return _build_simulation_event_summary(filtered_events)


@app.get("/simulation/events/{event_id}")
def get_simulation_event(event_id: str) -> dict:
    event = _find_simulation_event(event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Simulation event not found.")
    return _safe_simulation_event_view(event)


@app.get("/simulation/events/{event_id}/traces")
def get_simulation_event_traces(event_id: str) -> dict:
    event = _find_simulation_event(event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Simulation event not found.")
    return {"count": 1, "items": [_simulation_event_trace_view(event)]}


def _normalize_reviewer_id(value: str | None) -> str:
    if value is None:
        return "ui_reviewer"
    normalized = value.strip()
    return normalized or "ui_reviewer"


def _normalize_review_note_status(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip().lower()
    if not normalized:
        return None
    if normalized not in SIMULATION_EVENT_REVIEW_NOTE_ALLOWED_STATUSES:
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid review note status. "
                f"Allowed: {sorted(SIMULATION_EVENT_REVIEW_NOTE_ALLOWED_STATUSES)}"
            ),
        )
    return normalized


def _validate_review_note_text(note_text: str) -> str:
    normalized = note_text.strip()
    if not normalized:
        raise HTTPException(status_code=400, detail="Review note text cannot be empty.")
    if len(normalized) > SIMULATION_EVENT_REVIEW_NOTE_MAX_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"Review note exceeds max length ({SIMULATION_EVENT_REVIEW_NOTE_MAX_LENGTH}).",
        )
    return normalized


@app.get("/simulation/events/{event_id}/review-notes")
def get_simulation_event_review_notes(event_id: str) -> dict:
    event = _find_simulation_event(event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Simulation event not found.")

    with get_connection(platform_db_path) as conn:
        rows = conn.execute(
            """
            SELECT id, event_id, note_text, reviewer_id, status, created_at, updated_at
            FROM simulation_event_review_notes
            WHERE event_id = ?
            ORDER BY created_at DESC
            """,
            (event_id,),
        ).fetchall()

    items = [dict(row) for row in rows]
    return {"count": len(items), "items": items}


def _get_simulation_event_review_note(event_id: str, note_id: str) -> dict | None:
    with get_connection(platform_db_path) as conn:
        row = conn.execute(
            """
            SELECT id, event_id, note_text, reviewer_id, status, created_at, updated_at
            FROM simulation_event_review_notes
            WHERE id = ? AND event_id = ?
            LIMIT 1
            """,
            (note_id, event_id),
        ).fetchone()
    return dict(row) if row else None


def _coerce_review_audit_limit(limit: int) -> int:
    if limit < 1:
        raise HTTPException(status_code=400, detail="limit must be >= 1")
    return min(limit, SIMULATION_EVENT_REVIEW_AUDIT_MAX_LIMIT)


@app.post("/simulation/events/{event_id}/review-notes")
def create_simulation_event_review_note(
    event_id: str,
    request: SimulationEventReviewNoteCreateRequest,
) -> dict:
    event = _find_simulation_event(event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Simulation event not found.")

    note_text = _validate_review_note_text(request.note_text)

    reviewer_id = _normalize_reviewer_id(request.reviewer_id)
    status_value = _normalize_review_note_status(request.status)
    note_id = str(uuid4())
    now = datetime.now(timezone.utc).isoformat()

    with get_connection(platform_db_path) as conn:
        conn.execute(
            """
            INSERT INTO simulation_event_review_notes
            (id, event_id, note_text, reviewer_id, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (note_id, event_id, note_text, reviewer_id, status_value, now, now),
        )
        conn.execute(
            """
            INSERT INTO audit_logs (id, actor_id, action, target_type, target_id, details, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(uuid4()),
                reviewer_id,
                "simulation_event_review_note_created",
                "simulation_event",
                event_id,
                json_dumps(
                    {
                        "event_id": event_id,
                        "note_id": note_id,
                        "note_length": len(note_text),
                        "note_preview": note_text[:120],
                    }
                ),
                now,
            ),
        )

    return {
        "status": "created",
        "note": {
            "id": note_id,
            "event_id": event_id,
            "note_text": note_text,
            "reviewer_id": reviewer_id,
            "status": status_value,
            "created_at": now,
            "updated_at": now,
        },
    }


@app.patch("/simulation/events/{event_id}/review-notes/{note_id}")
def update_simulation_event_review_note(
    event_id: str,
    note_id: str,
    request: SimulationEventReviewNoteUpdateRequest,
) -> dict:
    event = _find_simulation_event(event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Simulation event not found.")

    existing = _get_simulation_event_review_note(event_id, note_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="Review note not found for simulation event.")

    status_provided = request.status is not None
    note_text_provided = request.note_text is not None
    if not status_provided and not note_text_provided:
        raise HTTPException(status_code=400, detail="No review note updates provided.")

    old_status = existing.get("status")
    new_status = _normalize_review_note_status(request.status) if status_provided else old_status
    new_note_text = (
        _validate_review_note_text(request.note_text or "")
        if note_text_provided
        else existing["note_text"]
    )

    now = datetime.now(timezone.utc).isoformat()
    with get_connection(platform_db_path) as conn:
        conn.execute(
            """
            UPDATE simulation_event_review_notes
            SET note_text = ?, status = ?, updated_at = ?
            WHERE id = ? AND event_id = ?
            """,
            (new_note_text, new_status, now, note_id, event_id),
        )

        if note_text_provided:
            conn.execute(
                """
                INSERT INTO audit_logs (id, actor_id, action, target_type, target_id, details, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(uuid4()),
                    existing.get("reviewer_id") or "ui_reviewer",
                    "simulation_event_review_note_updated",
                    "simulation_event",
                    event_id,
                    json_dumps(
                        {
                            "event_id": event_id,
                            "note_id": note_id,
                            "note_length": len(new_note_text),
                            "note_preview": new_note_text[:120],
                        }
                    ),
                    now,
                ),
            )

        if status_provided and old_status != new_status:
            conn.execute(
                """
                INSERT INTO audit_logs (id, actor_id, action, target_type, target_id, details, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(uuid4()),
                    existing.get("reviewer_id") or "ui_reviewer",
                    "simulation_event_review_note_status_changed",
                    "simulation_event",
                    event_id,
                    json_dumps(
                        {
                            "event_id": event_id,
                            "note_id": note_id,
                            "old_status": old_status,
                            "new_status": new_status,
                        }
                    ),
                    now,
                ),
            )

            if new_status == "archived":
                conn.execute(
                    """
                    INSERT INTO audit_logs (id, actor_id, action, target_type, target_id, details, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        str(uuid4()),
                        existing.get("reviewer_id") or "ui_reviewer",
                        "simulation_event_review_note_archived",
                        "simulation_event",
                        event_id,
                        json_dumps(
                            {
                                "event_id": event_id,
                                "note_id": note_id,
                                "old_status": old_status,
                                "new_status": new_status,
                            }
                        ),
                        now,
                    ),
                )

    updated = _get_simulation_event_review_note(event_id, note_id)
    if updated is None:
        raise HTTPException(status_code=404, detail="Review note not found for simulation event.")

    return {"status": "updated", "note": updated}


@app.get("/simulation/events/{event_id}/review-audit")
def get_simulation_event_review_audit(event_id: str, limit: int = SIMULATION_EVENT_REVIEW_AUDIT_DEFAULT_LIMIT) -> dict:
    event = _find_simulation_event(event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Simulation event not found.")

    bounded_limit = _coerce_review_audit_limit(limit)
    action_params = sorted(SIMULATION_EVENT_REVIEW_AUDIT_ACTIONS)
    placeholders = ",".join("?" for _ in action_params)

    with get_connection(platform_db_path) as conn:
        rows = conn.execute(
            f"""
            SELECT action, created_at, target_id, details
            FROM audit_logs
            WHERE target_type = 'simulation_event'
              AND target_id = ?
              AND action IN ({placeholders})
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (event_id, *action_params, bounded_limit),
        ).fetchall()

    items: list[dict] = []
    for row in rows:
        details_raw = row["details"] if isinstance(row["details"], str) else "{}"
        details = {}
        try:
            maybe = json.loads(details_raw)
            if isinstance(maybe, dict):
                details = maybe
        except Exception:
            details = {}

        items.append(
            {
                "action": row["action"],
                "created_at": row["created_at"],
                "target_id": row["target_id"],
                "details": details,
            }
        )

    return {"count": len(items), "items": items}


@app.websocket("/ws/unreal/{agent_id}")
async def unreal_ws(websocket: WebSocket, agent_id: str) -> None:
    if not _validate_unreal_websocket_token(websocket):
        await websocket.close(code=1008)
        return

    await websocket.accept()
    _register_unreal_socket(agent_id, websocket)

    current_state = _get_or_create_unreal_state(agent_id)
    await websocket.send_json(current_state.model_dump())
    await websocket.send_json(_build_greeting_command(agent_id).model_dump())
    await _drain_queued_unreal_commands(agent_id, websocket)

    try:
        while True:
            try:
                message = await websocket.receive_json()
            except ValueError:
                await websocket.send_json(
                    {
                        "type": "error",
                        "protocol_version": "roomzero.unreal.v1",
                        "error": "invalid_payload",
                    }
                )
                continue

            if not isinstance(message, dict):
                await websocket.send_json(
                    {
                        "type": "error",
                        "protocol_version": "roomzero.unreal.v1",
                        "error": "invalid_payload",
                    }
                )
                continue

            msg_type = str(message.get("type", "")).strip().lower()

            if msg_type == "hello":
                await websocket.send_json(_get_or_create_unreal_state(agent_id).model_dump())
                continue

            if msg_type == "observation":
                event_name = str(message.get("event", "")).strip()
                payload = message.get("payload")
                if not event_name:
                    await websocket.send_json(
                        {
                            "type": "error",
                            "protocol_version": "roomzero.unreal.v1",
                            "error": "missing_event",
                        }
                    )
                    continue
                if not isinstance(payload, dict):
                    payload = {}
                obs = ObservationEvent(agent_id=agent_id, event=event_name, payload=payload)
                _append_unreal_observation(obs)
                sim_event = _normalize_observation_to_simulation_event(obs)
                _append_simulation_event(sim_event)
                _trace_simulation_event(sim_event)
                await websocket.send_json(
                    {
                        "type": "ack",
                        "protocol_version": "roomzero.unreal.v1",
                        "kind": "observation",
                        "agent_id": agent_id,
                        "created_at": obs.created_at,
                    }
                )
                continue

            if msg_type == "state_update":
                state = _get_or_create_unreal_state(agent_id)
                emotion = message.get("emotion")
                awareness = message.get("awareness")
                trust = message.get("trust")
                is_speaking = message.get("is_speaking")
                is_observing = message.get("is_observing")

                if isinstance(emotion, str) and emotion.strip():
                    state.emotion = emotion.strip()
                if isinstance(awareness, (int, float)):
                    state.awareness = max(0.0, min(1.0, float(awareness)))
                if isinstance(trust, (int, float)):
                    state.trust = max(0.0, min(1.0, float(trust)))
                if isinstance(is_speaking, bool):
                    state.is_speaking = is_speaking
                if isinstance(is_observing, bool):
                    state.is_observing = is_observing
                state.updated_at = datetime.now(timezone.utc).isoformat()

                unreal_agent_states[agent_id] = state
                await websocket.send_json(state.model_dump())
                continue

            if msg_type == "ping":
                await websocket.send_json(
                    {
                        "type": "pong",
                        "protocol_version": "roomzero.unreal.v1",
                        "agent_id": agent_id,
                    }
                )
                continue

            await websocket.send_json(
                {
                    "type": "error",
                    "protocol_version": "roomzero.unreal.v1",
                    "error": "unknown_message_type",
                }
            )
    except WebSocketDisconnect:
        _unregister_unreal_socket(agent_id, websocket)
    except Exception:
        _unregister_unreal_socket(agent_id, websocket)


def _open_ui_after_delay(delay_seconds: float = 1.5) -> None:
    time.sleep(delay_seconds)
    try:
        webbrowser.open("http://127.0.0.1:8000/ui")
        print("RoomZero: opened browser at http://127.0.0.1:8000/ui")
    except Exception as exc:
        print(f"RoomZero: could not open browser automatically: {exc}")


if __name__ == "__main__":
    print("RoomZero: starting server on http://127.0.0.1:8000")
    threading.Thread(target=_open_ui_after_delay, daemon=True).start()
    try:
        uvicorn.run(app, host="127.0.0.1", port=8000, reload=False)
    except Exception as exc:
        print(f"RoomZero: startup failed: {exc}")
        raise

