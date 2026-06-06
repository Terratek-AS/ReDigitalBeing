from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class PersonaModel(BaseModel):
    name: str
    version: str
    personality_traits: list[str]
    principles: list[str]
    behavioral_rules: list[str]
    boundaries: list[str]
    internal_state_description: str


class EmotionalStateModel(BaseModel):
    calm: float = Field(default=0.8, ge=0.0, le=1.0)
    curiosity: float = Field(default=0.7, ge=0.0, le=1.0)
    focus: float = Field(default=0.7, ge=0.0, le=1.0)
    empathy: float = Field(default=0.7, ge=0.0, le=1.0)
    caution: float = Field(default=0.7, ge=0.0, le=1.0)
    last_updated: str = Field(default_factory=utc_now_iso)


class MemoryItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: str = Field(default_factory=utc_now_iso)
    category: Literal["working", "episodic", "semantic", "procedural"]
    content: str
    importance: float = Field(default=0.5, ge=0.0, le=1.0)
    tags: list[str] = Field(default_factory=list)
    source: str = "user"
    decay_factor: float = Field(default=1.0, ge=0.0, le=1.0)


class ConversationLogItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: str = Field(default_factory=utc_now_iso)
    user_message: str
    assistant_message: str
    mode: Literal["openai", "local_fallback"]
    safety_flagged: bool = False


TesterRole = Literal["observer", "tester", "researcher", "reviewer", "admin"]
ResearchStatus = Literal["submitted", "under_review", "answered", "approved", "rejected", "archived"]
ResearchCategory = Literal[
    "cognitive_architecture",
    "memory_systems",
    "digital_twins",
    "embodiment",
    "simulation",
    "ethics",
    "consciousness_theory",
    "human_ai_interaction",
    "sensors",
    "unreal_engine",
    "sustainability",
    "other",
]
SourceStatus = Literal["submitted", "approved", "rejected", "needs_review"]
ResearchJobStatus = Literal["active", "paused", "completed", "failed"]


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=5000)
    tester_id: str | None = None


class ChatResponse(BaseModel):
    reply: str
    mode: Literal["openai", "local_fallback"]
    state: EmotionalStateModel
    stored_memory: bool


class MemoryCreateRequest(BaseModel):
    content: str = Field(min_length=1, max_length=5000)
    category: Literal["episodic", "semantic", "procedural"] = "episodic"
    importance: float = Field(default=0.6, ge=0.0, le=1.0)
    tags: list[str] = Field(default_factory=list)
    source: str = "user"


class HealthResponse(BaseModel):
    status: str
    name: str
    safe_mode: bool


class InviteCodeModel(BaseModel):
    invite_code: str
    role: TesterRole
    created_at: str = Field(default_factory=utc_now_iso)
    active: bool = True


class TesterModel(BaseModel):
    tester_id: str = Field(default_factory=lambda: str(uuid4()))
    display_name: str
    role: TesterRole
    invite_code: str
    consent_accepted: bool
    created_at: str = Field(default_factory=utc_now_iso)
    last_seen: str = Field(default_factory=utc_now_iso)
    active: bool = True
    permissions: list[str] = Field(default_factory=list)


class TesterInviteRequest(BaseModel):
    role: TesterRole


class TesterRegisterRequest(BaseModel):
    display_name: str = Field(min_length=1, max_length=200)
    invite_code: str = Field(min_length=4, max_length=200)
    consent_accepted: bool = True


class ResearchQuestionModel(BaseModel):
    question_id: str = Field(default_factory=lambda: str(uuid4()))
    question: str
    category: ResearchCategory
    submitted_by: str
    timestamp: str = Field(default_factory=utc_now_iso)
    status: ResearchStatus = "submitted"
    priority: int = Field(default=5, ge=1, le=10)
    tags: list[str] = Field(default_factory=list)
    linked_sources: list[str] = Field(default_factory=list)
    eir_answer: str | None = None
    reviewer_notes: str | None = None
    approved_summary: str | None = None


class SubmitResearchQuestionRequest(BaseModel):
    question: str = Field(min_length=1, max_length=5000)
    category: ResearchCategory
    submitted_by: str
    priority: int = Field(default=5, ge=1, le=10)
    tags: list[str] = Field(default_factory=list)
    linked_sources: list[str] = Field(default_factory=list)


class ResearchAnswerRequest(BaseModel):
    answer: str = Field(min_length=1, max_length=10000)
    reviewer_notes: str | None = None


class ResearchReviewRequest(BaseModel):
    reviewer_notes: str | None = None
    approved_summary: str | None = None


class KnowledgeEntryModel(BaseModel):
    knowledge_id: str = Field(default_factory=lambda: str(uuid4()))
    question_id: str
    category: ResearchCategory
    summary: str
    answer: str
    approved_by: str
    approved_at: str = Field(default_factory=utc_now_iso)
    tags: list[str] = Field(default_factory=list)
    linked_sources: list[str] = Field(default_factory=list)


class SessionFeedbackModel(BaseModel):
    feedback_id: str = Field(default_factory=lambda: str(uuid4()))
    tester_id: str
    session_id: str
    timestamp: str = Field(default_factory=utc_now_iso)
    realism_score: int = Field(ge=1, le=10)
    coherence_score: int = Field(ge=1, le=10)
    memory_score: int = Field(ge=1, le=10)
    emotional_presence_score: int = Field(ge=1, le=10)
    ethical_safety_score: int = Field(ge=1, le=10)
    usefulness_score: int = Field(ge=1, le=10)
    uncanny_score: int = Field(ge=1, le=10)
    trust_score: int = Field(ge=1, le=10)
    free_text: str = ""
    suggested_improvement: str = ""


class SubmitSessionFeedbackRequest(BaseModel):
    tester_id: str
    session_id: str
    realism_score: int = Field(ge=1, le=10)
    coherence_score: int = Field(ge=1, le=10)
    memory_score: int = Field(ge=1, le=10)
    emotional_presence_score: int = Field(ge=1, le=10)
    ethical_safety_score: int = Field(ge=1, le=10)
    usefulness_score: int = Field(ge=1, le=10)
    uncanny_score: int = Field(ge=1, le=10)
    trust_score: int = Field(ge=1, le=10)
    free_text: str = ""
    suggested_improvement: str = ""


class SourceSubmissionModel(BaseModel):
    source_id: str = Field(default_factory=lambda: str(uuid4()))
    url_or_reference: str
    title: str
    submitted_by: str
    timestamp: str = Field(default_factory=utc_now_iso)
    category: ResearchCategory
    claimed_relevance: str
    reliability_score: int = Field(default=1, ge=1, le=10)
    status: SourceStatus = "submitted"
    reviewer_notes: str | None = None


class SubmitSourceRequest(BaseModel):
    url_or_reference: str = Field(min_length=1, max_length=2000)
    title: str = Field(min_length=1, max_length=500)
    submitted_by: str
    category: ResearchCategory
    claimed_relevance: str = Field(min_length=1, max_length=5000)


class SourceReviewRequest(BaseModel):
    reviewer_notes: str | None = None


class ResearchJobModel(BaseModel):
    job_id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    topic: str
    category: ResearchCategory
    query: str
    schedule: str = "manual"
    status: ResearchJobStatus = "active"
    last_run: str | None = None
    next_run: str | None = None
    created_by: str = "system"
    notes: str = ""


class ResearchJobCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    topic: str = Field(min_length=1, max_length=500)
    category: ResearchCategory = "other"
    query: str = Field(min_length=1, max_length=1000)
    schedule: str = "manual"
    created_by: str = "admin"
    notes: str = ""


# --- M2 platform requests ---
class PlatformActorRequest(BaseModel):
    actor_id: str = Field(min_length=1, max_length=200)


class PlatformInvitationCreateRequest(BaseModel):
    actor_id: str = Field(min_length=1, max_length=200)
    role: str = Field(min_length=1, max_length=50)
    expires_in_hours: int = Field(default=72, ge=1, le=24 * 30)


class PlatformInvitationAcceptRequest(BaseModel):
    invite_code: str = Field(min_length=4, max_length=200)
    display_name: str = Field(min_length=1, max_length=200)
    accepted_by: str | None = None


class PlatformResearchQuestionCreateRequest(BaseModel):
    actor_id: str = Field(min_length=1, max_length=200)
    title: str = Field(min_length=1, max_length=500)
    description: str = Field(min_length=1, max_length=10000)
    category: str = Field(min_length=1, max_length=100)
    hypothesis: str = Field(min_length=1, max_length=5000)
    simulation_relevance: str = Field(min_length=1, max_length=5000)
    ethical_risk: str = Field(min_length=1, max_length=2000)
    suggested_conditions: str = Field(min_length=1, max_length=5000)
    tags: list[str] = Field(default_factory=list)


class PlatformResearchQuestionUpdateRequest(BaseModel):
    actor_id: str = Field(min_length=1, max_length=200)
    title: str | None = None
    description: str | None = None
    hypothesis: str | None = None
    simulation_relevance: str | None = None
    ethical_risk: str | None = None
    suggested_conditions: str | None = None
    tags: list[str] | None = None


class PlatformResearchStatusChangeRequest(BaseModel):
    actor_id: str = Field(min_length=1, max_length=200)
    status: str = Field(min_length=1, max_length=50)


class PlatformCommentCreateRequest(BaseModel):
    actor_id: str = Field(min_length=1, max_length=200)
    comment: str = Field(min_length=1, max_length=5000)


class PlatformScenarioConvertRequest(BaseModel):
    actor_id: str = Field(min_length=1, max_length=200)
    purpose: str = Field(min_length=1, max_length=5000)
    agent_type: str = Field(min_length=1, max_length=200)
    environment: str = Field(min_length=1, max_length=5000)
    variables: list[str] = Field(default_factory=list)
    metrics: list[str] = Field(default_factory=list)
    ethical_constraints: list[str] = Field(default_factory=list)


class PlatformKnowledgeCreateRequest(BaseModel):
    actor_id: str = Field(min_length=1, max_length=200)
    title: str = Field(min_length=1, max_length=500)
    content: str = Field(min_length=1, max_length=20000)
    source_type: str = Field(min_length=1, max_length=100)
    source_id: str = Field(min_length=1, max_length=200)
    linked_question_id: str | None = None
    linked_scenario_id: str | None = None
    linked_observation_id: str | None = None


# --- Unreal bridge (local-first MVP) ---
class AgentState(BaseModel):
    protocol_version: str = "roomzero.unreal.v1"
    agent_id: str
    emotion: str = "neutral"
    awareness: float = Field(default=0.5, ge=0.0, le=1.0)
    trust: float = Field(default=0.2, ge=0.0, le=1.0)
    is_speaking: bool = False
    is_observing: bool = True
    updated_at: str = Field(default_factory=utc_now_iso)


class AgentCommand(BaseModel):
    protocol_version: str = "roomzero.unreal.v1"
    type: Literal["command"] = "command"
    agent_id: str
    command: str
    text: str | None = None
    emotion: str | None = None
    animation: str | None = None
    duration_seconds: float | None = None


class ObservationEvent(BaseModel):
    protocol_version: str = "roomzero.unreal.v1"
    type: Literal["observation"] = "observation"
    agent_id: str
    event: str
    payload: dict[str, Any] = Field(default_factory=dict)
    created_at: str = Field(default_factory=utc_now_iso)


class SimulationEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid4()))
    event_type: str
    source: str
    payload: dict[str, Any] = Field(default_factory=dict)
    created_at: str = Field(default_factory=utc_now_iso)
    agent_id: str | None = None
    scenario_id: str | None = None
    simulation_id: str | None = None
    protocol_version: str | None = None
    status: str | None = None
    severity: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    # Additive M3 transport/lifecycle trace fields
    transport: str | None = None
    correlation_id: str | None = None
    parent_event_id: str | None = None
    trace_id: str | None = None
    schema_version: str = "roomzero.simulation-event.v1"


class SimulationEventTrace(BaseModel):
    event_id: str
    event_type: str
    source: str
    agent_id: str | None = None
    created_at: str
    status: str | None = None
    severity: str | None = None
    protocol_version: str | None = None
    schema_version: str = "roomzero.simulation-event.v1"
    payload_summary: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class SimulationEventReviewNoteCreateRequest(BaseModel):
    note_text: str = Field(min_length=1, max_length=2000)
    reviewer_id: str | None = Field(default=None, max_length=200)
    status: str | None = Field(default=None, max_length=100)


class SimulationEventReviewNoteModel(BaseModel):
    id: str
    event_id: str
    note_text: str
    reviewer_id: str
    status: str | None = None
    created_at: str
    updated_at: str


class SimulationEventReviewNotesResponse(BaseModel):
    count: int
    items: list[SimulationEventReviewNoteModel]


class SimulationEventReviewNoteUpdateRequest(BaseModel):
    status: str | None = Field(default=None, max_length=100)
    note_text: str | None = Field(default=None, max_length=2000)


class SimulationEventReviewAuditEntryModel(BaseModel):
    action: str
    created_at: str
    target_id: str
    details: dict[str, Any] = Field(default_factory=dict)


class SimulationEventReviewAuditResponse(BaseModel):
    count: int
    items: list[SimulationEventReviewAuditEntryModel]
