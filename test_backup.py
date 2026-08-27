#!/usr/bin/env python3
"""
Test Suite für das Backup-Skript
"""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from backup import (
    backup_files,
    log_message,
)


class TestBackupScript(unittest.TestCase):
    """Tests für die Backup-Funktionalität und Protokollierung."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base_path = Path(self.temp_dir.name)
        self.source_dir = self.base_path / "source"
        self.source_dir.mkdir()
        self.target_dir = self.base_path / "backup"
        self.log_file = self.base_path / "log.txt"

        # Beispiel-Dateien anlegen
        (self.source_dir / "dokument.txt").write_text("Inhalt A")
        (self.source_dir / "tabelle.csv").write_text("1,2,3")
        (self.source_dir / "bild.png").write_text("Binary")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_log_message_creates_file_with_timestamp(self):
        log_path = self.base_path / "sub" / "custom_log.txt"
        log_message(log_path, "Testmeldung")
        self.assertTrue(log_path.exists())
        content = log_path.read_text(encoding="utf-8")
        self.assertIn("Testmeldung", content)
        self.assertRegex(content, r"\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\]")

    def test_backup_creates_target_dir_and_copies_files(self):
        # Zielverzeichnis existiert vor dem Aufruf nicht
        self.assertFalse(self.target_dir.exists())

        stats = backup_files(
            source=self.source_dir,
            target=self.target_dir,
            log_path=self.log_file,
        )

        # Überprüfen der Rückgabewerte
        self.assertEqual(stats["copied"], 3)
        self.assertEqual(stats["failed"], 0)

        # Zielverzeichnis und Dateien müssen existieren
        self.assertTrue(self.target_dir.exists())
        self.assertTrue((self.target_dir / "dokument.txt").exists())
        self.assertTrue((self.target_dir / "tabelle.csv").exists())
        self.assertTrue((self.target_dir / "bild.png").exists())
        self.assertEqual(
            (self.target_dir / "dokument.txt").read_text(), "Inhalt A"
        )

        # Logdatei muss existieren und Kopiervorgänge enthalten
        self.assertTrue(self.log_file.exists())
        log_content = self.log_file.read_text(encoding="utf-8")
        self.assertIn("START: Backup", log_content)
        self.assertIn("ERFOLGREICH: 'dokument.txt'", log_content)
        self.assertIn("ERFOLGREICH: 'tabelle.csv'", log_content)
        self.assertIn("ERFOLGREICH: 'bild.png'", log_content)
        self.assertIn("ENDE: Backup abgeschlossen", log_content)

    def test_backup_catches_and_logs_file_copy_errors(self):
        import shutil as real_shutil

        original_copy2 = real_shutil.copy2

        def mock_copy2(src, dst):
            if "tabelle.csv" in str(src):
                raise PermissionError("Zugriff verweigert (nicht lesbar)")
            return original_copy2(src, dst)

        with patch("shutil.copy2", side_effect=mock_copy2):
            stats = backup_files(
                source=self.source_dir,
                target=self.target_dir,
                log_path=self.log_file,
            )

        self.assertEqual(stats["copied"], 2)
        self.assertEqual(stats["failed"], 1)
        self.assertTrue((self.target_dir / "dokument.txt").exists())
        self.assertFalse((self.target_dir / "tabelle.csv").exists())

        # Fehlerprotokollierung im Log prüfen
        log_content = self.log_file.read_text(encoding="utf-8")
        self.assertIn("FEHLER: Datei 'tabelle.csv' konnte nicht kopiert werden", log_content)
        self.assertIn("Zugriff verweigert", log_content)

    def test_nonexistent_source_directory_logs_error(self):
        nonexistent = self.base_path / "nicht_vorhanden"
        stats = backup_files(
            source=nonexistent,
            target=self.target_dir,
            log_path=self.log_file,
        )
        self.assertEqual(stats["copied"], 0)
        self.assertTrue(self.log_file.exists())
        self.assertIn("FEHLER: Quellverzeichnis existiert nicht", self.log_file.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
