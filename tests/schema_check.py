"""Offline checker: validates documents against the $jsonSchema validators in schemas.py.
Used in tests because the mock database doesn't enforce validators. Real MongoDB does this itself."""
import datetime, decimal, re
from bson import ObjectId, Decimal128

TYPES = {
    "string": str, "bool": bool, "date": datetime.datetime, "objectId": ObjectId,
    "int": int, "long": int, "double": float, "decimal": (Decimal128, decimal.Decimal),
    "object": dict, "array": list, "null": type(None),
}

def _is(v, t):
    if t in ("int", "long") and isinstance(v, bool):
        return False
    return isinstance(v, TYPES[t])

def errors(doc, schema, path="$"):
    out = []
    if "bsonType" in schema:
        ts = schema["bsonType"] if isinstance(schema["bsonType"], list) else [schema["bsonType"]]
        if not any(_is(doc, t) for t in ts):
            return [f"{path}: expected {ts}, got {type(doc).__name__} {doc!r:.40}"]
    if "enum" in schema and doc not in schema["enum"]:
        out.append(f"{path}: {doc!r} not in {schema['enum']}")
    if isinstance(doc, (int, float)) and not isinstance(doc, bool):
        if "minimum" in schema and doc < schema["minimum"]:
            out.append(f"{path}: {doc} < {schema['minimum']}")
        if "maximum" in schema and doc > schema["maximum"]:
            out.append(f"{path}: {doc} > {schema['maximum']}")
    if isinstance(doc, str):
        if "minLength" in schema and len(doc) < schema["minLength"]:
            out.append(f"{path}: too short")
        if "pattern" in schema and not re.search(schema["pattern"], doc):
            out.append(f"{path}: {doc!r} doesn't match {schema['pattern']}")
    if isinstance(doc, dict):
        for r in schema.get("required", []):
            if r not in doc:
                out.append(f"{path}: missing required '{r}'")
        for k, sub in schema.get("properties", {}).items():
            if k in doc:
                out += errors(doc[k], sub, f"{path}.{k}")
    if isinstance(doc, list):
        if "minItems" in schema and len(doc) < schema["minItems"]:
            out.append(f"{path}: fewer than {schema['minItems']} items")
        if "maxItems" in schema and len(doc) > schema["maxItems"]:
            out.append(f"{path}: more than {schema['maxItems']} items")
        if "items" in schema:
            for i, v in enumerate(doc):
                out += errors(v, schema["items"], f"{path}[{i}]")
    return out
