STOP_WORDS = ("stop", "unsubscribe", "don't message", "do not contact", "remove me", "opt out", "opt-out")


def is_opt_out(text: str | None) -> bool:
    if not text:
        return False
    lowered = text.lower()
    return any(word in lowered for word in STOP_WORDS)
