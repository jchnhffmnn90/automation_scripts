#!/usr/bin/env python3
"""
File Organizer CLI Script
Sortiert Dateien in einem Verzeichnis nach Dateityp und Alter in Unterordner.
"""

from __future__ import annotations

import argparse
import datetime
import logging
import shutil
import sys
from pathlib import Path

DEFAULT_CATEGORIES: dict[str, list[str]] = {
    "Dokumente": [
        ".pdf",
        ".docx",
        ".doc",
        ".xlsx",
        ".xls",
        ".pptx",
        ".txt",
        ".csv",
        ".odt",
    ],
    "Bilder": [".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp", ".bmp", ".tiff"],
    "Audio": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a"],
    "Videos": [".mp4", ".mkv", ".mov", ".avi", ".webm"],
    "Archive": [".zip", ".tar.gz", ".tgz", ".tar", ".gz", ".7z", ".rar"],
    "Code": [".py", ".js", ".ts", ".html", ".css", ".json", ".xml", ".sh", ".sql"],
}

IGNORED_EXTENSIONS = {".crdownload", ".tmp", ".part", ".downloading"}


def parse_arguments(args: list[str] | None = None) -> argparse.Namespace:
    """Parst Kommandozeilenargumente."""
    parser = argparse.ArgumentParser(
        description="Organisiert Dateien in einem Quellordner in thematische Unterordner."
    )
    parser.add_argument(
        "source",
        nargs="?",
        default=".",
        help="Pfad zum Quellverzeichnis (Standard: aktuelles Verzeichnis)",
    )
    parser.add_argument(
        "--target",
        "-t",
        default=None,
        help="Zielverzeichnis (Standard: dasselbe wie Quellverzeichnis)",
    )
    parser.add_argument(
        "--older-than",
        type=int,
        default=None,
        metavar="DAYS",
        help="Nur Dateien verschieben, die älter als X Tage sind",
    )
    parser.add_argument(
        "--dry-run", "-n", action="store_true", help="Simulation ausführen"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Ausführliche Log-Ausgaben aktivieren",
    )
    return parser.parse_args(args)


def get_category_for_file(
    file_path: Path, categories: dict[str, list[str]] | None = None
) -> str | None:
    """
    Ermittelt die passende Kategorie für eine Datei.
    Unterstützt auch mehrteilige Dateiendungen wie '.tar.gz'.
    Gibt None zurück wenn die Datei ignoriert werden soll.
    """
    cat_map = categories if categories is not None else DEFAULT_CATEGORIES
    name_lower = file_path.name.lower()
    for ignored in IGNORED_EXTENSIONS:
        if name_lower.endswith(ignored):
            return None
    for category, extensions in cat_map.items():
        for ext in sorted(extensions, key=len, reverse=True):
            if name_lower.endswith(ext.lower()):
                return category
    return "Sonstiges"


def resolve_collision(
    target_dir: Path,
    filename: str,
    categories: dict[str, list[str]] | None = None,
) -> Path:
    """
    Erzeugt einen eindeutigen Zieldateinamen bei Namenskollisionen.
    Beispiel: datei.pdf -> datei_1.pdf, datei_2.pdf
    """
    candidate = target_dir / filename
    if not candidate.exists():
        return candidate

    path_obj = Path(filename)
    stem = path_obj.stem
    suffix = path_obj.suffix

    cat_map = categories if categories is not None else DEFAULT_CATEGORIES
    compound_extensions = [
        ext.lower()
        for exts in cat_map.values()
        for ext in exts
        if ext.count(".") > 1
    ]

    for comp_ext in sorted(compound_extensions, key=len, reverse=True):
        if filename.lower().endswith(comp_ext):
            stem = filename[: -len(comp_ext)]
            suffix = filename[-len(comp_ext) :]
            break

    counter = 1
    while candidate.exists():
        candidate = target_dir / f"{stem}_{counter}{suffix}"
        counter += 1
    return candidate


def is_older_than(
    file_path: Path, days: int, reference_time: datetime.datetime | None = None
) -> bool:
    """Prüft, ob die Datei älter als angegebene Anzahl an Tagen ist."""
    try:
        mtime = datetime.datetime.fromtimestamp(
            file_path.stat().st_mtime, tz=datetime.timezone.utc
        )
        now = reference_time or datetime.datetime.now(tz=datetime.timezone.utc)
        return (now - mtime).days >= days
    except (OSError, FileNotFoundError):
        return False


def organize_directory(
    source_dir: Path,
    target_dir: Path | None = None,
    older_than_days: int | None = None,
    dry_run: bool = False,
    categories: dict[str, list[str]] | None = None,
) -> dict[str, int]:
    """
    Organisiert alle Dateien in source_dir in die Zielkategorien.
    Gibt eine Statistik über verschobene, übersprungene und ignorierten Dateien zurück.
    """
    src = Path(source_dir).resolve()
    dst = Path(target_dir).resolve() if target_dir else src
    stats = {"moved": 0, "skipped": 0, "ignored": 0}
    if not src.exists() or not src.is_dir():
        logging.error(f"Quellverzeichnis existiert nicht: {src}")
        return stats

    for item in sorted(src.iterdir()):
        if not item.is_file():
            continue
        if older_than_days is not None and not is_older_than(item, older_than_days):
            logging.debug(f"Übersprungen (zu neu): {item.name}")
            stats["skipped"] += 1
            continue
        category = get_category_for_file(item, categories)
        if category is None:
            logging.debug(f"Ignoriert (temporäre Datei): {item.name}")
            stats["ignored"] += 1
            continue
        category_dir = dst / category
        destination = resolve_collision(category_dir, item.name, categories=categories)
        action_prefix = "[DRY-RUN] Würde verschieben" if dry_run else "Verschiebe"
        logging.info(f"{action_prefix}: {item.name} -> {category}/{destination.name}")
        if not dry_run:
            category_dir.mkdir(parents=True, exist_ok=True)
            try:
                shutil.move(item, destination)
                stats["moved"] += 1
            except OSError as e:
                logging.error(f"Fehler beim Verschieben von: {item.name}: {e}")
                stats["skipped"] += 1
        else:
            stats["moved"] += 1

    return stats


def main(args: list[str] | None = None) -> int:
    parsed_args = parse_arguments(args)
    log_level = logging.DEBUG if parsed_args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )
    source_path = Path(parsed_args.source)
    target_path = Path(parsed_args.target) if parsed_args.target else None
    logging.info(f"Starte Organisation von: {source_path.resolve()}")

    stats = organize_directory(
        source_dir=source_path,
        target_dir=target_path,
        older_than_days=parsed_args.older_than,
        dry_run=parsed_args.dry_run,
    )

    logging.info(
        f"Fertig! Verschoben: {stats['moved']}, Übersprungen: {stats['skipped']}, Ignoriert: {stats['ignored']}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
