#!/usr/bin/env python3
"""
Test Suite für den File Organizer (Unit- und Integrationstests)
"""

import datetime
import os
import tempfile
import unittest
from pathlib import Path

from organizer import (
    DEFAULT_CATEGORIES,
    get_category_for_file,
    is_older_than,
    organize_directory,
    resolve_collision,
)


class TestCategoryDetection(unittest.TestCase):
    """Unit-Tests für die Dateityp- und Kategorieerkennung."""

    def test_standard_extensions(self):
        self.assertEqual(get_category_for_file(Path("dokument.pdf")), "Dokumente")
        self.assertEqual(get_category_for_file(Path("foto.PNG")), "Bilder")
        self.assertEqual(get_category_for_file(Path("song.mp3")), "Audio")
        self.assertEqual(get_category_for_file(Path("script.py")), "Code")

    def test_compound_extensions(self):
        self.assertEqual(get_category_for_file(Path("archiv.tar.gz")), "Archive")

    def test_ignored_extensions(self):
        self.assertIsNone(get_category_for_file(Path("download.crdownload")))
        self.assertIsNone(get_category_for_file(Path("tempfile.tmp")))
        self.assertIsNone(get_category_for_file(Path("partial.part")))

    def test_unknown_extension_fallback(self):
        self.assertEqual(get_category_for_file(Path("unbekannt.xyz123")), "Sonstiges")


class TestCollisionResolution(unittest.TestCase):
    """Unit-Tests für die Behandlung von Namenskollisionen."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.path = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_no_collision(self):
        res = resolve_collision(self.path, "neu.txt")
        self.assertEqual(res, self.path / "neu.txt")

    def test_single_collision(self):
        (self.path / "neu.txt").touch()
        res = resolve_collision(self.path, "neu.txt")
        self.assertEqual(res, self.path / "neu_1.txt")

    def test_multiple_collisions(self):
        (self.path / "neu.txt").touch()
        (self.path / "neu_1.txt").touch()
        (self.path / "neu_2.txt").touch()
        res = resolve_collision(self.path, "neu.txt")
        self.assertEqual(res, self.path / "neu_3.txt")

    def test_compound_extension_collision(self):
        (self.path / "archiv.tar.gz").touch()
        res = resolve_collision(self.path, "archiv.tar.gz")
        self.assertEqual(res, self.path / "archiv_1.tar.gz")

    def test_custom_compound_extension_collision(self):
        custom_categories = {"CustomArchive": [".tar.bz2"]}
        (self.path / "backup.tar.bz2").touch()
        res = resolve_collision(
            self.path, "backup.tar.bz2", categories=custom_categories
        )
        self.assertEqual(res, self.path / "backup_1.tar.bz2")

    def test_dotted_filename_collision(self):
        (self.path / "report.2024.pdf").touch()
        res = resolve_collision(self.path, "report.2024.pdf")
        self.assertEqual(res, self.path / "report.2024_1.pdf")


class TestDateAgeFilter(unittest.TestCase):
    """Unit-Tests für die Altersprüfung."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_file = Path(self.temp_dir.name) / "test.txt"
        self.test_file.touch()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_age_comparison(self):
        now = datetime.datetime.now(tz=datetime.timezone.utc)
        # Datei soeben erstellt -> nicht älter als 5 Tage
        self.assertFalse(is_older_than(self.test_file, 5, reference_time=now))

        # Virtuell 10 Tage in der Zukunft testen
        future = now + datetime.timedelta(days=10)
        self.assertTrue(is_older_than(self.test_file, 5, reference_time=future))


class TestOrganizeIntegration(unittest.TestCase):
    """Integrationstests für den gesamten Organisations-Workflow."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.src = Path(self.temp_dir.name) / "downloads"
        self.src.mkdir()

        # Testdateien anlegen
        (self.src / "rechnung.pdf").write_text("PDF Inhalt")
        (self.src / "urlaub.jpg").write_text("Bild Inhalt")
        (self.src / "archiv.zip").write_text("Zip Inhalt")
        (self.src / "unvollstaendig.crdownload").write_text("Download läuft...")
        (self.src / "custom.xyz").write_text("Sonstiges")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_dry_run_does_not_modify_files(self):
        stats = organize_directory(self.src, dry_run=True)
        self.assertEqual(stats["moved"], 4)
        self.assertEqual(stats["ignored"], 1)

        # Quelldateien müssen unverändert vorhanden sein
        self.assertTrue((self.src / "rechnung.pdf").exists())
        self.assertFalse((self.src / "Dokumente").exists())

    def test_full_organization(self):
        stats = organize_directory(self.src, dry_run=False)
        self.assertEqual(stats["moved"], 4)
        self.assertEqual(stats["ignored"], 1)

        # Prüfen, ob Unterordner und Dateien existieren
        self.assertTrue((self.src / "Dokumente" / "rechnung.pdf").exists())
        self.assertTrue((self.src / "Bilder" / "urlaub.jpg").exists())
        self.assertTrue((self.src / "Archive" / "archiv.zip").exists())
        self.assertTrue((self.src / "Sonstiges" / "custom.xyz").exists())

        # Ignorierte Datei verbleibt am Ursprungsort
        self.assertTrue((self.src / "unvollstaendig.crdownload").exists())

        # Ursprüngliche Dateien sollten verschoben sein
        self.assertFalse((self.src / "rechnung.pdf").exists())


if __name__ == "__main__":
    unittest.main()
