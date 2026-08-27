#!/usr/bin/env python3
"""
Simple Backup Utility CLI Script
Copies files from a source directory to a destination backup directory and logs operations.
"""

from __future__ import annotations

import argparse
import datetime
import logging
import shutil
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

DEFAULT_LOG_FILE = "log.txt"


def parse_arguments(args: list[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments for the backup script."""
    parser = argparse.ArgumentParser(
        prog="backup",
        description="Copies files from a source directory to a destination backup directory.",
    )
    parser.add_argument(
        "source",
        help="Path to the source directory to back up",
    )
    parser.add_argument(
        "target",
        help="Path to the destination backup directory",
    )
    parser.add_argument(
        "--log-file",
        "-l",
        default=DEFAULT_LOG_FILE,
        help="Path to the log file (default: log.txt)",
    )
    parser.add_argument(
        "--dry-run",
        "-n",
        action="store_true",
        help="Simulate the backup without actually copying files",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output to stdout",
    )
    return parser.parse_args(args)


def write_log_entry(log_file_path: Path, message: str) -> None:
    """
    Appends a timestamped log entry to the specified log file.
    Creates parent directories for the log file if necessary.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] {message}\n"
    log_file_path.parent.mkdir(parents=True, exist_ok=True)
    with log_file_path.open("a", encoding="utf-8") as f:
        f.write(log_line)


def run_backup(
    source_dir: Path | str,
    target_dir: Path | str,
    log_file: Path | str = DEFAULT_LOG_FILE,
    dry_run: bool = False,
) -> dict[str, int]:
    """
    Copies all files from source_dir to target_dir and logs each operation into log_file.
    Catches errors with try-except blocks and logs them accordingly.

    Returns:
        dict[str, int]: Statistics on copied, failed, and skipped items.
    """
    src = Path(source_dir).resolve()
    dst = Path(target_dir).resolve()
    log_path = Path(log_file).resolve()

    stats = {"copied": 0, "failed": 0, "skipped": 0}

    if not src.exists() or not src.is_dir():
        error_msg = f"ERROR: Source directory does not exist or is not a directory: {src}"
        logger.error(error_msg)
        write_log_entry(log_path, error_msg)
        return stats

    # Ensure destination directory exists or create it automatically
    try:
        if not dry_run:
            dst.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        error_msg = f"ERROR: Could not create target directory {dst}: {e}"
        logger.error(error_msg)
        write_log_entry(log_path, error_msg)
        stats["failed"] += 1
        return stats

    write_log_entry(
        log_path,
        f"START: Backup from '{src}' to '{dst}'{' [DRY-RUN]' if dry_run else ''}",
    )

    for item in sorted(src.iterdir()):
        if not item.is_file():
            stats["skipped"] += 1
            continue

        target_file = dst / item.name
        action_desc = f"Copying '{item.name}' -> '{target_file}'"

        if dry_run:
            logger.info(f"[DRY-RUN] {action_desc}")
            write_log_entry(log_path, f"[DRY-RUN] SUCCESS: {action_desc}")
            stats["copied"] += 1
            continue

        try:
            # Copy file with metadata preserved
            shutil.copy2(item, target_file)
            success_msg = f"SUCCESS: Copied '{item.name}' to '{target_file}'"
            logger.info(success_msg)
            write_log_entry(log_path, success_msg)
            stats["copied"] += 1
        except (OSError, PermissionError, shutil.Error) as e:
            error_msg = f"ERROR: Failed to copy '{item.name}': {e}"
            logger.error(error_msg)
            write_log_entry(log_path, error_msg)
            stats["failed"] += 1

    summary_msg = (
        f"FINISHED: Copied: {stats['copied']}, Failed: {stats['failed']}, "
        f"Skipped: {stats['skipped']}"
    )
    logger.info(summary_msg)
    write_log_entry(log_path, summary_msg)
    return stats


def main(args: list[str] | None = None) -> int:
    """Main CLI entrypoint."""
    parsed_args = parse_arguments(args)
    log_level = logging.DEBUG if parsed_args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )

    logger.info(f"Starting backup from '{parsed_args.source}' to '{parsed_args.target}'")
    stats = run_backup(
        source_dir=parsed_args.source,
        target_dir=parsed_args.target,
        log_file=parsed_args.log_file,
        dry_run=parsed_args.dry_run,
    )
    return 1 if stats["failed"] > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
