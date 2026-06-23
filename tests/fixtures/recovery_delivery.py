from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class CapturingRecoveryDelivery:
    messages: list[tuple[str, str]] = field(default_factory=list)
    fail: bool = False

    def send(self, recipient: str, link: str) -> None:
        if self.fail:
            raise RuntimeError("delivery unavailable")
        self.messages.append((recipient, link))
