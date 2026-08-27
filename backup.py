#!/usr/bin/env python3
"""
Einfache Backup-Anwendung
Kopiert alle Dateien aus einem Quellverzeichnis in ein Zielverzeichnis
und protokolliert alle Vorgänge sowie eventuelle Fehler in 'log.txt'.
"""

from __future__ import annotations

import datetime
import shutil
from pathlib import Path

# Standard-Konfiguration
SOURCE_DIRECTORY = Path("./source")
TARGET_DIRECTORY = Path("./backup")
LOG_FILE = Path("log.txt")


def log_message(log_file: Path, message: str) -> None:
    """Schreibt einen Eintrag mit aktuellem Zeitstempel in die Log-Datei."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_file.parent.mkdir(parents=True, exist_ok=True)
    with log_file.open("a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")


def backup_files(
    source: Path | str = SOURCE_DIRECTORY,
    target: Path | str = TARGET_DIRECTORY,
    log_path: Path | str = LOG_FILE,
) -> dict[str, int]:
    """
    Kopiert alle Dateien aus dem Quellverzeichnis in das Zielverzeichnis.
    Erstellt das Zielverzeichnis automatisch, falls es nicht existiert.
    Protokolliert jeden Kopiervorgang und eventuelle Fehler in der Log-Datei.
    """
    src_dir = Path(source).resolve()
    target_dir = Path(target).resolve()
    log_file = Path(log_path).resolve()

    stats = {"copied": 0, "failed": 0, "skipped": 0}

    # Sicherstellen, dass das Quellverzeichnis existiert
    if not src_dir.exists() or not src_dir.is_dir():
        log_message(
            log_file,
            f"FEHLER: Quellverzeichnis existiert nicht oder ist kein Ordner: {src_dir}",
        )
        return stats

    # Zielverzeichnis automatisch erstellen, falls es noch nicht existiert
    try:
        target_dir.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        log_message(
            log_file,
            f"FEHLER: Zielverzeichnis konnte nicht erstellt werden ({target_dir}): {e}",
        )
        stats["failed"] += 1
        return stats

    log_message(log_file, f"START: Backup von '{src_dir}' nach '{target_dir}'")

    # Alle Dateien im Quellordner durchgehen
    for item in sorted(src_dir.iterdir()):
        if not item.is_file():
            stats["skipped"] += 1
            continue

        destination = target_dir / item.name

        # Kopiervorgang mit try-except absichern
        try:
            shutil.copy2(item, destination)
            log_message(log_file, f"ERFOLGREICH: '{item.name}' nach '{destination}' kopiert.")
            print(f"Kopiert: {item.name}")
            stats["copied"] += 1
        except Exception as error:
            log_message(
                log_file,
                f"FEHLER: Datei '{item.name}' konnte nicht kopiert werden: {error}",
            )
            print(f"Fehler bei: {item.name} ({error})")
            stats["failed"] += 1

    log_message(
        log_file,
        f"ENDE: Backup abgeschlossen (Kopiert: {stats['copied']}, Fehler: {stats['failed']}, Übersprungen: {stats['skipped']})",
    )
    return stats


if __name__ == "__main__":
    backup_files()
