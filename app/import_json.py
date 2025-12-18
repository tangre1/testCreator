import json
from pathlib import Path

from app.services.import_bank import import_bank_from_dict


def import_bank(json_path: Path):
    if not json_path.exists():
        raise FileNotFoundError(f"File not found: {json_path}")

    data = json.loads(json_path.read_text(encoding="utf-8"))
    bank_key = json_path.stem

    import_bank_from_dict(data, bank_key)


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        raise SystemExit("Usage: python -m app.import_json <path_to_json>")

    import_bank(Path(sys.argv[1]))
