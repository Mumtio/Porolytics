from datetime import datetime

def iso_to_ms(iso_str: str) -> int:
    try:
        # GRID timestamps are typically ISO 8601 with Z for UTC
        return int(datetime.fromisoformat(iso_str.replace("Z", "+00:00")).timestamp() * 1000)
    except Exception:
        return 0
