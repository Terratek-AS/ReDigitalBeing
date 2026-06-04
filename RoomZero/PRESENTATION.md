# RoomZero Presentation

## 1) First Page — Release Headline

**RoomZero: Persistent Digital-Being Research Platform (Phase 1 Release)**

RoomZero delivers a local-first, safety-aware foundation for persistent digital-being simulation.  
This release introduces **Eir**, the first digital being prototype with memory continuity, emotional state handling, and transparent governance workflows for research and testing.

Repository: https://github.com/Terratek-AS/ReDigitalBeing

## 2) Description (Release-Friendly)

RoomZero is built for teams exploring long-term, stateful AI interactions under controlled and ethical constraints.  
It combines:
- persistent memory and persona continuity
- structured tester/research workflows
- explicit safety boundaries
- practical local deployment via API, CLI, and Windows installer path

## 3) What’s Included

- Eir persona chat with memory/state continuity
- Research Network (testers, research queue, sources, feedback)
- Continuous research jobs (manual/local mode)
- Web UI dashboard for faster testing operations
- Windows installer pipeline (PyInstaller + Inno Setup)

## 4) Architecture Snapshot

- Backend: FastAPI (`app/main.py`)
- Modules: memory, persona, state, safety, llm, testers, research, feedback, sources, research_jobs
- Data store: JSON files under `data/`
- UI: static dashboard under `app/static/`
- CLI: `python -m app.cli`

## 5) Effective User Testing Flow

1. Create invite
2. Register tester
3. Chat with Eir
4. Submit research question/source
5. Run research jobs
6. Submit session feedback
7. Review stats and iterate

## 6) Install and Run

- Install:
  `.\install.ps1`
- Run:
  `.\run.ps1`
- Build installer:
  `.\install.ps1 -WithBuilder`
  `.\build_installer.ps1`

## 7) API and Console

- API docs: `/docs`
- UI dashboard: `/ui`
- Health: `/health`

## 8) Safety and Governance

- Explicit consent for tester onboarding
- Role-based tester permissions
- Reviewer-controlled approval pipelines
- Local-first data control and transparency
- MetaHuman may be used as a visual avatar/presentation layer only. MetaHuman assets, animation curves, rendered outputs, facial/motion data, or derived datasets must not be used to train, test, benchmark, evaluate, or enhance AI/ML/neural-network systems.
- MetaHuman license review is mandatory before commercial release, paid distribution, enterprise use, or public product launch.
- Unreal/MetaHuman visual presentation must remain strictly separated from RoomZero cognition, training, evaluation, simulation research datasets, and knowledge-base data.
- AI research/testing must use original data, user-owned data, synthetic data created independently of MetaHuman assets, or separately licensed datasets.

## 9) M4 Planning Outlook: Simulation Intelligence & Digital Human Layer (Planning-Only)

### M4 objective
- Provide a future roadmap for the **Simulation Intelligence & Digital Human Layer** without implementing runtime features in this cycle.
- Ensure M2/M3 architectural decisions remain compatible with future controlled simulation capabilities.

### What M4 is
- A planning framework for turning approved research scenarios into **controlled simulation runs**.
- A roadmap for repeatable, observable, auditable simulation operations.
- A governance model for agent behavior, cognition simulation, and ethical reasoning tests.
- A future visual-presentation layer plan using Unreal/MetaHuman only as avatar presentation.

### What M4 is not
- Not an implementation milestone in the current cycle.
- Not a bypass of M2.1.4 deployment ownership, M2.2 research MVP foundation, or M3 simulation event hardening.
- Not a claim of real consciousness.
- Not an AI/ML data rights expansion for Unreal/MetaHuman assets.

### M4 dependency position
- M2.1.4 must be resolved first (deployment ownership authority).
- M2.2 governance and review workflows must be stable.
- M3 event model must define simulation event transport and auditability.
- M4 starts only after those gates are satisfied.

### M4 roadmap pillars
- Simulation runtime roadmap (future)
- Agent profile roadmap (future)
- Memory state roadmap (future)
- Metrics and observation roadmap (future)
- Ethical simulation gate (future)
- Unreal/MetaHuman presentation layer (future)
- Future DB/API/UI planning artifacts (future)
- Testing/safety/licensing boundaries (future)

### Required safety and licensing boundaries
- Medium/high-risk scenarios require ethical approval and human oversight before execution.
- Harmful real-world operational simulation behavior must be blocked or flagged.
- Use language such as:
  - synthetic consciousness markers
  - consciousness-adjacent behavioral markers
  - agent behavior
  - cognition simulation
  - controlled simulation runs
- MetaHuman may only be used as visual avatar/presentation layer.
- MetaHuman assets, animation curves, rendered outputs, facial/motion data, or derived datasets must not be used for AI/ML training, testing, benchmarking, evaluation, or enhancement.
- RoomZero cognition/training/evaluation/simulation research datasets/knowledge-base data must remain separated from Unreal/MetaHuman assets.

## 10) Next Recommended Steps

### Immediate priority (before M4 implementation)
- Complete M2.1.4 deployment ownership path.
- Complete M2.2 research MVP hardening and governance acceptance.
- Complete M3 simulation event architecture baseline.

### Post-M4 planning milestone
- M4.1 Controlled Simulation Pilot:
  - approved low-risk scenarios only
  - repeatability/observability/auditability validation
  - ethical gate validation
  - Unreal/MetaHuman boundary-safe presentation validation

## 11) Repository

- GitHub: https://github.com/Terratek-AS/ReDigitalBeing

