# Django API Backend Architecture and Engineering Roadmap

## Part 1 — Application goals, architecture, and current state

### Goal and success condition

A user submits one action, such as a map edit that must update both Cassandra and ArcGIS. The frontend needs one trustworthy answer even when those systems respond at different times. For this workflow, **Django may report completion only after it has evidence that both required changes took effect**. If a response is lost, the user needs an operation ID and a way to check progress without submitting the edit again.

### Application and system boundaries

The frontend renders pages. The API-only Django monolith handles REST requests, enforces permissions, performs inserts, updates, and deletes, coordinates external work, and reports outcomes. Background execution can continue after the HTTP response. Django remains responsible for explaining the operation to its caller.

| Participant | How it connects | Responsibility and boundary |
|---|---|---|
| Frontend | REST, plus an eventual SSE or WebSocket channel | Submits actions, shows status, and retrieves the latest result after reconnecting. |
| Django | Inbound HTTP, outbound clients, database drivers, and messaging | Owns workflow rules, authorization, user-visible status, and recovery decisions. |
| Cassandra | Database driver | Supplies application reads from `cleaned_01`. Identify the permitted write target and owner for each mutation. Raw ingestion keyspaces are outside this backend’s responsibility. |
| ArcGIS Server | REST API | Applies GIS changes and owns writes to its managed PostgreSQL data. Django depends on evidence the specific ArcGIS operation exposes. |
| Elasticsearch | Client or API | Supports indexed-document operations and search. Each workflow decides whether indexing must finish before it reports success. |
| HDFS | Filesystem client or API | Stores and retrieves files. Django owns application-level access checks and the result it reports for a transfer. |
| Oracle visualization service | REST API | Supplies visualization operations. The exact Oracle product and endpoint contracts remain open. |
| Spark and external processing services | Job submission or service-specific API | Run longer work. The integration needs a way to correlate submission, remote job identity, and eventual result. |
| External REST worker, provisionally “IntelliU Worker” | REST API | Accepts processing requests. Its final name, completion contract, and relationship to the broker consumer remain open. |
| Broker and consuming worker | RabbitMQ or Kafka, choice open | Carry and process background tasks. Publishing, execution, result recording, and frontend notification are separate events. |

### Synchronous example — one edit across two systems

1. Django authorizes the user, validates the edit, and checks that both required systems are enabled. It associates the request with a stable operation ID.
2. Before the first side effect, Django durably records the intended operation and the identifiers recovery will need. It attempts the Cassandra change.
3. After confirming Cassandra applied the change, Django calls ArcGIS. It records what the response establishes for the specific edit. A remote job ID means the backend has more work to track.
4. Django uses the evidence below to determine what the user sees and what recovery may safely do.

| Evidence available to Django | User-visible outcome | Next action |
|---|---|---|
| Both required writes are confirmed | Completed | Return or expose the result and relevant resource IDs. |
| The first write was definitively rejected before taking effect | Failed | Record the rejection and end the workflow. |
| Either write may have taken effect, but its reply was lost | Outcome unknown | Reconcile that step. Preserve the operation ID and avoid an unsafe repeat or reversal. |
| Cassandra succeeded and ArcGIS definitively rejected the edit before applying it | Compensation pending | Apply the defined compensating action for the Cassandra change. |
| Cassandra compensation is confirmed | Compensated | Explain that the requested edit failed and the earlier change was reversed. |
| Compensation failed or its reply was lost | Recovery outstanding | Record the failure or uncertainty about compensation. Check the current state before another attempt. |
| Django restarted between an external effect and its local confirmation | Status may still show processing | Resume from durable intent and check the system that owns the effect before advancing. |

Compensation is a new business operation. Undoing a create might remove a record created specifically by this request. Undoing an update may require previous values and a version check so recovery preserves a colleague’s later edit. If an ArcGIS request changes several items, record the evidence for each required item before deciding whether any reversal is safe.

### Asynchronous example — one processing job

1. Django authorizes the request and durably records the job, its owner, and the intent to dispatch it. It returns `202 Accepted` with an identifier and a way to retrieve status.
2. Dispatch sends the task to the broker or external service according to the chosen workflow. A publication error leaves discoverable work to retry.
3. A worker executes the task. Django associates verified results with the same job and exposes the recorded status to its owner. The mechanism for returning results remains open.
4. Django can notify the frontend after recording the result. If a notification is missed, the client retrieves the current result by ID. A completed job remains completed even while the client is offline.

### State vocabulary and current implementation status

**Accepted** means Django has durably taken responsibility. **Processing** means execution is underway. **Completed** means the workflow’s success condition was verified. **Failed** means definitive failure with no outstanding reversal. **Outcome unknown** means a required effect is uncertain. **Compensation pending** and **Compensated** distinguish outstanding recovery from a verified reversal. These are proposed meanings. The final names, persistence model, and status API are open.

The agreed design includes configuration-first development, early debugging, a class-based low-level design where useful, and staged delivery. **Implementation progress is unverified.** This roadmap records intended behavior. Mark a phase complete when its completion criteria have been demonstrated.

## Part 2 — Engineering roadmap in 16 phases

Build the smallest usable workflow in each phase. **Basic** means the minimum safe behavior for that feature. **Intermediate** covers coordination across requests, systems, or failures. **Advanced** covers operational scale and automation justified by demand. A later phase can move forward when a product feature depends on it. For example, ship bounded streaming with the first large-file endpoint, regardless of its place in this sequence.

### Phase 1 — Project setup and configuration management

#### Goal and reason for this phase

Make a fresh local environment start the API predictably. This is the first development milestone because every later feature depends on knowing which settings are in effect.

#### Prerequisites

Identify the supported environments and who controls their configuration and secrets. The first local startup needs no live external systems.

#### Scope and implementation depth

**Basic.** Establish a repeatable project startup, environment selection, file precedence, defaults, secret references, and startup validation. Document which settings are required for each enabled feature.

#### Configuration and feature behavior

Load and validate settings in one place. Give feature flags explicit defaults and provide each caller only the settings it needs. If authentication bypass is allowed for isolated local development, reject that combination in any shared environment.

#### Design and ownership

The configuration component owns parsing and validation. Feature owners define the meaning of their settings. A feature flag can control availability. The workflow still owns its success condition.

#### Security, correctness, and failure handling

Fail startup on an invalid required value and identify the setting without revealing its secret. Keep real credentials out of ordinary configuration files. A temporary dependency outage belongs to runtime health reporting.

#### Completion criteria

A developer can start Django with the documented local settings. A missing credential for an enabled integration and a shared environment with authentication bypass both produce clear startup errors.

#### What can wait

Live reload, a flag-management interface, and configuration for integrations with no current caller.

### Phase 2 — Local logging and debugging

#### Goal and reason for this phase

Make startup and runtime failures understandable to the developer who encounters them. Establish this before business logic makes failures harder to isolate.

#### Prerequisites

Phase 1 provides the environment identity, validated settings, and a reliable startup path.

#### Scope and implementation depth

**Basic.** Establish structured application and error logs, log levels, local exception details, and lookup by identifier. Add access logs and request IDs when the first route exists.

#### Configuration and feature behavior

Allow environment-specific verbosity. Keep detailed exception output local and redact sensitive values at every level, including debug.

#### Design and ownership

The logging setup owns formatting and redaction. Each component records facts it knows. The ArcGIS client can record a timeout while the workflow records the resulting operation state.

#### Security, correctness, and failure handling

Exclude credentials, tokens, and sensitive payloads. Keep untrusted text within its structured field so input cannot forge a separate log entry. Define basic log access and rotation before retaining shared logs.

#### Completion criteria

Trigger a startup error and find its cause from one log record. Exercise a message containing a token and a newline and verify that the token stays hidden and the message remains one event.

#### What can wait

Centralized shipping, analytics, dashboards, and always-on profiling.

### Phase 3 — Development checks and automated testing

#### Goal and reason for this phase

Make basic quality and safety checks repeatable while the application is still small.

#### Prerequisites

A runnable project and deterministic local settings. Early configuration and diagnostic behavior supply real cases to test.

#### Scope and implementation depth

**Basic.** Agree on naming, formatting, linting, and a test command. Run these in continuous integration. Add targeted type checks around settings and workflow results as those boundaries appear.

#### Configuration and feature behavior

Give tests an isolated configuration. Keep tests that require live dependencies identifiable so an ordinary test run cannot modify shared data.

#### Design and ownership

Put a new test with the behavior it protects. Review names for meaning, keep methods focused, and extract common behavior when multiple callers need the same decision.

#### Security, correctness, and failure handling

Start with valid and unsafe configuration combinations. Each later feature brings its failure cases into the same checks before release.

#### Completion criteria

A fresh checkout runs the same checks locally and in CI. An intentionally unsafe settings change fails the relevant test and identifies the broken rule.

#### What can wait

Broad coverage targets and exhaustive end-to-end suites. Add coverage reporting when it helps identify untested decisions.

### Phase 4 — Basic low-level design and policy ownership

#### Goal and reason for this phase

Trace the first use case before writing its endpoint. Decide who accepts inputs, who makes the business decision, and who talks to another system.

#### Prerequisites

A specific user action, its expected result, and the information the caller may receive. Design just the participants that action requires.

#### Scope and implementation depth

**Basic.** Identify each object’s inputs, outputs, dependencies, and failure cases. For a map edit, the HTTP handler calls the workflow object. The workflow calls the Cassandra repository and ArcGIS client, then determines the combined result.

#### Configuration and feature behavior

The workflow can use a shared Boolean check such as `is_arcgis_enabled()` to determine availability. A richer result carries confirmed success, rejection, pending work, or uncertainty after an actual call.

#### Design and ownership

The handler owns HTTP translation. The workflow owns the completion rule. Each client owns its protocol and interprets its own evidence. A recovery job can call the same workflow policy. Keep a short single-purpose predicate near the feature that owns it.

#### Security, correctness, and failure handling

Specify which evidence permits each state change. The caller should be able to tell the difference between an enabled feature, a reachable service, and a successfully applied edit.

#### Completion criteria

Walk through a successful edit and a lost ArcGIS response. For every decision, identify the responsible object and what evidence it receives. Both the API and future recovery path reach the same conclusion from the same evidence.

#### What can wait

A base class for every client, a generic orchestration framework, or a global collection of unrelated Boolean helpers.

### Phase 5 — First REST endpoint and API contract

#### Goal and reason for this phase

Deliver one local request from routing to a predictable response. This makes the design observable before adding real data dependencies.

#### Prerequisites

Phases 1–4 provide settings, diagnostics, repeatable checks, and a first use case.

#### Scope and implementation depth

**Basic.** Define request, success, and error schemas. Establish request context, middleware order, validation, serialization, response headers, and cleanup. Document one valid request and one failure. Add page bounds and allowed sort fields with the first collection route.

#### Configuration and feature behavior

Configure request-size limits and safe error verbosity. API field meanings and required response fields are part of the contract.

#### Design and ownership

The boundary validates shape and normalizes inputs where appropriate. The workflow validates business rules. Central error mapping keeps equivalent failures consistent across routes.

#### Security, correctness, and failure handling

Reject unsupported types, ranges, and oversized inputs before calling downstream code. Apply output encoding where the output context requires it. Keep diagnostic details out of public errors.

#### Completion criteria

Trace a valid and an invalid request by request ID. Verify documented status codes and response bodies, and show that invalid input causes no downstream call.

#### What can wait

A full API catalog and formal deprecation machinery. Establish a versioning and compatibility policy before independent clients rely on a released contract.

### Phase 6 — Authentication, authorization, and audit

#### Goal and reason for this phase

Protect the first shared environment and establish who may perform each action on each resource.

#### Prerequisites

The first API contract and a definition of actors, resource ownership, and protected actions.

#### Scope and implementation depth

**Basic, required before shared access.** Authenticate users and service callers. Enforce action and object permissions, throttle login attempts, and audit login outcomes, lockouts, and permission changes. Hash passwords if Django owns credentials.

#### Configuration and feature behavior

Set expiry, throttling, lockout, and trusted identities through validated settings. Choose the safeguards appropriate to the actual login mechanism. Cookie sessions need secure cookie and CSRF controls. A JWT flow needs signature and claim checks plus explicit expiry, refresh, and revocation behavior where issued.

#### Design and ownership

Authentication identifies the caller. Authorization decides access at each entry point. The audit record identifies actor, action, resource, time, and outcome. Define audit access and retention from the first shared deployment.

#### Security, correctness, and failure handling

Use TLS with certificate verification on protected network connections. Give downstream service accounts the smallest required permissions. Cover renewal, logout, and invalidation for the credential mechanism selected.

#### Completion criteria

An unauthenticated request is rejected. A signed-in user cannot change another user’s protected resource. Repeated failed logins trigger the configured policy and leave a usable audit record.

#### What can wait

Complex role hierarchies and delegated access until a workflow needs them. Controlled access and encryption for sensitive data become requirements before that data is introduced.

### Phase 7 — First Cassandra read

#### Goal and reason for this phase

Read one supported application query from `cleaned_01` and return an authorized, bounded result.

#### Prerequisites

A permitted query, known keyspace and table ownership, an API contract, and credentials scoped to the read.

#### Scope and implementation depth

**Basic.** Configure a reusable driver client with bounded connections, query deadlines, and cleanup. Use parameterized CQL for values. Allowlist dynamic fields and cap result size. Provide a bounded dependency check with last-checked time.

#### Configuration and feature behavior

Validate contact points, keyspace, credential references, pool limits, and timeouts. An unavailable read feature should produce an explicit response.

#### Design and ownership

The repository owns the query and client lifecycle, including safe creation per process where required. The workflow interprets a missing record. The API translates the result.

#### Security, correctness, and failure handling

Distinguish empty results, rejected access, deadline expiry, and an unavailable dependency. Keep dependency failure separate from process liveness so a Cassandra outage does not trigger a restart loop.

#### Completion criteria

Verify an allowed read, an empty result, an invalid filter, and a simulated outage. After connectivity returns, verify the client reconnects and the route can serve reads again.

#### What can wait

Broad repository abstractions, speculative indexes, and pool tuning beyond safe initial limits.

### Phase 8 — First Cassandra write and recovery basics

#### Goal and reason for this phase

Make one mutation safe to submit and investigate before adding a second writer.

#### Prerequisites

Confirm the writable target and its owner separately from permission to read `cleaned_01`. Specify the business key, caller permissions, and success evidence.

#### Scope and implementation depth

**Basic write support with required recovery safeguards.** Define create, update, or delete semantics for one operation. Associate retried requests with the same logical operation, detect conflicting reuse, and record its audit outcome. Establish repeatable reference seeds where the workflow needs them.

#### Configuration and feature behavior

Configure deadlines, size limits, and bounded retry behavior. Account for driver retries in the overall attempt budget. Set datastore backup and retention rules before accepting valuable data.

#### Design and ownership

The repository performs the mutation and reports its evidence. The workflow owns idempotency and the meaning of a conflicting update. The datastore owner verifies backup and restore.

#### Security, correctness, and failure handling

A write timeout can leave an applied change. Provide a reliable lookup or a manual recovery route. For concurrent updates, define how to detect a stale edit. Scope idempotency keys to the authorized caller and action.

#### Completion criteria

Repeat the same request, including concurrent submissions, and verify one intended business effect. Lose the reply after a successful write and demonstrate how to establish or report its outcome. Restore representative data before relying on recovery.

#### What can wait

Point-in-time recovery beyond the agreed recovery target, broader mutation support, and tuning based on future traffic.

### Phase 9 — First ArcGIS REST operation

#### Goal and reason for this phase

Learn exactly what the selected ArcGIS endpoint can establish about a map edit before coordinating it with Cassandra.

#### Prerequisites

A representative edit, endpoint access, credentials with the required permissions, and a safe integration environment.

#### Scope and implementation depth

**Basic client with intermediate outcome handling.** Define method, headers, payload mapping, expected response fields, and application-level errors. Distinguish completed edits, pending jobs, explicit rejection, and unknown outcomes. Capture remote IDs or status URLs when supplied.

#### Configuration and feature behavior

Set endpoint, credentials, TLS verification, connection and response timeouts, overall deadline, and pool limits. A retry policy must match this operation’s replay guarantees.

#### Design and ownership

The client translates the remote response into evidence about this edit. The workflow interprets that evidence in context. Django accesses ArcGIS-managed PostgreSQL through ArcGIS REST.

#### Security, correctness, and failure handling

An HTTP success response may contain an item-level failure. A malformed reply, timeout, or lost connection can leave an uncertain write. Document which lookup, if any, can reliably resolve it.

#### Completion criteria

Using real responses or verified fixtures, identify a confirmed edit, a rejected edit, and an ambiguous response. Where the endpoint offers a job ID or per-item results, demonstrate how to use them.

#### What can wait

A general-purpose ArcGIS wrapper, additional endpoints, and automatic replay of ambiguous writes without established replay safety.

### Phase 10 — Cassandra–ArcGIS coordination and recovery

#### Goal and reason for this phase

Deliver the first user action whose success requires two confirmed writes. Its failure and recovery behavior is part of the first release of that action.

#### Prerequisites

Phases 8 and 9 supply the evidence each system can provide. Choose durable tracking, operation identity, recovery access, and a compensation rule for this specific edit.

#### Scope and implementation depth

**Intermediate and required.** Record intent before effects. Track step attempts, confirmed results, remote IDs, and compensation. Make status available by operation ID. Start with a documented manual path wherever evidence cannot support safe automation.

#### Configuration and feature behavior

Check required feature availability before the first write. A flag turned off later should block new work while preserving status and a controlled path for operations already in progress. Keep the policy governing an accepted operation identifiable through recovery.

#### Design and ownership

The workflow coordinates Cassandra first and ArcGIS second. Each client reports local evidence. Recovery uses the same completion policy as the request handler. Protect transitions against two workers or a client retry advancing the same operation twice.

#### Security, correctness, and failure handling

On definitive ArcGIS rejection, compensate only the Cassandra effect owned by this request. Check before overwriting later edits. On uncertain ArcGIS outcome, reconcile before retry or reversal. A failed or uncertain compensation remains recoverable.

#### Completion criteria

Exercise both-success, confirmed rejection, lost response, crash after either write, concurrent edit, and failed compensation. Given one ID, an operator can identify confirmed effects, unresolved effects, and the next safe action.

#### What can wait

A reusable Saga engine and fully automatic reconciliation. Bring the scheduled recovery work from Phase 13 forward if resolution must happen without operator intervention.

### Phase 11 — Additional integrations by product need

#### Goal and reason for this phase

Support the next user workflow that actually needs search, file storage, visualization, or another external system. Integrate one dependency at a time.

#### Prerequisites

A named product workflow, authorized data sources, and an explicit decision about which downstream results are required for success.

#### Scope and implementation depth

**Basic per integration.** For Elasticsearch, define search or index-update semantics. For HDFS, define permitted file operations and ownership. For Oracle visualizations, define the REST request and expected result. Apply the client lifecycle and error rules established earlier.

#### Configuration and feature behavior

Each enabled integration has its own endpoint, credentials, timeouts, quotas, and feature settings. Define any degraded behavior in the API contract, including how stale or partial results are identified.

#### Design and ownership

Each client owns protocol details and connection cleanup. The workflow owns the decision to proceed when an optional dependency is unavailable. Parameterize queries wherever a directly used database driver supports them.

#### Security, correctness, and failure handling

Validate identifiers, paths, and query fields at the relevant boundary. Honor downstream rate-limit signals within the caller’s deadline. If a required publication or index update is deferred, record the outstanding work and provide a recovery path.

#### Completion criteria

Disable or interrupt one dependency and verify the user sees the promised behavior. For an optional search index, verify that a pending index update can be found and completed once search recovers.

#### What can wait

Integrations without a committed workflow. Large-file safeguards from Phase 15 move here if the first HDFS feature handles large transfers.

### Phase 12 — Background jobs and durable messaging

#### Goal and reason for this phase

Allow the frontend to leave a long-running task and come back to a reliable result.

#### Prerequisites

A job owner, stable ID, persistent status and result contract, and a decision on how to dispatch each job and receive evidence of completion.

#### Scope and implementation depth

**Intermediate.** Make the job and intent to dispatch recoverable together before returning `202 Accepted`. For broker-backed jobs, define message schema, routing, publish confirmation, and consumer acknowledgments or offset commits. For a REST worker or Spark, record the remote job ID and track execution through the supported interface.

#### Configuration and feature behavior

Configure destinations, service identities, deadlines, concurrency, and retry limits. Set a policy for exhausted attempts and controlled replay. Disabling new submissions should leave outstanding jobs discoverable.

#### Design and ownership

Django owns application job status. The dispatcher owns delivery attempts. The worker owns execution and durable progress at its boundary. A single application job can have several delivery attempts.

#### Security, correctness, and failure handling

Expect redelivery when a worker finishes an effect and crashes before acknowledging it. Deduplicate or reconcile at the effect boundary. Persist enough evidence before acknowledging. Authenticate callbacks or poll an authorized status endpoint. Protect result access by job ownership.

#### Completion criteria

Stop the broker after acceptance and verify the job can still be dispatched. Crash a worker after its effect and verify redelivery cannot duplicate it. Restart Django and retrieve the saved job result as the authorized user.

#### What can wait

Fine-grained progress percentages, complex routing, and a replay interface. Start with inspectable failed work and a safe procedure for handling it.

### Phase 13 — Scheduled tasks and reconciliation

#### Goal and reason for this phase

Run recurring work such as revisiting unresolved operations. Move this phase earlier if automatic reconciliation is a release requirement for Phase 10.

#### Prerequisites

An identifiable unit of work, a safe way to repeat it, and a defined owner for failures that need human attention.

#### Scope and implementation depth

**Basic scheduling with intermediate duplicate protection.** Specify frequency, run identity, missed-run policy, and overlap behavior. Make the last attempt and its result visible.

#### Configuration and feature behavior

Configure schedule, time zone, batch size, maximum concurrency, and retry budget. Allow pausing new runs while retaining the backlog and current status.

#### Design and ownership

The scheduler decides when a run is due. The existing workflow decides what recovery action is valid for each operation. A management command can expose the same behavior to an authorized operator.

#### Security, correctness, and failure handling

Two scheduler instances can discover the same operation. Coordinate ownership and make each action safe under retry. Send unresolved cases for manual review when available evidence is insufficient.

#### Completion criteria

Simulate a missed interval and an overlapping run. Demonstrate that eligible work is eventually revisited and protected business effects occur once.

#### What can wait

Complex calendars, general scheduling interfaces, and automation for cases without reliable outcome evidence.

### Phase 14 — Real-time frontend updates

#### Goal and reason for this phase

Tell an authorized user that a recorded operation has changed while preserving the ability to retrieve the result after disconnecting.

#### Prerequisites

An authorized status endpoint, durable results, and a stable operation or job ID. Decide whether the product needs one-way updates or two-way messages.

#### Scope and implementation depth

**Basic.** Use SSE for a one-way use case or WebSockets if the feature needs two-way communication. Include the affected ID and a way to recover the latest state. Support reconnection and disconnect cleanup.

#### Configuration and feature behavior

Set connection and idle limits, keepalive behavior, and bounded buffering. If push is disabled, keep the status lookup usable.

#### Design and ownership

The job or workflow owner records the result first. The notification component routes the event to authorized subscribers. The frontend refreshes status when it reconnects or receives an ambiguous update.

#### Security, correctness, and failure handling

Authorize subscription to each resource, validate inbound messages where applicable, and handle permission expiry. Disconnect or resynchronize slow clients before buffers grow without bound.

#### Completion criteria

Disconnect before completion and reconnect as the same user. Recover the correct result. Verify that another user cannot subscribe to that job and that a slow client does not exhaust server memory.

#### What can wait

Event replay if latest-state recovery meets the product need. Add replay if the client must reconstruct every transition.

### Phase 15 — Large-file and media streaming

#### Goal and reason for this phase

Support the first upload or download too large to hold safely in memory. Move this phase forward with that feature.

#### Prerequisites

Known file ownership, size and access policies, a storage integration, and a product decision about interrupted transfers.

#### Scope and implementation depth

**Basic.** Stream bounded chunks, enforce size and type limits, and stop unnecessary work on disconnect. For uploads, define when a file is complete and what happens to partial content.

#### Configuration and feature behavior

Configure maximum object size, chunk and buffer bounds, concurrent transfers, and deadlines. Establish separate limits for expensive media endpoints.

#### Design and ownership

The API enforces resource permissions. The storage client handles bounded reads and writes. The workflow decides when a file becomes visible and owns partial-file cleanup.

#### Security, correctness, and failure handling

Validate paths and file types, including attempts to access another user’s files. Bound total memory across concurrent transfers. Keep incomplete uploads distinguishable from finished files.

#### Completion criteria

Transfer a representative large file, cancel midway, and verify bounded memory and resource cleanup. A partial upload must not appear as a completed file. Test forbidden paths and oversized payloads.

#### What can wait

Range requests when seeking is required, resumable uploads when restarting is too costly, and additional media delivery optimization after measurement.

### Phase 16 — Production readiness and operational verification

#### Goal and reason for this phase

Demonstrate that people can operate, recover, and safely shut down the deployed application under realistic conditions.

#### Prerequisites

Representative workflows, verified failure cases from earlier phases, expected traffic, and agreed availability and recovery objectives.

#### Scope and implementation depth

**Intermediate across the application, advanced where measured.** Separate startup, liveness, and readiness checks. Ship and protect logs, track rates, errors, latency, queue age, and unresolved operations. Set external uptime probes and actionable alerts. Drain traffic, stop intake, finish or preserve in-flight work, and flush telemetry on shutdown.

#### Configuration and feature behavior

Set probe timeouts, drain deadlines, log and audit retention, concurrency budgets, backup schedules, and alert thresholds. Exercise credential, token-signing key, encryption key, and certificate rotation as applicable.

#### Design and ownership

Operations owns alerts and recovery procedures. Each client owns pool cleanup. Workers acknowledge completed work and checkpoint where supported. Datastore owners restore their data. Workflow owners reconcile cross-system differences after restore.

#### Security, correctness, and failure handling

Verify encryption at rest and controlled decryption for protected data. Test recovery to an agreed point in time where supported. Give operators restricted access to logs, audit records, and replay actions. An optional dependency outage should affect only the work that depends on it.

#### Completion criteria

Run load, rate-limit, shutdown, and restore drills. Trace one lost ArcGIS response and one interrupted job by ID. Measure recovery against the agreed objectives and verify frontend status matches the recovered business state.

#### What can wait

Advanced trace sampling, more infrastructure, and performance tuning without an observed bottleneck. Bring any operational safeguard forward when a real release already depends on it.

## Part 3 — Coverage, operating rules, and open decisions

### Coverage of the 27 engineering concerns

Phase numbers show when each subtask becomes useful. Later depth is conditional on the actual feature, data sensitivity, and operating requirements. For example, a verified restore belongs before valuable writes even if the full recovery drill comes in Phase 16.

| # | Engineering concern | First required capability | Later depth or trigger |
|---|---|---|---|
| 1 | Configuration management | P1 — environment files, precedence, flags, defaults, and startup validation | Every phase — introduce and validate the relevant connection, feature, timeout, or limit settings. |
| 2 | Secrets management and encryption | P1 — secret references and controlled access. P6 or first protected connection — password hashing if applicable, TLS, and certificate verification | P8 or first sensitive storage — encryption at rest and controlled decryption. P16 — exercise key, certificate, and credential rotation. |
| 3 | Authentication and user sessions | P6 — user/service identity, login throttling, lockouts, and selected session or token protections | P6 before release of that login method — cookie and CSRF controls, renewal and invalidation, or JWT signing, claim checks, expiry, refresh rotation and revocation as applicable. P16 — rotation drills. |
| 4 | Authorization | P6 — roles, least privilege, action and resource checks | P7–12 — service accounts, delegated access where required, files and jobs. P14–15 — authorize each subscription or transfer. |
| 5 | HTTP request–response lifecycle | P5 — routing, middleware order, context, validation, handlers, serialization, headers, and cleanup | P6 — authentication and permission checks. P14–16 — long-lived requests and graceful termination. |
| 6 | Input validation and injection prevention | P5 — type, schema, range, length, normalization and context-specific encoding | P7–11 — parameterized CQL or SQL where used and allowed fields, filters, and sorts. P14–15 — message, file type, size, and path checks. |
| 7 | API contracts, versioning, and documentation | P5 — request, result, error examples, and bounded collections | Before dependent client releases — publish an OpenAPI contract, compatibility and deprecation policy. P10–15 — document status, job, event, and transfer contracts. |
| 8 | External service integrations | P7–10 — Cassandra reads and authorized writes, then ArcGIS REST | P11 — HDFS, Elasticsearch, Oracle REST and other APIs as required. P12 — Spark and external worker submissions. |
| 9 | Outbound API requests and responses | P9 — method, credentials, payload validation, application errors, malformed replies, and outcome classification | P10–12 — persist remote resource IDs, job IDs and status links, reconcile pending or unknown outcomes. |
| 10 | Outbound clients, sessions, and connection pools | P7 and P9 — service-specific clients, reuse, bounded pools, timeouts and cleanup | P12 and P16 — process/worker ownership, stale connection recovery, shutdown and measured pool tuning. |
| 11 | Error handling and dependency outages | P5 — predictable errors. P7 — empty result versus outage | P9–11 — required/optional dependencies, partial results, recovery on restoration. P16 — alerts for prolonged degradation. |
| 12 | Timeouts, retries, and idempotency | P7–9 — connection, response and total budgets, stable mutation identity, lost-response lookup | P10–13 — coordinate driver and application attempts. Use limited backoff with jitter for safe retries and respect downstream deadlines. |
| 13 | Data ownership and cross-system consistency | P4 and P8 — assign policy ownership and establish the writable record and identity | P9–10 — map local and remote IDs, record ordered steps, detect partial effects, compensate or reconcile. P16 — reconciliation after restore. |
| 14 | Rate limiting and resource protection | P5 — size and page limits. P6 — login and client throttling | P7–12 — per-user, per-client and endpoint budgets, downstream quotas, `Retry-After`, concurrency. P14–16 — stream backpressure and load verification. |
| 15 | Message broker publishing and consumption | P12 — routing, schema, publish confirmation, acknowledgments or offset commits and idempotent consumers | P12 before relying on redelivery — bounded retries and handling of exhausted messages. P16 — dead-letter inspection and controlled replay drills. |
| 16 | Background jobs and scheduled tasks | P12 — job ownership, submission, persistent status, polling or verified callbacks and result retrieval | P13 — cron or scheduled maintenance, missed and overlapping runs. P16 — restart and recovery drills. |
| 17 | Client notifications and real-time communication | P14 — authorized SSE or WebSocket channel, message validation, reconnection, slow-client handling and cleanup | P14 onward — replay when every transition matters. P16 — verify behavior during shutdown and at load. |
| 18 | Streaming APIs and large media | P15, or the first large-file feature — bounded chunked transfers, cancellation, and media access controls | Range requests for seeking and resumable transfers where needed. P16 — measure memory and concurrency under load. |
| 19 | Health checks and uptime monitoring | P1 — startup checks. P7 — bounded dependency checks for connectivity, credentials and access | At first deployment — liveness, readiness and external uptime checks. P16 — availability alerts, last-checked times and outage drills. |
| 20 | Graceful shutdown | P7–9 — release clients. P12 — stop intake and acknowledge completed work | P14–16 — drain requests, close streams, checkpoint jobs where supported, honor deadlines and flush telemetry. |
| 21 | Application logging and log management | P2 and P5 — structured application, error, and access logs, levels, request IDs, redaction and injection prevention | P10 and P12 — operation and job IDs. P16 — shipping, search, analytics, retention and restricted access. |
| 22 | Audit logging | P6 — login attempts, lockouts, role changes, actor, resource, timestamp and outcome | P8–10 — create, update, delete and compensation records. Protect integrity and restrict writers from the first retained audit. P16 — verify retention and retrieval. |
| 23 | Observability and error tracking | P2 and P5 — local exception capture, stack traces, request timing and correlation | P9–16 — error grouping, dependency and pool metrics, broker/job metrics, trace propagation, dashboards and alerts. |
| 24 | Shared utilities and debugging helpers | P2 and P4 — diagnostic lookup and clear ownership for shared decisions | P5–13 — reuse validation, pagination, client and error mapping logic where callers share semantics. Add diagnostic commands, request inspection, and profiling for observed problems. |
| 25 | Seed data, backups, and recovery | P7–8 — repeatable environment-specific seeds and migrations where relevant. Verify backups and a restore before valuable writes | P11 and P16 — define retention per store, point-in-time recovery where supported, restore dependencies and reconcile systems. |
| 26 | Testing and failure verification | P3–6 — unit, API contract, validation and access-control tests | P7–15 — integration and end-to-end tests for outages, timeouts, lost replies, duplicates, partial writes, disconnects and shutdown. P16 — load, rate-limit and recovery drills. |
| 27 | Code quality | P3 — naming, formatting, linting, automated checks and targeted type checking | P4 onward — review ownership and contracts. Expand static typing and coverage reporting around business decisions and recovery branches. |

### Identifiers used during an investigation

| Identifier | Lifetime and purpose |
|---|---|
| Request ID | One HTTP attempt. A retry can have a different request ID while referring to the same operation. |
| Idempotency key | Identifies a caller’s repeat submission of the same intended action. Define its scope, validity period, and response to a different payload using the same key. |
| Operation ID | One logical business action. Links step records, retries, compensation, and the user-visible result. |
| Job ID | One accepted background job. It can serve as the operation ID when the relationship is one-to-one. Record remote job or resource IDs separately. |

The durable operation record answers **what work is outstanding**. An audit record answers **who acted on which resource and with what outcome**. Diagnostic logs explain **what the application observed during an attempt**. Give each record an owner and correlate them by ID. Recovery must remain possible after diagnostic logs rotate.

### Decisions to close before the affected feature ships

| Decision | When it must be settled | Evidence or agreement needed |
|---|---|---|
| Which data may Django mutate? | P8 | Named Cassandra target, business key, ownership, concurrency rule, and recovery objective. |
| What does ArcGIS confirm for the selected edit? | P9 | Example accepted, rejected, partial, and ambiguous outcomes where applicable. Verify whether a stable identifier, authoritative lookup, or safe repeat exists. |
| What proves success and what may remain pending? | P10 for the dual write, then per workflow | Agreement on required systems, acceptable temporary differences, user-visible wording, and how clients retrieve an updated result. |
| Where are operation state and compensation details stored? | P10 | Evidence that intent survives crashes, competing attempts cannot overwrite progress, and recovery can find unresolved work. Define how long records and previous values are retained. |
| How is each mutation compensated and who handles uncertainty? | P10 | Per-action reversal rules, concurrency checks, permission to perform recovery, an owner for manual cases, and a target time to investigate. |
| Which additional systems does the next product feature actually need? | P11 or first dependent feature | Oracle product and API contract, required HDFS or search behavior, and permission boundaries. |
| Which broker, worker, and result channel serve each job? | P12 | RabbitMQ or Kafka decision, identity of the REST and broker workers, correlation with Spark or remote jobs, and polling or verified callback contract. |
| Which notification and transfer capabilities do users need? | P14–15 or first dependent feature | One-way or two-way communication, latest status or every event, maximum file sizes, seeking needs, and interruption cost. |
| What operational targets are acceptable? | Before the first deployment carrying real data or users | Agreed downtime and data-loss targets, backup owners, sensitive-data handling and retention, alert ownership, and evidence from a restore drill. |

### Keeping current state accurate

For each completed phase, record the date, environment, test or demonstration, and any remaining limitations. For Phase 10, a successful map edit demonstrates only the normal path. Completion also requires evidence that a lost response produces an honest status and that recovery preserves later edits.
