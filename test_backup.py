#!/usr/bin/env python3
"""
Test Suite for Backup Script (Unit and Integration Tests)
"""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from backup import (
    DEFAULT_LOG_FILE,
    parse_arguments,
    run_backup,
    write_log_entry,
)


class TestBackupArgumentParsing(unittest.TestCase):
    """Unit tests for backup CLI argument parsing."""

    def test_default_arguments(self):
        args = parse_arguments(["/src/dir", "/dst/dir"])
        self.assertEqual(args.source, "/src/dir")
        self.assertEqual(args.target, "/dst/dir")
        self.assertEqual(args.log_file, DEFAULT_LOG_FILE)
        self.assertFalse(args.dry_run)
        self.assertFalse(args.verbose)

    def test_custom_arguments(self):
        args = parse_arguments(
            ["/src", "/dst", "--log-file", "/tmp/custom.log", "--dry-run", "--verbose"]
        )
        self.assertEqual(args.source, "/src")
        self.assertEqual(args.target, "/dst")
        self.assertEqual(args.log_file, "/tmp/custom.log")
        self.assertTrue(args.dry_run)
        self.assertTrue(args.verbose)


class TestBackupIntegration(unittest.TestCase):
    """Integration and error handling tests for backup utility."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base_path = Path(self.temp_dir.name)
        self.src_dir = self.base_path / "source"
        self.src_dir.mkdir()
        self.target_dir = self.base_path / "backup_target"
        self.log_file = self.base_path / "log.txt"

        # Create sample files in source
        (self.src_dir / "document.txt").write_text("Hello World")
        (self.src_dir / "data.csv").write_text("a,b,c\n1,2,3")
        (self.src_dir / "notes.md").write_text("# Notes")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_successful_backup_creates_target_dir_and_copies_files(self):
        # Target directory does not exist initially
        self.assertFalse(self.target_dir.exists())

        stats = run_backup(
            source_dir=self.src_dir,
            target_dir=self.target_dir,
            log_file=self.log_file,
            dry_run=False,
        )

        self.assertEqual(stats["copied"], 3)
        self.assertEqual(stats["failed"], 0)
        self.assertTrue(self.target_dir.exists())
        self.assertTrue((self.target_dir / "document.txt").exists())
        self.assertTrue((self.target_dir / "data.csv").exists())
        self.assertTrue((self.target_dir / "notes.md").exists())
        self.assertEqual(
            (self.target_dir / "document.txt").read_text(), "Hello World"
        )

        # Verify log file contents
        self.assertTrue(self.log_file.exists())
        log_content = self.log_file.read_text()
        self.assertIn("START: Backup", log_content)
        self.assertIn("SUCCESS: Copied 'document.txt'", log_content)
        self.assertIn("SUCCESS: Copied 'data.csv'", log_content)
        self.assertIn("SUCCESS: Copied 'notes.md'", log_content)
        self.assertIn("FINISHED: Copied: 3, Failed: 0", log_content)

    def test_dry_run_does_not_create_files_but_logs(self):
        stats = run_backup(
            source_dir=self.src_dir,
            target_dir=self.target_dir,
            log_file=self.log_file,
            dry_run=True,
        )

        self.assertEqual(stats["copied"], 3)
        self.assertEqual(stats["failed"], 0)
        self.assertFalse(self.target_dir.exists())

        self.assertTrue(self.log_file.exists())
        log_content = self.log_file.read_text()
        self.assertIn("[DRY-RUN]", log_content)

    def test_handles_copy_error_gracefully(self):
        # Create unreadable/error-triggering file simulation via mock
        import shutil as real_shutil

        original_copy2 = real_shutil.copy2

        def mock_copy2(src, dst):
            if "data.csv" in str(src):
                raise PermissionError("Permission denied: unreadable file")
            return original_copy2(src, dst)

        with patch("shutil.copy2", side_effect=mock_copy2):
            stats = run_backup(
                source_dir=self.src_dir,
                target_dir=self.target_dir,
                log_file=self.log_file,
            )

        self.assertEqual(stats["copied"], 2)
        self.assertEqual(stats["failed"], 1)
        self.assertTrue((self.target_dir / "document.txt").exists())
        self.assertTrue((self.target_dir / "notes.md").exists())
        self.assertFalse((self.target_dir / "data.csv").exists())

        # Check log file contains the error
        log_content = self.log_file.read_text()
        self.assertIn("ERROR: Failed to copy 'data.csv'", log_content)
        self.assertIn("Permission denied", log_content)

    def test_nonexistent_source_directory(self):
        nonexistent = self.base_path / "does_not_exist"
        stats = run_backup(
            source_dir=nonexistent,
            target_dir=self.target_dir,
            log_file=self.log_file,
        )
        self.assertEqual(stats["copied"], 0)
        self.assertTrue(self.log_file.exists())
        self.assertIn(
            "Source directory does not exist", self.log_file.read_text()
        )

    def test_write_log_entry(self):
        log_path = self.base_path / "subdir" / "test_log.txt"
        write_log_entry(log_path, "Test entry")
        self.assertTrue(log_path.exists())
        self.assertIn("Test entry", log_path.read_text())

    def test_subdirectories_are_skipped(self):
        subdir = self.src_dir / "nested_folder"
        subdir.mkdir()
        (subdir / "inner.txt").write_text("inner")

        stats = run_backup(
            source_dir=self.src_dir,
            target_dir=self.target_dir,
            log_file=self.log_file,
        )

        self.assertEqual(stats["copied"], 3)
        self.assertEqual(stats["skipped"], 1)
        self.assertFalse((self.target_dir / "nested_folder").exists())


if __name__ == "__main__":
    unittest.main()
