from __future__ import annotations

from hashlib import sha256
import json


class HashChainAuditLog:
    """Tiny tamper-evident in-memory ledger for the reference implementation."""

    def __init__(self) -> None:
        self.records: list[dict] = []
        self._head = "0" * 64

    @property
    def head(self) -> str:
        return self._head

    def append(self, payload: dict) -> str:
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
        digest = sha256((self._head + canonical).encode()).hexdigest()
        self.records.append({"previous": self._head, "digest": digest, "payload": payload})
        self._head = digest
        return digest

    def verify(self) -> bool:
        previous = "0" * 64
        for record in self.records:
            canonical = json.dumps(record["payload"], sort_keys=True, separators=(",", ":"), default=str)
            expected = sha256((previous + canonical).encode()).hexdigest()
            if record["previous"] != previous or record["digest"] != expected:
                return False
            previous = expected
        return True
