#!/usr/bin/env python3
"""Create a consistent SQLite backup using the online backup API.

The default database path matches ``app/core/config.py``. Run it from the
project root (or pass absolute paths):

    python3 scripts/backup_db.py
    python3 scripts/backup_db.py --source data/match_combat.db \
        --output-dir /var/backups/match_combat --keep 14
"""

from __future__ import annotations

import argparse
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Backup the SQLite database")
    parser.add_argument(
        "--source",
        default="data/match_combat.db",
        help="Path to the SQLite database (default: data/match_combat.db)",
    )
    parser.add_argument(
        "--output-dir",
        default="backups",
        help="Directory for the backup files (default: backups)",
    )
    parser.add_argument(
        "--keep",
        type=int,
        default=7,
        help="Number of backups to keep, 0 disables pruning (default: 7)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source = Path(args.source).expanduser()

    if not source.is_file():
        raise SystemExit(f"Database not found: {source}")

    output_dir = Path(args.output_dir).expanduser()
    output_dir.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    target = output_dir / f"{source.stem}_{stamp}.db"

    source_conn = sqlite3.connect(source)
    target_conn = sqlite3.connect(target)
    try:
        source_conn.backup(target_conn)
    finally:
        target_conn.close()
        source_conn.close()

    if args.keep > 0:
        backups = sorted(output_dir.glob(f"{source.stem}_*.db"))
        for old_backup in backups[: -args.keep]:
            old_backup.unlink()

    print(target)


if __name__ == "__main__":
    main()
