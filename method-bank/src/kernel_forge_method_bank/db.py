"""SQLite source of truth; multi-table mutations are atomic."""
import datetime
import json
from pathlib import Path
import re
import sqlite3
import uuid
from models import SCHEMAS, validate

def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

class MethodBank:
    def __init__(self, path):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(path, timeout=10)
        self.connection.row_factory = sqlite3.Row
        self.connection.executescript(Path(__file__).with_name("schema.sql").read_text(encoding="utf-8-sig"))
        self.seed()

    def close(self):
        self.connection.close()

    def call(self, name, arguments):
        if name not in SCHEMAS:
            raise ValueError(f"Unknown tool: {name}")
        validate(arguments, SCHEMAS[name])
        return getattr(self, name)(**arguments)

    def _insert(self, method, sources):
        method = dict(method)
        method["id"] = method.get("id") or "METHOD-" + uuid.uuid4().hex.upper()
        method["status"] = "candidate"
        method["created_at"] = method["updated_at"] = now()
        method["scope_tags"] = json.dumps(method["scope_tags"], ensure_ascii=False)
        columns = list(method)
        self.connection.execute(f"INSERT INTO methods ({','.join(columns)}) VALUES ({','.join('?' for _ in columns)})", list(method.values()))
        for source in sources:
            data = {k: source[k] for k in ("source_id", "source_type", "title", "external_id", "uri", "metadata")}
            data["metadata"] = json.dumps(data["metadata"], ensure_ascii=False, sort_keys=True, allow_nan=False)
            existing = self.connection.execute("SELECT * FROM sources WHERE source_id=?", (source["source_id"],)).fetchone()
            if existing and dict(existing) != data:
                raise ValueError(f"Conflicting metadata for source {source['source_id']}")
            if not existing:
                self.connection.execute("INSERT INTO sources VALUES (?,?,?,?,?,?)", list(data.values()))
            self.connection.execute("INSERT INTO method_sources VALUES (?,?,?,?,?)",
                (method["id"], source["source_id"], source["locator"], source["relation"], source["note"]))
        return {"method_id": method["id"]}

    def method_add_candidate(self, method, sources):
        with self.connection:
            return self._insert(method, sources)

    def _method(self, method_id):
        row = self.connection.execute("SELECT * FROM methods WHERE id=?", (method_id,)).fetchone()
        if row is None:
            raise ValueError(f"Method not found: {method_id}")
        result = dict(row)
        result["scope_tags"] = json.loads(result["scope_tags"])
        return result

    def method_get(self, method_id):
        result = self._method(method_id)
        result["sources"] = self.method_sources(method_id)
        result["reviews"] = [dict(r) for r in self.connection.execute("SELECT * FROM reviews WHERE method_id=? ORDER BY review_id", (method_id,))]
        return result

    def method_sources(self, method_id):
        self._method(method_id)
        rows = self.connection.execute("SELECT s.*, l.locator, l.relation, l.note FROM sources s JOIN method_sources l USING(source_id) WHERE l.method_id=? ORDER BY s.source_id,l.locator,l.relation", (method_id,))
        return [{**dict(r), "metadata": json.loads(r["metadata"])} for r in rows]

    def source_get(self, source_id):
        row = self.connection.execute("SELECT * FROM sources WHERE source_id=?", (source_id,)).fetchone()
        if row is None:
            raise ValueError(f"Source not found: {source_id}")
        result = dict(row)
        result["metadata"] = json.loads(result["metadata"])
        result["locators"] = [dict(r) for r in self.connection.execute("SELECT method_id,locator,relation,note FROM method_sources WHERE source_id=? ORDER BY method_id,locator,relation", (source_id,))]
        return result

    def _review(self, method_id, decision, review_note):
        timestamp = now()
        self._method(method_id)
        self.connection.execute("INSERT INTO reviews(method_id,decision,review_note,reviewed_at) VALUES (?,?,?,?)", (method_id, decision, review_note, timestamp))
        self.connection.execute("UPDATE methods SET status=?,updated_at=? WHERE id=?", (decision, timestamp, method_id))
        return {"method_id": method_id, "status": decision, "updated_at": timestamp}

    def method_review(self, method_id, decision, review_note):
        with self.connection:
            return self._review(method_id, decision, review_note)

    def method_search(self, query="", scope_levels=None, scope_tags=None, status=None, limit=20):
        tokens = re.findall(r"[^\W_]+", query, re.UNICODE)
        params, conditions = [], []
        join, order = "", "m.id"
        if query.strip() and not tokens:
            return []
        if tokens:
            join = " JOIN methods_fts f ON m.id=f.id"
            conditions.append("methods_fts MATCH ?")
            params.append(" OR ".join('"' + t + '"' for t in tokens))
            order = "bm25(methods_fts),m.id"
        if scope_levels:
            conditions.append(f"m.scope_level IN ({','.join('?' for _ in scope_levels)})")
            params.extend(scope_levels)
        if scope_tags:
            conditions.append(f"EXISTS (SELECT 1 FROM json_each(m.scope_tags) t WHERE t.value IN ({','.join('?' for _ in scope_tags)}))")
            params.extend(scope_tags)
        if status:
            conditions.append("m.status=?")
            params.append(status)
        where = " WHERE " + " AND ".join(conditions) if conditions else ""
        sql = "SELECT m.id,m.title,m.aphorism,m.trigger,m.scope_level,m.scope_tags,m.status FROM methods m" + join + where + " ORDER BY " + order + " LIMIT ?"
        rows = self.connection.execute(sql, [*params, limit])
        return [{**dict(r), "scope_tags": json.loads(r["scope_tags"])} for r in rows]

    def seed(self):
        mid = "METHOD-MINIMUM-SUFFICIENT-CONTEXT"
        # Serialize concurrent startups; seed and review are one transaction.
        with self.connection:
            self.connection.execute("BEGIN IMMEDIATE")
            if self.connection.execute("SELECT 1 FROM methods WHERE id=?", (mid,)).fetchone():
                return
            method = dict(id=mid, title="Minimum Sufficient Context",
                aphorism="Give each agent only the context required to perform its role reliably.",
                source_claim="The specification requires task context derived from goal, artifacts, constraints and acceptance criteria.",
                interpretation="Select context for the assigned role and preserve pointers to additional evidence.",
                generalized_principle="Provide the smallest sufficient context for reliable delegation.",
                trigger="Whenever work is delegated to an agent or subagent.",
                scope_level="universal", scope_tags=["agent-orchestration"],
                action_bias="Construct task context from goal, required artifacts, relevant constraints and acceptance criteria.",
                verification="Check whether the agent could complete its assignment and whether extra context materially contributed.")
            source = dict(source_id="SOURCE-KERNEL-FORGE-SPEC", source_type="repository",
                title="Kernel-Forge Specification v0.1", external_id="v0.1", uri="KERNEL_FORGE_SPEC.md",
                metadata={}, locator="sections 2 and 11", relation="origin",
                note="Explicit reviewed seed required by section 11.")
            self._insert(method, [source])
            self._review(mid, "reviewed", "Explicitly accepted as universal seed by specification section 11.")
