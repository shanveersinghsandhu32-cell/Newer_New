# utils.py
import hashlib
from typing import Any
import json

def sha256_of_string(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()

def pretty(obj: Any) -> str:
    try:
        return json.dumps(obj, indent=2, sort_keys=True)
    except Exception:
        return str(obj)
