from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    data_dir = root / "data"
    out_dir = root / "output"

    # Ensure directories exist
    (data_dir).mkdir(parents=True, exist_ok=True)
    (out_dir / "manifests").mkdir(parents=True, exist_ok=True)
    (out_dir / "logs").mkdir(parents=True, exist_ok=True)

    run_ts = utc_now_iso()

    # Minimal proof-of-run artifact
    manifest = {
        "run_utc": run_ts,
        "status": "ok",
        "note": "Initial scaffold run. Official fetchers will be added next."
    }

    (out_dir / "manifests" / f"manifest_{run_ts.replace(':','-')}.json").write_text(
        json.dumps(manifest, indent=2),
        encoding="utf-8"
    )

    (out_dir / "logs" / f"runlog_{run_ts.replace(':','-')}.txt").write_text(
        f"[{run_ts}] Pipeline executed successfully.\n",
        encoding="utf-8"
    )


if __name__ == "__main__":
    main()
