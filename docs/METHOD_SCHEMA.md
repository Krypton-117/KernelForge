# Method Bank v0.1 contract

The database is authoritative; source objects are independent and shared. Method/source links store locator, relation and note. Every candidate requires at least one source with a nonblank locator.

## Method fields

Inputs contain title, aphorism (may be empty), source_claim, interpretation, generalized_principle, trigger, scope_level, scope_tags, action_bias and verification. Optional id must match METHOD-[A-Za-z0-9_-]+; otherwise the service generates a UUID ID. Timestamps are server-generated UTC ISO-8601. Client timestamps are rejected. Candidate addition always creates status candidate; explicitly supplying reviewed is rejected.

Scopes: universal, domain, project, task. Statuses: candidate, reviewed. Tags are unique nonblank strings. Keep source_claim close to supporting evidence, interpretation specific to the problem, and generalized_principle clearly identifiable as an abstraction.

## Sources and links

Each item in sources includes source_id, source_type, title, external_id, uri, metadata (JSON object), locator, relation, note. external_id, uri and note may be empty. Source types: paper, documentation, human, agent, experiment, repository. Relations: supports, motivates, limits, contradicts, origin.

The same source_id may support many methods and many locations; metadata must match the existing independent source exactly. A conflicting source causes the entire candidate insertion (including FTS rows and all earlier sources/links) to roll back. The API does not silently rewrite existing provenance.

## Six tools

| Tool | Arguments | Result |
|---|---|---|
| method_search | query="", scope_levels=[], scope_tags=[], optional status, limit=20 | Compact records: id/title/aphorism/trigger/scope/tags/status |
| method_get | method_id | Full record, decoded tags, sources, ordered reviews |
| method_add_candidate | method, sources | method_id |
| method_review | method_id, decision, review_note | method_id/status/updated_at |
| method_sources | method_id | Source metadata and link locators/relations/notes |
| source_get | source_id | Source metadata and all method locators |

Search tokenizes ordinary words literally, ORs them, ranks matches using FTS5 BM25 and breaks ties by ID. FTS covers title, aphorism, trigger, interpretation and generalized_principle. An empty query browses deterministically. Punctuation-only queries return no candidates. Scope filters match any listed level, tag filters match any listed tag, and separate filters combine with AND. Status is a single enum; omit it to include both statuses. Limit is an integer from 1 to 100.

method_review accepts decision reviewed or candidate and a nonblank review_note. Each review is durable; returning to candidate preserves review history. The universal seed's initial reviewed status comes explicitly from specification section 11. Candidate extraction is not automatic acceptance.

## MCP and failure behavior

The server implements UTF-8 newline-delimited JSON-RPC over stdio, initialization/version negotiation, initialized notification, ping, tools/list and tools/call. Supported protocol revisions: 2024-11-05, 2025-03-26, 2025-06-18, 2025-11-25. Unknown requested revisions negotiate the latest supported revision. There are no prompts/resources, subscriptions, batch requests or remote HTTP transport.

Malformed JSON and protocol requests return JSON-RPC errors. Tool validation, missing records and storage failures return content with isError=true. Well-formed notifications receive no reply. EOF closes the connection. Tool schemas are discoverable and validated server-side; there is no arbitrary SQL interface.

Only add/review mutate methods. SQLite foreign keys enforce links; transactions keep method/provenance/reviews coherent. Connections close on process exit. The service does not implement a general migration or editing API in v0.1.
