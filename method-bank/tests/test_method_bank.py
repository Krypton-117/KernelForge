"""Behavioral acceptance and regression checks; only temporary databases."""
import copy
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest

SRC = Path(__file__).resolve().parents[1] / "src" / "kernel_forge_method_bank"
sys.path.insert(0, str(SRC))
from db import MethodBank
from server import Server, ProtocolError

def candidate(mid="METHOD-TEST", scope="domain", title="Controlled experiment"):
    return {"method": dict(id=mid, title=title, aphorism="Change one factor.",
        source_claim="Paired comparisons isolate measured effects.",
        interpretation="Hold workload fixed when changing a factor.",
        generalized_principle="Compare controls before attribution.",
        trigger="Investigating a regression", scope_level=scope, scope_tags=["testing"],
        action_bias="Measure baseline and treatment.", verification="Repeat the measurement."),
        "sources": [dict(source_id="SOURCE-TEST", source_type="experiment", title="Test experiment",
            external_id="", uri="test://experiment", metadata={"run": 1},
            locator="measurement 1", relation="supports", note="Test fixture, not research evidence.")]}

class BankTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "test.sqlite3"
        self.bank = MethodBank(self.path)
    def tearDown(self):
        self.bank.close()
        self.temp.cleanup()
    def add(self, **kwargs):
        return self.bank.call("method_add_candidate", candidate(**kwargs))

    def test_seed_and_restart(self):
        mid = "METHOD-MINIMUM-SUFFICIENT-CONTEXT"
        record = self.bank.method_get(mid)
        self.assertEqual(record["status"], "reviewed")
        self.assertEqual(len(record["reviews"]), 1)
        self.bank.close()
        self.bank = MethodBank(self.path)
        self.assertEqual(self.bank.method_get(mid), record)

    def test_three_scopes_compact_filtered_retrieval(self):
        self.add()
        self.add(mid="METHOD-PROJECT", scope="project")
        result = self.bank.call("method_search", {"query": "regression controls",
            "scope_levels": ["domain"], "scope_tags": ["testing"], "status": "candidate", "limit": 1})
        self.assertEqual([m["id"] for m in result], ["METHOD-TEST"])
        self.assertNotIn("source_claim", result[0])
        self.assertNotIn("sources", result[0])
        self.assertEqual(len(self.bank.method_search()), 3)
        self.assertEqual(self.bank.method_search(scope_tags=["missing"]), [])
        for field in ("title", "aphorism", "trigger", "interpretation", "generalized_principle"):
            payload = candidate("METHOD-" + field)
            payload["method"][field] = "uniquefindtoken"
            self.bank.call("method_add_candidate", payload)
        self.assertEqual(len(self.bank.method_search("uniquefindtoken")), 5)

    def test_provenance_roundtrip_many_to_many(self):
        payload = candidate()
        extra = copy.deepcopy(payload["sources"][0])
        extra.update(source_id="SOURCE-SECOND", locator="section 2")
        payload["sources"].append(extra)
        self.bank.call("method_add_candidate", payload)
        self.add(mid="METHOD-SECOND")
        record = self.bank.method_get("METHOD-TEST")
        self.assertEqual(record["scope_tags"], ["testing"])
        self.assertEqual(len(record["sources"]), 2)
        source = self.bank.source_get("SOURCE-TEST")
        self.assertEqual(source["metadata"], {"run": 1})
        self.assertEqual(len(source["locators"]), 2)

    def test_atomic_rollback_on_late_source_conflict(self):
        self.add()
        payload = candidate("METHOD-FAILED")
        good = copy.deepcopy(payload["sources"][0])
        good["source_id"] = "SOURCE-ROLLBACK"
        payload["sources"][0]["title"] = "Conflicting title"
        payload["sources"].insert(0, good)
        with self.assertRaises(ValueError):
            self.bank.call("method_add_candidate", payload)
        with self.assertRaises(ValueError):
            self.bank.method_get("METHOD-FAILED")
        with self.assertRaises(ValueError):
            self.bank.source_get("SOURCE-ROLLBACK")
        self.assertEqual(len(self.bank.method_search("Controlled")), 1)
        self.assertEqual(self.bank.connection.execute("PRAGMA integrity_check").fetchone()[0], "ok")
        self.assertEqual(self.bank.connection.execute("PRAGMA foreign_key_check").fetchall(), [])

    def test_review_records_and_filters(self):
        self.add()
        created = self.bank.method_get("METHOD-TEST")["created_at"]
        self.bank.call("method_review", dict(method_id="METHOD-TEST", decision="reviewed", review_note="Verified experiment."))
        self.assertEqual(len(self.bank.method_search("experiment", status="reviewed")), 1)
        self.bank.call("method_review", dict(method_id="METHOD-TEST", decision="candidate", review_note="Needs replication."))
        method = self.bank.method_get("METHOD-TEST")
        self.assertEqual(method["created_at"], created)
        self.assertEqual(len(method["reviews"]), 2)
        self.assertEqual(method["status"], "candidate")

    def test_invalid_inputs_do_not_write(self):
        for change in [{"status": "reviewed"}, {"scope_level": "global"}, {"title": " "}, {"scope_tags": "testing"}, {"created_at": "fake"}]:
            payload = candidate()
            payload["method"].update(change)
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.bank.call("method_add_candidate", payload)
        payload = candidate()
        payload["sources"] = []
        with self.assertRaises(ValueError):
            self.bank.call("method_add_candidate", payload)
        for limit in [0, 101, True, "10"]:
            with self.subTest(limit=limit), self.assertRaises(ValueError):
                self.bank.call("method_search", {"limit": limit})
        self.assertEqual(len(self.bank.method_search()), 1)

    def test_literal_query_punctuation_and_injection(self):
        self.add(title="O'Reilly: regression 中文")
        self.assertEqual(len(self.bank.method_search("中文")), 1)
        self.assertEqual(len(self.bank.method_search('O"Reilly regression')), 1)
        self.assertEqual(self.bank.method_search("***"), [])
        self.bank.method_search("'; DROP TABLE methods; --")
        self.assertEqual(len(self.bank.method_search()), 2)

    def test_missing_records(self):
        for name, args in [("method_get", {"method_id": "missing"}), ("method_sources", {"method_id": "missing"}),
            ("source_get", {"source_id": "missing"}), ("method_review", {"method_id": "missing", "decision": "reviewed", "review_note": "test"})]:
            with self.subTest(tool=name), self.assertRaises(ValueError):
                self.bank.call(name, args)

class StdioTests(unittest.TestCase):
    def test_mcp_wire_lifecycle_and_persistence(self):
        with tempfile.TemporaryDirectory() as td:
            db = Path(td) / "wire.sqlite3"
            initialize = dict(jsonrpc="2.0", id=1, method="initialize", params={
                "protocolVersion": "2025-11-25", "capabilities": {}, "clientInfo": {"name": "test", "version": "1"}})
            requests = [
                dict(jsonrpc="2.0", id=0, method="tools/list"),
                initialize, dict(jsonrpc="2.0", method="notifications/initialized"),
                dict(jsonrpc="2.0", id=2, method="tools/list"),
                dict(jsonrpc="2.0", id=3, method="tools/call", params={"name": "method_add_candidate", "arguments": candidate()}),
                dict(jsonrpc="2.0", method="notifications/cancelled", params={"requestId": 999}),
                dict(jsonrpc="2.0", id=4, method="tools/call", params={"name": "method_get", "arguments": {"method_id": "METHOD-TEST"}}),
                dict(jsonrpc="2.0", id=5, method="tools/call", params={"name": "method_search", "arguments": {"limit": True}}),
                dict(jsonrpc="2.0", id=6, method="tools/call", params={"name": "unknown"}),
                dict(jsonrpc="2.0", id=7, method="ping"),
            ]
            wire = "\n".join(json.dumps(r) for r in requests) + "\nnot json\n[]\n"
            p = subprocess.run([sys.executable, str(SRC/"server.py"), "--db", str(db)], input=wire,
                capture_output=True, text=True, encoding="utf-8", timeout=20, cwd=td)
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertEqual(p.stderr, "")
            results = [json.loads(line) for line in p.stdout.splitlines()]
            self.assertEqual(len(results), 10)
            self.assertIn("error", results[0])
            self.assertEqual(results[1]["result"]["protocolVersion"], "2025-11-25")
            self.assertEqual(len(results[2]["result"]["tools"]), 6)
            record = json.loads(results[4]["result"]["content"][0]["text"])
            self.assertEqual(record["sources"][0]["locator"], "measurement 1")
            self.assertTrue(results[5]["result"]["isError"])
            self.assertEqual(results[6]["error"]["code"], -32602)
            self.assertEqual(results[-2]["error"]["code"], -32700)
            self.assertEqual(results[-1]["error"]["code"], -32600)
            bank = MethodBank(db)
            try:
                self.assertEqual(bank.method_get("METHOD-TEST")["title"], "Controlled experiment")
            finally:
                bank.close()

if __name__ == "__main__":
    unittest.main()
