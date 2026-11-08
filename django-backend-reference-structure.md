# Django API Backend — Redesigned Reference Structure

This is the complete reference structure for the agreed application scope. It is not a starting implementation, a development sequence, or a requirement to create empty files. All 27 engineering categories remain covered.

The redesign separates business ownership, durable operation coordination, integration protocols, execution infrastructure, and production operations. A category can cross these boundaries without having competing owners.

## 1. Main ownership boundaries

| Location | Owns |
| --- | --- |
| `config/` | Configuration definitions, defaults, overrides, validation, and application assembly. |
| `apps/` | Application features, business decisions, permissions, and authoritative application records. |
| `integrations/` | Communication with external systems: clients, pools, requests, response interpretation, and connectivity checks. |
| `foundation/` | Small shared technical mechanisms: HTTP behavior, security helpers, resilience mechanics, and telemetry. |
| `runtime/` | Broker transport, durable message delivery, worker entry points, scheduler execution, and process lifecycle. |
| `ops/` | Deployment, monitoring infrastructure, secrets provisioning, backup procedures, and operational configuration. |
| `tests/` | Automated verification, including cross-boundary failures and recovery. |
| `docs/` | Contracts, ownership decisions, workflow specifications, and operational runbooks. |

`resources` is the existing business-domain placeholder. Replace its name with the actual business term once established. Do not invent additional business domains merely to fill the tree.

## 2. Full reference tree

Python package marker files are omitted for readability. `apps.py` is shown for application packages. Persistence is deliberately represented by `store.py` until its backend is selected. Add `models.py` and `migrations/` only in owners that use Django ORM persistence; the tree does not assume Cassandra or ArcGIS-managed PostgreSQL is a Django ORM database.

```text
django_backend/
├── manage.py
├── pyproject.toml
├── .gitignore
├── .env.example
├── .pre-commit-config.yaml
├── .github/
│   └── workflows/
│       └── quality_checks.yml
│
├── config/
│   ├── urls.py
│   ├── asgi.py
│   ├── wsgi.py
│   ├── wiring.py
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   ├── testing.py
│   │   └── production.py
│   ├── connections.py
│   ├── features.py
│   ├── security.py
│   ├── execution.py
│   ├── limits.py
│   ├── telemetry.py
│   └── validation.py
│
├── apps/
│   ├── identity/
│   │   ├── apps.py
│   │   ├── api/
│   │   │   ├── urls.py
│   │   │   ├── views.py
│   │   │   └── serializers.py
│   │   ├── authentication.py
│   │   ├── credentials.py
│   │   ├── sessions.py
│   │   ├── tokens.py
│   │   ├── access_policy.py
│   │   └── store.py
│   ├── resources/
│   │   ├── apps.py
│   │   ├── api/
│   │   │   ├── urls.py
│   │   │   ├── views.py
│   │   │   └── serializers.py
│   │   ├── service.py
│   │   ├── queries.py
│   │   ├── rules.py
│   │   ├── permissions.py
│   │   ├── dependency_policy.py
│   │   ├── store.py
│   │   ├── remote_mappings.py
│   │   └── workflows/
│   │       ├── create.py
│   │       ├── update.py
│   │       ├── delete.py
│   │       ├── compensation.py
│   │       └── reconciliation.py
│   ├── operations/
│   │   ├── apps.py
│   │   ├── api/
│   │   │   ├── urls.py
│   │   │   ├── views.py
│   │   │   └── serializers.py
│   │   ├── service.py
│   │   ├── states.py
│   │   ├── store.py
│   │   ├── steps.py
│   │   ├── idempotency.py
│   │   ├── claims.py
│   │   ├── recovery.py
│   │   └── permissions.py
│   ├── jobs/
│   │   ├── apps.py
│   │   ├── api/
│   │   │   ├── urls.py
│   │   │   ├── views.py
│   │   │   ├── serializers.py
│   │   │   └── callbacks.py
│   │   ├── service.py
│   │   ├── states.py
│   │   ├── store.py
│   │   ├── handlers.py
│   │   ├── remote_results.py
│   │   ├── schedules.py
│   │   └── permissions.py
│   ├── files/
│   │   ├── apps.py
│   │   ├── api/
│   │   │   ├── urls.py
│   │   │   ├── views.py
│   │   │   └── serializers.py
│   │   ├── service.py
│   │   ├── store.py
│   │   ├── permissions.py
│   │   ├── validation.py
│   │   └── transfers.py
│   ├── notifications/
│   │   ├── apps.py
│   │   ├── events.py
│   │   ├── service.py
│   │   ├── subscriptions.py
│   │   ├── permissions.py
│   │   ├── replay.py
│   │   ├── store.py
│   │   └── transports/
│   │       ├── sse.py
│   │       └── websocket.py
│   ├── audit/
│   │   ├── apps.py
│   │   ├── events.py
│   │   ├── service.py
│   │   ├── store.py
│   │   └── policy.py
│   └── support/
│       ├── apps.py
│       ├── health/
│       │   ├── urls.py
│       │   ├── views.py
│       │   └── checks.py
│       ├── diagnostics.py
│       └── management/
│           └── commands/
│               ├── check_dependencies.py
│               ├── inspect_operation.py
│               ├── inspect_job.py
│               ├── find_request.py
│               ├── recover_operations.py
│               ├── seed_data.py
│               ├── apply_schema_changes.py
│               └── verify_restore.py
│
├── integrations/
│   ├── cassandra/
│   │   ├── client.py
│   │   ├── queries.py
│   │   └── health.py
│   ├── arcgis/
│   │   ├── client.py
│   │   ├── resources.py
│   │   ├── mapping.py
│   │   ├── outcome_lookup.py
│   │   └── health.py
│   ├── elasticsearch/
│   │   ├── client.py
│   │   ├── documents.py
│   │   └── health.py
│   ├── hdfs/
│   │   ├── client.py
│   │   ├── files.py
│   │   └── health.py
│   ├── oracle_visualization/
│   │   ├── client.py
│   │   ├── visualizations.py
│   │   └── health.py
│   ├── spark/
│   │   ├── client.py
│   │   ├── jobs.py
│   │   └── health.py
│   └── external_worker/
│       ├── client.py
│       ├── tasks.py
│       └── health.py
│
├── foundation/
│   ├── context.py
│   ├── outcomes.py
│   ├── errors.py
│   ├── http/
│   │   ├── middleware.py
│   │   ├── responses.py
│   │   ├── pagination.py
│   │   └── validation.py
│   ├── security/
│   │   ├── secrets.py
│   │   ├── encryption.py
│   │   └── tls.py
│   ├── resilience/
│   │   ├── deadlines.py
│   │   ├── retries.py
│   │   └── limits.py
│   └── telemetry/
│       ├── logging.py
│       ├── redaction.py
│       ├── metrics.py
│       ├── tracing.py
│       └── errors.py
│
├── runtime/
│   ├── messaging/
│   │   ├── client.py
│   │   ├── envelopes.py
│   │   ├── publisher.py
│   │   ├── consumer.py
│   │   ├── outbox.py
│   │   ├── inbox.py
│   │   ├── store.py
│   │   ├── redelivery.py
│   │   └── health.py
│   ├── workers.py
│   ├── scheduler.py
│   └── lifecycle.py
│
├── ops/
│   ├── deployment/
│   │   ├── application.yaml
│   │   ├── workers.yaml
│   │   └── scheduler.yaml
│   ├── security/
│   │   ├── access_policies.yaml
│   │   └── key_rotation.md
│   ├── monitoring/
│   │   ├── uptime_probes.yaml
│   │   ├── log_shipping.yaml
│   │   ├── retention_and_access.yaml
│   │   ├── dashboards.json
│   │   └── alerts.yaml
│   └── data/
│       ├── seeds/
│       │   ├── reference_data.json
│       │   └── development_data.json
│       ├── schema_changes/
│       │   ├── cassandra/
│       │   └── elasticsearch/
│       ├── backup_policy.yaml
│       └── restore_checks.py
│
├── tests/
│   ├── conftest.py
│   ├── unit/
│   ├── integration/
│   ├── contracts/
│   ├── end_to_end/
│   ├── security/
│   ├── failures/
│   ├── lifecycle/
│   ├── load/
│   └── recovery/
│
└── docs/
    ├── architecture.md
    ├── ownership.md
    ├── configuration.md
    ├── capability_coverage.md
    ├── api/
    │   ├── openapi.yaml
    │   ├── examples.md
    │   └── compatibility.md
    ├── workflows/
    │   ├── resource_changes.md
    │   ├── asynchronous_execution.md
    │   ├── operation_states.md
    │   └── persistence_guarantees.md
    ├── decisions/
    └── runbooks/
        ├── dependency_outage.md
        ├── unknown_outcome.md
        ├── manual_recovery.md
        └── backup_and_restore.md
```

The listed JSON and YAML files are responsibility placeholders, not a selection of deployment platform, monitoring product, broker, or configuration format. SSE and WebSocket locations are alternatives or optional capabilities; the tree does not require implementing both. The same applies to session-based and token-based authentication.

## 3. Ownership rules that remove overlap

### 3.1 Business workflows versus operation coordination

`apps/resources/workflows/` decides the business sequence, completion requirements, compensation, and reconciliation. It owns the Cassandra–ArcGIS workflow.

`apps/operations/` owns the durable operation record, step evidence, transition validation, duplicate-request handling, and recovery claims. It does not decide how to undo a resource update.

`operations/recovery.py` finds recoverable operations and dispatches their registered recovery handler. `resources/workflows/reconciliation.py` determines what that specific workflow should do. `config/wiring.py` connects these handlers explicitly; no workflow engine, plugin framework, or event bus is implied.

Generic transitions are validated by operations. The business workflow supplies the evidence and decides whether its required steps satisfy completion. Neither layer can mark success merely because a function returned without raising an exception.

### 3.2 Operations versus jobs

An operation represents one logical user action. A job represents an execution unit, which may run locally in a worker or remotely in Spark or another service.

One operation can have zero, one, or several jobs. Each job has an operation ID when it belongs to that action. A scheduled job may create an operation when it performs a tracked business change.

`operations/states.py` owns the user-visible business outcome. `jobs/states.py` owns job execution status, progress, attempts, remote IDs, and result references. Job completion is evidence for the workflow; it does not automatically complete the operation.

`jobs/handlers.py` invokes business services or workflows; it does not reproduce their business rules. `jobs/remote_results.py` normalizes verified callbacks and polling results into the same job transition path, including duplicate and late-result handling.

### 3.3 Jobs versus messaging

`runtime/messaging/` owns message publication, delivery confirmation, consumption, acknowledgment or offset handling, delivery retries, dead-letter handling, and replay. Broker delivery status is not business success.

The message envelope belongs to messaging. Job payload semantics belong to jobs; notification event semantics belong to notifications. The generic transport must not become the owner of every business payload schema.

`outbox.py` tracks publication intent and retries sending it. `inbox.py` tracks received message identities and processing claims. `store.py` persists transport records. Inbox deduplication alone does not make a remote side effect exactly once; the business workflow must still handle retries and ambiguous effects.

Broker acknowledgment follows the documented durable-processing boundary. A received message, a submitted job, and a completed business operation are different facts.

### 3.4 Durable acceptance versus publication

Placing an operation store and an outbox next to each other does not make their writes atomic.

Before reporting durable acceptance, the application must preserve enough state to recover both the accepted work and its publication intent. The chosen persistence design must either commit these together within a supported atomic boundary or make missing publication intent reconstructible from accepted operation records.

The same question applies to recording job results and arranging completion processing or notifications. This remains an explicit storage design decision in `docs/workflows/persistence_guarantees.md`.

Django database transactions cannot be treated as a transaction covering Cassandra driver calls, ArcGIS REST calls, and broker publication. The folder structure makes no such guarantee.

### 3.5 Notifications versus authoritative results

`apps/notifications/` owns recipient selection, subscription authorization, event validation, transport delivery, reconnect handling, replay policy, and slow-client behavior.

Operations and jobs remain the authoritative sources for status. Notification delivery failure cannot turn a completed business operation into a failed one.

`notifications/store.py` holds notification/replay information, not a competing operation-status database. Reconnecting clients retrieve authoritative status even when event replay is unavailable or its retention window has expired.

### 3.6 Integration clients versus business persistence

Each integration `client.py` owns its connection/session lifecycle, pool limits, and protocol configuration. Its neighboring files expose provider operations and interpret provider responses.

`apps/resources/store.py` owns application persistence operations and calls Cassandra query functions. `apps/resources/queries.py` owns application read use cases. `integrations/cassandra/queries.py` owns parameterized CQL and driver-level query behavior. These are separate responsibilities, not three competing repositories.

`remote_mappings.py` owns the association between application resources and remote resource IDs. `arcgis/mapping.py` owns provider payload/response translation. Django uses ArcGIS REST APIs, not direct access to ArcGIS-managed PostgreSQL.

Application owners keep their own persistence logic. They may share a physical database and client pool; separate `store.py` files do not imply separate databases or services. No generic repository base class is required.

The existing `cleaned_01` read boundary is retained. The destination and ownership of application-originated Cassandra writes remain open; do not silently assign them to raw keyspaces or assume the backend owns every table in `cleaned_01`.

### 3.7 Configuration versus behavior

`config/` is the only definition and validation location for runtime configuration. Environment settings assemble it. Feature code consumes validated settings without privately rereading environment variables or inventing another default.

- `connections.py`: endpoints, keyspaces, indexes, connection and pool settings.
- `features.py`: feature flags and per-feature settings.
- `security.py`: authentication settings, credential references, TLS and cryptographic policy settings; never actual secrets.
- `execution.py`: deadlines, retry budgets, job timing, and shutdown settings.
- `limits.py`: request, page, concurrency, rate, quota, stream, and buffering limits.
- `telemetry.py`: logging levels, instrumentation switches, and export settings.
- `validation.py`: required values, type/range checks, and invalid cross-setting combinations.

Configuration management is continuous across all features. Deployment changes are reviewed, validated, and traceable. Diagnostic output must redact sensitive values.

Defaults, environment overrides, and feature-level overrides need a documented precedence. Workflow-critical policy choices should be recorded or versioned so recovery does not silently reinterpret an in-progress operation after configuration changes.

A feature flag may block new operations while allowing existing operations to finish or recover. It must not silently bypass authorization or necessary correctness checks. Feature flags cannot redefine an established success condition without an explicit workflow policy.

### 3.8 Retry configuration versus retry decisions

`foundation/resilience/retries.py` supplies bounded retry timing and budget mechanics. `config/execution.py` supplies values. Integration adapters classify provider errors and capabilities. Business workflows decide whether repeating a particular action is safe.

Transport redelivery belongs to messaging, while operation recovery belongs to operations and the business workflow. These are distinct retry scopes, coordinated by a common deadline/attempt policy. Driver retries must count toward the effective budget; nested retries must not multiply unchecked.

`foundation/outcomes.py` provides common vocabulary for confirmed, rejected, pending, and unknown external outcomes. It is not a second operation state machine.

### 3.9 Authentication versus feature permissions

`identity/` owns user/service identity, password verification through supported hashing facilities, session and token lifecycle, global role assignments, account lockout, and authentication policy.

Each feature's `permissions.py` owns action and object access for that feature. Resources, operations, jobs, files, and notification subscriptions each enforce their own access rules using identity information.

Login throttling uses shared limiting mechanisms, but identity owns the lockout decision. Deployment access policies provision downstream service permissions; feature policies decide whether to use service credentials or permitted delegated user access.

Cookie/CSRF behavior follows the selected authentication transport. Password hashing is not encryption. `foundation/security/` provides controlled access to existing security facilities; it is not a place to invent cryptographic algorithms.

### 3.10 Input validation versus business rules

API serializers validate each endpoint's request and response shape. Feature rules validate business constraints, including calls originating from workers. Shared HTTP validation contains only genuinely reusable field/query checks.

File type, size, path, and transfer validation belong to `apps/files/validation.py`. Provider payload mapping belongs to the respective integration. Query parameterization belongs to datastore adapters. Output encoding remains specific to the destination context.

There is no global sanitize-everything function. Different boundaries require different checks.

### 3.11 Files versus HDFS

`apps/files/` owns application file identity, access rules, transfer policy, upload/download behavior, range/resume semantics, and bounded buffering. Its `store.py` holds application file/transfer metadata where needed.

`integrations/hdfs/files.py` performs HDFS operations. It does not decide which user may download a file or how the API should represent a resumable transfer.

Disconnect cancellation and transfer cleanup belong to the transfer owner. Process-wide shutdown invokes that owner's cleanup hooks.

### 3.12 Logging versus audit versus diagnostics

`foundation/telemetry/` implements application/access/error log formatting, correlation, redaction, log injection prevention, metrics, tracing, and exception capture. Middleware and integrations call it; they do not each invent a logging system.

`apps/audit/` owns structured accountability records: actor, action, resource, time, and outcome, including attempted and uncertain outcomes where applicable. Its policy governs access, integrity, retention requirements, and behavior when audit persistence fails. Infrastructure enforces the corresponding storage controls.

`apps/support/diagnostics.py` provides profiling, request inspection, and operational inspection helpers. Management commands are thin entry points into their actual owners. For example, `recover_operations` invokes operations recovery; it does not contain another compensation algorithm.

Request ID, operation ID, job ID, message ID, and trace ID are related identifiers, not interchangeable ones. A retry may have a new request/message ID while retaining the same operation ID.

### 3.13 Health checks versus availability decisions

Integration health files measure bounded connectivity/access checks and expose timestamped results. `apps/support/health/checks.py` aggregates liveness, readiness, startup, and dependency results.

`resources/dependency_policy.py` defines required and optional dependencies for resource operations. Other feature owners define their own policy within their service when needed; it is not necessary to create a policy file everywhere.

An optional Elasticsearch outage need not make all Django endpoints unready. A successful health check also does not prove the next write will succeed. Each workflow still handles actual call failures.

### 3.14 Scheduling versus process lifecycle

`jobs/schedules.py` owns schedules, run identity, overlap/missed-run policy, and durable run claims. `runtime/scheduler.py` triggers due runs through that API. `ops/deployment/scheduler.yaml` configures the scheduler process; it does not define a competing business schedule.

`runtime/lifecycle.py` coordinates readiness transitions, draining, deadlines, client cleanup, and telemetry flushing. Messaging, file transfers, and notification transports implement their own cleanup behavior and register it with lifecycle assembly.

An external worker cannot be assumed to stop or checkpoint when Django shuts down. The application records remote job identity and resumes tracking after restart. Checkpointing is used only where the worker/provider supports it.

Do not open network connections or start background loops merely because a Python module is imported. Django application registration is not a substitute for worker process supervision.

### 3.15 Operational recovery versus business reconciliation

`ops/data/` owns backup inventory/policy, schedules, retention, restore checks, and non-ORM schema artifacts. Native Django ORM migrations, if selected, stay with their owning app.

`resources/workflows/reconciliation.py` owns business repair decisions after a restore or partial write. Restore checks can discover mismatches and invoke/report that workflow, but do not define their own repair rules.

ArcGIS-managed data must be backed up and restored through the responsible platform's supported procedures. Point-in-time recovery is included only where the selected datastore and deployment support it.

## 4. Coverage of all 27 categories

| # | Engineering category | Primary owner and coverage |
| --- | --- | --- |
| 1 | Configuration management | `config/`: environments, precedence, connections, feature flags, limits, execution settings, defaults, startup validation, and ongoing change management. |
| 2 | Secrets management and encryption | `foundation/security/`, `config/security.py`, and `ops/security/`: secret access, TLS verification, encryption/decryption and rotation controls. Identity owns password hashing integration; datastore/infrastructure owners enforce at-rest encryption. |
| 3 | Authentication and user sessions | `apps/identity/`: user/service authentication, login/logout, lockout, sessions, secure cookies/CSRF policy, JWT validation, expiry, refresh rotation, and revocation as applicable. |
| 4 | Authorization | `identity/access_policy.py` plus each feature's `permissions.py`: RBAC, action/resource checks, least privilege, service/delegated access, files, jobs, and subscriptions. |
| 5 | HTTP request–response lifecycle | `config/urls.py`, settings, `foundation/http/`, and feature `api/`: routing, middleware order, context, authentication hooks, validation, execution, serialization, headers, status, and cleanup. |
| 6 | Input validation and injection prevention | Feature serializers/rules, `foundation/http/validation.py`, `files/validation.py`, and adapters: normalization, parameterization, allowlisted query keys, context-specific encoding, and file/path checks. |
| 7 | API contracts, versioning, and documentation | Feature `api/`, `foundation/http/pagination.py`, and `docs/api/`: schemas, pagination/filtering/sorting, routing-based version boundaries, compatibility, deprecation, OpenAPI, and examples. |
| 8 | External service integrations | `integrations/`: Cassandra `cleaned_01` reads, HDFS, Elasticsearch, ArcGIS, Oracle visualization, Spark, and the separately identified external REST worker. |
| 9 | Outbound API requests and responses | Integration operation modules and `foundation/outcomes.py`: request mapping, credentials, malformed responses, HTTP/application errors, outcome classification, remote IDs, and status lookup. |
| 10 | Outbound clients, sessions, and connection pools | Each integration `client.py` and messaging `client.py`: connection reuse, pool limits, concurrency/process rules, reconnects, stale connections, and cleanup. |
| 11 | Error handling and dependency outages | `foundation/errors.py`, HTTP responses, feature dependency policies, and business workflows: consistent errors, optional/required systems, partial results, fallbacks, and recovery. |
| 12 | Timeouts, retries, and idempotency | `config/execution.py`, `foundation/resilience/`, `operations/idempotency.py`, and provider lookup methods: deadlines, coordinated retry budgets, backoff/jitter, duplicate requests, and ambiguous writes. |
| 13 | Data ownership and cross-system consistency | `resources/`, its workflows, and `operations/`: ownership, resource mappings, write order, durable steps, partial writes, compensation, concurrency protection, reconciliation, and manual recovery. |
| 14 | Rate limiting and resource protection | `config/limits.py`, `foundation/resilience/limits.py`, identity, adapters, and stream owners: login/request throttling, quotas/Retry-After, request/page/concurrency limits, and backpressure. |
| 15 | Message broker publishing and consumption | `runtime/messaging/`: connection configuration, envelopes/routing, publisher confirmation, consumption/acknowledgments/offsets, outbox/inbox, duplicate delivery, bounded redelivery, dead letters, and replay. |
| 16 | Background jobs and scheduled tasks | `apps/jobs/`, remote integrations, `runtime/workers.py`, and `runtime/scheduler.py`: submission, persistent ownership/status, progress/results, polling/verified callbacks, schedules, overlap/missed runs, and duplicate execution. |
| 17 | Client notifications and real-time communication | `apps/notifications/`: SSE/WebSocket transport choices, event validation, subscription permissions, reconnect, status resynchronization/replay, disconnect cleanup, and slow-client handling. |
| 18 | Streaming APIs and large media | `apps/files/` and HDFS adapter: large uploads/downloads, video/audio/images, chunked transfer, ranges/resume, bounded buffering, and disconnect cancellation. |
| 19 | Health checks and uptime monitoring | `apps/support/health/`, integration checks, and `ops/monitoring/`: startup/liveness/readiness, timed dependency/access checks, timestamps, external probes, and availability alerts. |
| 20 | Graceful shutdown | `runtime/lifecycle.py` and component cleanup hooks, configured through deployment: draining, request deadlines, stream closure, consumer completion/acknowledgments, supported checkpoints, and telemetry flushing. |
| 21 | Application logging and log management | `foundation/telemetry/`, `config/telemetry.py`, and `ops/monitoring/`: structured application/access/error logs, levels, correlation, redaction, injection prevention, collection, search, retention, and access controls. |
| 22 | Audit logging | `apps/audit/` with identity/business emitters and operational storage controls: login/lockout, permissions changes, data changes, actor/action/resource/time/outcome, integrity, access, and retention. |
| 23 | Observability and error tracking | `foundation/telemetry/` and `ops/monitoring/`: request/dependency/pool/job/broker metrics, traces and context propagation, exception grouping, dashboards, and alerts. |
| 24 | Shared utilities and debugging helpers | `foundation/`, service-specific integrations, and `apps/support/`: shared validation/error/pagination helpers, diagnostic commands, profiling, request inspection, and ID lookup. |
| 25 | Seed data, backups, and recovery | `ops/data/`, support commands, and owner workflows: repeatable seeds/schema changes, per-datastore backups/retention, supported PITR, restore testing, and cross-system reconciliation. |
| 26 | Testing and failure verification | `tests/`: unit, integration, contracts, end-to-end, security, outages, lost responses, duplicates, partial writes, failed compensation, reconnect/shutdown, load, rate limits, and recovery. |
| 27 | Code quality | `pyproject.toml`, pre-commit configuration, and CI: formatting, linting, type checks, coverage reporting, and automated checks. |

## 5. How the main workflow uses these owners

1. HTTP middleware creates request context and applies configured limits. Authentication identifies the caller.
2. The resource API validates the contract and invokes the resource service. The feature checks action/resource permissions and business rules.
3. Operations establishes the operation identity and idempotency decision, using durable storage and concurrency protection.
4. The resource workflow records intended step information before attempting side effects. It performs the Cassandra change through its store and integration, then records the available evidence.
5. The ArcGIS adapter performs the remote request and returns normalized evidence: confirmed, rejected, pending, or unknown as appropriate for that endpoint.
6. The resource workflow decides the next business action. It may complete, check remote state, wait, compensate, or require manual recovery. Cassandra timeouts can also be ambiguous; this rule is not limited to ArcGIS.
7. Operations persists the resulting operation/step state. A crash after a remote change but before this update remains a reconciliation case; tracking cannot remove that distributed failure window.
8. For background execution, jobs owns the execution unit and messaging delivers its command. Job results return through the registered workflow continuation with duplicate/late-result checks.
9. Notifications conveys recorded progress/results. Status APIs remain available for authorized clients that missed an event.

Changing an operation's execution from synchronous to asynchronous must reuse the same business workflow and completion rules.

## 6. Decisions the structure deliberately leaves open

- The durable backend for identities, operations, jobs, audit, message delivery records, and notification replay.
- The actual atomicity and conditional-update guarantees needed for acceptance, idempotency, claims, result recording, and publication intent.
- Cassandra write ownership and keyspaces for application-originated changes.
- RabbitMQ versus Kafka and the exact acknowledgment/replay model.
- Session versus token authentication, and SSE versus WebSockets where applicable.
- Which ArcGIS endpoints support safe retries, identifiers, and reliable outcome lookup.
- Whether the external REST worker is the same service as the broker consumer.
- Per-workflow success conditions, update/delete compensation rules, and manual recovery policy.
- Exact deployment platform, Oracle visualization product, and operational tooling.

These are explicit design decisions, not missing folders. The redesign is an ownership model for LLD; interfaces, storage guarantees, and transition rules still need to be specified for each implemented workflow.

## 7. Framework references

The organization above is a project-specific design proposal. These references support the Django-specific boundaries, not a claim that Django prescribes this folder tree:

- [Django applications](https://docs.djangoproject.com/en/5.2/ref/applications/): application registration, app configuration, and startup limitations.
- [Django database transactions](https://docs.djangoproject.com/en/5.2/topics/db/transactions/): transaction scope and connection-specific atomic blocks.

No Django version, package stack, storage backend, or new production service is selected by this reference structure.
