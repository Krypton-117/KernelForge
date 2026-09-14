PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS methods (
 id TEXT PRIMARY KEY, title TEXT NOT NULL, aphorism TEXT NOT NULL,
 source_claim TEXT NOT NULL, interpretation TEXT NOT NULL,
 generalized_principle TEXT NOT NULL, trigger TEXT NOT NULL,
 scope_level TEXT NOT NULL CHECK(scope_level IN ('universal','domain','project','task')),
 scope_tags TEXT NOT NULL, action_bias TEXT NOT NULL, verification TEXT NOT NULL,
 status TEXT NOT NULL CHECK(status IN ('candidate','reviewed')),
 created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);
CREATE VIRTUAL TABLE IF NOT EXISTS methods_fts USING fts5(
 id UNINDEXED, title, aphorism, trigger, interpretation, generalized_principle
);
CREATE TRIGGER IF NOT EXISTS methods_insert AFTER INSERT ON methods BEGIN
 INSERT INTO methods_fts VALUES(new.id,new.title,new.aphorism,new.trigger,new.interpretation,new.generalized_principle);
END;
CREATE TRIGGER IF NOT EXISTS methods_delete AFTER DELETE ON methods BEGIN
 DELETE FROM methods_fts WHERE id=old.id;
END;
CREATE TABLE IF NOT EXISTS sources (
 source_id TEXT PRIMARY KEY, source_type TEXT NOT NULL, title TEXT NOT NULL,
 external_id TEXT NOT NULL, uri TEXT NOT NULL, metadata TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS method_sources (
 method_id TEXT NOT NULL REFERENCES methods(id), source_id TEXT NOT NULL REFERENCES sources(source_id),
 locator TEXT NOT NULL, relation TEXT NOT NULL, note TEXT NOT NULL,
 PRIMARY KEY(method_id,source_id,locator,relation)
);
CREATE TABLE IF NOT EXISTS reviews (
 review_id INTEGER PRIMARY KEY, method_id TEXT NOT NULL REFERENCES methods(id),
 decision TEXT NOT NULL CHECK(decision IN ('candidate','reviewed')),
 review_note TEXT NOT NULL, reviewed_at TEXT NOT NULL
);
