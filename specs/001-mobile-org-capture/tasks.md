# Tasks: Captura móvil al inbox Org

**Input**: Design documents from `/specs/001-mobile-org-capture/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`,
`contracts/telegram-bot.md`, and `quickstart.md`

**Tests**: pytest tests are required by the feature specification and use synthetic fixtures only.

**Organization**: Tasks are grouped by user story so each increment can be tested independently.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel with other tasks in the same phase after its stated dependencies.
- **[USn]**: Identifies the user story served by the task.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize the Python project and reproducible local development environment.

- [ ] T001 Create Python 3.11 project metadata and uv dependency groups in `pyproject.toml`
- [ ] T002 Generate the committed resolved dependency lock in `uv.lock` from `pyproject.toml`
- [ ] T003 [P] Create the package skeleton and module exports in `src/captura_movil/__init__.py`
- [ ] T004 [P] Configure pytest test discovery and synthetic-fixture markers in `pyproject.toml`
- [ ] T005 [P] Add ignore rules for virtual environments, systemd environment files, queue data, Org data, and artifacts in `.gitignore`
- [ ] T006 [P] Create shared synthetic Telegram, filesystem, and time-zone fixtures in `tests/conftest.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Implement the local durability, configuration, and ingestion primitives required by all
user stories.

**⚠️ CRITICAL**: Complete this phase before beginning any user story.

- [ ] T007 Add a socket-blocking fixture for post-retention ingestion tests in `tests/conftest.py`
- [ ] T008 Write configuration validation tests for required environment values, IANA time zones, positive limits, and local paths in `tests/unit/test_settings.py`
- [ ] T009 Write atomic-publication and directory-fsync tests using temporary directories in `tests/unit/test_spool.py`
- [ ] T010 Write append-only Org rendering and durable-append failure tests in `tests/unit/test_org.py`
- [ ] T011 Write local ingestion retry, `pending/` to `done/` transition, offline isolation, and 100-capture failure-retention tests in `tests/integration/test_ingestion.py`
- [ ] T012 Implement validated environment settings, including `CAPTURE_SWEEP_INTERVAL`, in `src/captura_movil/settings.py`
- [ ] T013 Implement a reusable same-directory temporary-write, file-fsync, atomic-rename, and directory-fsync primitive in `src/captura_movil/atomic.py`
- [ ] T014 Implement immutable UTF-8 manifest publication, pending enumeration, and same-filesystem move to `done/` in `src/captura_movil/spool.py`
- [ ] T015 Implement TODO heading rendering with reception timestamps, verbatim body content, and abbreviation links in `src/captura_movil/org.py`
- [ ] T016 Implement local-only serialized pending sweeps, append-before-done ordering, and retry behavior in `src/captura_movil/ingest.py`
- [ ] T017 Implement capture and manifest value types with immutable receipt timestamp and artifact metadata in `src/captura_movil/capture.py`
- [ ] T018 Create the service entry point that runs startup and periodic serialized ingestion sweeps in `src/captura_movil/__main__.py`

**Checkpoint**: Configuration, durable queue, append-only inbox writer, and local retry path are
ready. No completed ingestion depends on network access.

---

## Phase 3: User Story 1 - Capturar una nota desde el teléfono (Priority: P1) 🎯 MVP

**Goal**: The authorized user sends text or a URL from Telegram and receives separate retained and
incorporated confirmations for a TODO heading in the Org inbox.

**Independent Test**: Send a synthetic authorized two-line update and verify the first line is the
TODO title, the rest is the exact body, receipt precedes incorporation, and an inbox-write failure
leaves the manifest pending without an incorporation confirmation.

### Tests for User Story 1

- [ ] T019 [P] [US1] Write text and URL normalization tests, including empty first line and verbatim link preservation, in `tests/unit/test_capture.py`
- [ ] T020 [P] [US1] Write authorized and unauthorized text-update contract tests in `tests/contract/test_telegram_bot.py`
- [ ] T021 [P] [US1] Write 100-capture end-to-end tests for retained-before-incorporated confirmation, title/body preservation, and inbox failure in `tests/integration/test_text_capture.py`

### Implementation for User Story 1

- [ ] T022 [US1] Implement title/body normalization and manifest construction for text updates in `src/captura_movil/capture.py`
- [ ] T023 [US1] Implement Telegram long-polling startup and chat-ID authorization before any update processing in `src/captura_movil/bot.py`
- [ ] T024 [US1] Implement retained receipt and post-ingestion incorporation notifications without blocking the local ingestion path in `src/captura_movil/bot.py`
- [ ] T025 [US1] Wire the bot polling lifecycle and local sweeper lifecycle into the service entry point in `src/captura_movil/__main__.py`

**Checkpoint**: An authorized text or URL capture becomes an append-only TODO heading without using
an editor or computer command. This is the MVP.

---

## Phase 4: User Story 2 - Capturar un adjunto (Priority: P2)

**Goal**: The authorized user sends a photo or document and the final TODO heading links to a
uniquely named artifact through the configured Org abbreviation.

**Independent Test**: Send synthetic photo and PDF updates with captions, verify the complete binary
is atomically published before its manifest, then verify the TODO heading contains an abbreviation
link. Test an over-limit attachment with a caption retains the text and records the rejected
attachment.

### Tests for User Story 2

- [ ] T026 [P] [US2] Write artifact filename normalization, uniqueness, abbreviation-link, and no-filename synthesis tests, including compressed photos without a Telegram filename, in `tests/unit/test_artifacts.py`
- [ ] T027 [P] [US2] Write 50-capture attachment publication-before-manifest and atomic failure tests in `tests/integration/test_attachment_capture.py`
- [ ] T028 [P] [US2] Write oversized attachment tests for rejection, caption retention, and heading notice in `tests/contract/test_telegram_attachments.py`

### Implementation for User Story 2

- [ ] T029 [US2] Implement attachment size preflight, normalized timestamp-prefixed names, and atomic artifact publication in `src/captura_movil/artifacts.py`
- [ ] T030 [US2] Extend capture manifests and Org heading rendering for published artifact links and rejected-attachment notices in `src/captura_movil/capture.py` and `src/captura_movil/org.py`
- [ ] T031 [US2] Handle authorized Telegram photos and documents by publishing the artifact before the referencing manifest in `src/captura_movil/bot.py`
- [ ] T032 [US2] Implement the oversized-attachment reply while retaining and queuing any accompanying text or caption in `src/captura_movil/bot.py`


**Checkpoint**: Photos and PDFs produce unique local artifacts and Org abbreviation links; an
oversized attachment never downloads but does not discard a valid accompanying note.

---

## Phase 5: User Story 3 - Consultar capturas pendientes (Priority: P3)

**Goal**: The authorized user can ask the bot for the current pending count and titles without any
database or external state.

**Independent Test**: Place three synthetic manifests in `pending/`, call `/pendientes` from the
authorized chat, and verify the count and all titles. Move one manifest to `done/` and verify the
next response reports two. Verify an unauthorized request does no work and receives no status.

### Tests for User Story 3

- [ ] T033 [P] [US3] Write pending manifest count and title extraction tests without persisted state in `tests/unit/test_spool.py`
- [ ] T034 [P] [US3] Write authorized and unauthorized `/pendientes` contract tests in `tests/contract/test_telegram_pending.py`
- [ ] T035 [P] [US3] Write pending-count transition integration tests after successful and failed ingestion in `tests/integration/test_pending_status.py`

### Implementation for User Story 3

- [ ] T036 [US3] Implement pending manifest count and title listing from `pending/*.txt` in `src/captura_movil/spool.py`
- [ ] T037 [US3] Implement the authorized `/pendientes` command and response formatting in `src/captura_movil/bot.py`

**Checkpoint**: The user can identify every locally retained but not incorporated capture from
Telegram, with no added persistent state.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Complete native deployment, operational safety, and end-to-end validation.

- [ ] T038 [P] Create the native restart-on-boot systemd unit with an external `EnvironmentFile` and absolute virtual-environment entry point in `deploy/captura-movil.service`
- [ ] T039 [P] Create a secret-free environment-file template with every required setting in `deploy/captura-movil.env.example`
- [ ] T040 [P] Write systemd unit and secret-exclusion tests in `tests/unit/test_systemd_unit.py`
- [ ] T041 Document uv installation, external secret setup, systemd enablement, and recovery procedure in `README.md`
- [ ] T042 Run all quickstart scenarios using synthetic fixtures and record any deviations in `specs/001-mobile-org-capture/quickstart.md`
- [ ] T043 Run the complete synthetic pytest suite and fix failures in `tests/`
- [ ] T044 [P] Document the Syncthing ignore pattern for temporary artifact files inside the Org artifact directory in `README.md`
- [ ] T045 [P] Document the required `org-link-abbrev-alist` entry on every Emacs machine so artifact links resolve in `README.md`
---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Starts immediately.
- **Foundational (Phase 2)**: Depends on T001-T006 and blocks all user stories.
- **US1 (Phase 3)**: Depends on T007-T018; provides the MVP.
- **US2 (Phase 4)**: Depends on the foundational phase and uses the established bot lifecycle from
  US1; it can be developed after T023 is stable.
- **US3 (Phase 5)**: Depends on the foundational phase and the authorized bot command routing from
  US1; it can be developed after T023 is stable.
- **Polish (Phase 6)**: Depends on the desired user stories being complete.

### User Story Dependencies

- **US1 (P1)**: No dependency on another user story after the foundational phase.
- **US2 (P2)**: Reuses US1's bot polling and authorization boundary but its artifact workflow is
  independently testable with synthetic updates.
- **US3 (P3)**: Reuses US1's bot polling and authorization boundary but its queue-derived status is
  independently testable with synthetic manifests.

### Within Each User Story

- Write and run test tasks before their implementation tasks.
- Preserve the atomic-write, authorization-before-processing, append-only, and offline-ingestion
  invariants in every implementation task.
- Complete the checkpoint before beginning the next story in a sequential implementation.

## Parallel Opportunities

- T003-T006 can run in parallel after T001.
- T008-T011 can be drafted after the fixture setup; T013 and test implementation can
  proceed in parallel once their interfaces are agreed.
- US1 test tasks T019-T021 can run in parallel.
- US2 test tasks T026-T028 can run in parallel.
- US3 test tasks T033-T035 can run in parallel.
- T038-T040 can run in parallel after the service entry point is stable.
- After T023, US2 and US3 can be assigned to separate developers.

## Parallel Example: User Story 2

```text
Task: "Write artifact filename normalization and abbreviation-link tests in tests/unit/test_artifacts.py"
Task: "Write attachment publication-before-manifest tests in tests/integration/test_attachment_capture.py"
Task: "Write oversized attachment contract tests in tests/contract/test_telegram_attachments.py"
```

## Implementation Strategy

### MVP First

1. Complete Phases 1 and 2.
2. Complete US1 through T025.
3. Validate the US1 independent test, including an interrupted inbox write.
4. Deploy the text-only bot for personal use before adding attachment and status features.

### Incremental Delivery

1. Add US2 to support binary artifacts and over-limit attachment behavior.
2. Add US3 to expose queue-derived pending status.
3. Complete Phase 6 and validate the systemd recovery path.

### Format Validation

All 45 tasks use the required checkbox, sequential task ID, optional parallel marker, story label
for story phases, and concrete file path.
