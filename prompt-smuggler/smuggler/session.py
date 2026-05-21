import os
import json
import hashlib
import tempfile

SESSION_DIR = os.path.join(tempfile.gettempdir(), "prompt_smuggler_sessions")


def _session_path(session_id: str) -> str:
    os.makedirs(SESSION_DIR, exist_ok=True)
    return os.path.join(SESSION_DIR, f"{session_id}.json")


def _grammar_hash(grammar: dict) -> str:
    """Stable hash of the grammar dict so we can detect if it changed."""
    serialized = json.dumps(grammar, sort_keys=True)
    return hashlib.sha256(serialized.encode()).hexdigest()[:16]


def grammar_already_sent(session_id: str, grammar: dict) -> bool:
    """Returns True if this exact grammar was already sent in this session."""
    path = _session_path(session_id)
    if not os.path.exists(path):
        return False
    with open(path, "r") as f:
        data = json.load(f)
    return data.get("grammar_hash") == _grammar_hash(grammar)


def mark_grammar_sent(session_id: str, grammar: dict) -> None:
    """Record that the grammar header was sent for this session."""
    path = _session_path(session_id)
    with open(path, "w") as f:
        json.dump({"grammar_hash": _grammar_hash(grammar)}, f)


def clear_session(session_id: str) -> None:
    path = _session_path(session_id)
    if os.path.exists(path):
        os.remove(path)
