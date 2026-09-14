"""JSON Schemas shared by tool discovery and input validation."""
import re

def obj(properties, required=()):
    return {"type": "object", "properties": properties, "required": list(required), "additionalProperties": False}

TEXT = {"type": "string", "minLength": 1}
STRING = {"type": "string"}
SCOPES = {"type": "string", "enum": ["universal", "domain", "project", "task"]}
STATUS = {"type": "string", "enum": ["candidate", "reviewed"]}
TAGS = {"type": "array", "items": TEXT, "uniqueItems": True}
FIELDS = ["title", "aphorism", "source_claim", "interpretation", "generalized_principle", "trigger", "action_bias", "verification"]
METHOD = obj({**{k: TEXT for k in FIELDS}, "aphorism": STRING,
    "id": {"type": "string", "pattern": r"^METHOD-[A-Za-z0-9_-]+$"},
    "scope_level": SCOPES, "scope_tags": TAGS,
    "status": {"type": "string", "enum": ["candidate"]}}, FIELDS + ["scope_level", "scope_tags"])
SOURCE = obj({"source_id": TEXT, "source_type": {"type": "string",
    "enum": ["paper", "documentation", "human", "agent", "experiment", "repository"]},
    "title": TEXT, "external_id": STRING, "uri": STRING, "metadata": {"type": "object"},
    "locator": TEXT, "relation": {"type": "string", "enum": ["supports", "motivates", "limits", "contradicts", "origin"]},
    "note": STRING}, ["source_id", "source_type", "title", "external_id", "uri", "metadata", "locator", "relation", "note"])
SCHEMAS = {
    "method_search": obj({"query": STRING, "scope_levels": {"type": "array", "items": SCOPES},
        "scope_tags": TAGS, "status": STATUS, "limit": {"type": "integer", "minimum": 1, "maximum": 100}}),
    "method_get": obj({"method_id": TEXT}, ["method_id"]),
    "method_add_candidate": obj({"method": METHOD, "sources": {"type": "array", "items": SOURCE, "minItems": 1}}, ["method", "sources"]),
    "method_review": obj({"method_id": TEXT, "decision": STATUS, "review_note": TEXT}, ["method_id", "decision", "review_note"]),
    "method_sources": obj({"method_id": TEXT}, ["method_id"]),
    "source_get": obj({"source_id": TEXT}, ["source_id"]),
}
DESCRIPTIONS = {
    "method_search": "Search compact methods with literal words (OR), scopes, any matching tag and status. Empty query browses methods. Fetch selected records with method_get.",
    "method_get": "Get a complete method with decoded tags, provenance and review history.",
    "method_add_candidate": "Atomically add a candidate and its source links. IDs/timestamps are generated. Existing source metadata must match.",
    "method_review": "Record explicit review rationale. Decision reviewed accepts; candidate returns to pending review.",
    "method_sources": "Get source metadata, locators and relation notes for a method.",
    "source_get": "Get an independent source and all linked method locators.",
}

def validate(value, schema, path="arguments"):
    kind = schema.get("type")
    types = {"object": dict, "array": list, "string": str, "integer": int}
    if kind and (not isinstance(value, types[kind]) or (kind == "integer" and isinstance(value, bool))):
        raise ValueError(f"{path} must be {kind}")
    if "enum" in schema and value not in schema["enum"]:
        raise ValueError(f"{path} must be one of {schema['enum']}")
    if kind == "object":
        for key in schema.get("required", []):
            if key not in value:
                raise ValueError(f"{path}.{key} is required")
        for key, item in value.items():
            if key in schema.get("properties", {}):
                validate(item, schema["properties"][key], f"{path}.{key}")
            elif schema.get("additionalProperties") is False:
                raise ValueError(f"{path}.{key} is not supported")
    elif kind == "array":
        if len(value) < schema.get("minItems", 0):
            raise ValueError(f"{path} must have supporting provenance")
        for i, item in enumerate(value):
            validate(item, schema["items"], f"{path}[{i}]")
        if schema.get("uniqueItems") and len(value) != len(set(value)):
            raise ValueError(f"{path} must contain unique values")
    elif kind == "string":
        if schema.get("minLength") and not value.strip():
            raise ValueError(f"{path} must not be blank")
        if "pattern" in schema and not re.fullmatch(schema["pattern"], value):
            raise ValueError(f"{path} has invalid format")
    elif kind == "integer":
        if not schema.get("minimum", value) <= value <= schema.get("maximum", value):
            raise ValueError(f"{path} is outside supported bounds")
