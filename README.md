# Automation Scripts

A curated collection of modular, production-ready Python automation scripts designed to streamline everyday workflows, file management, and system administration tasks.

Built with modern Python practices, type safety, zero external runtime dependencies, and comprehensive unit/integration test coverage.

---

## Repository Structure

```text
.
├── backup.py           # CLI backup application with operation & error logging
├── test_backup.py      # Test suite for backup.py
├── organizer.py        # CLI file organization tool
├── test_organizer.py   # Test suite for organizer.py (unit & integration tests)
├── pyproject.toml      # Project packaging and metadata configuration
├── LICENSE             # Project license
└── README.md           # Project documentation
```

---

## Scripts & Tools

### 1. File Organizer (`organizer.py`)

A fast and configurable CLI utility to organize cluttered directories (such as `Downloads` or `Desktop`) into categorized subfolders based on file types and modification dates.

#### Key Features
- **Smart Category Detection:** Automatically categorizes files into *Dokumente*, *Bilder*, *Audio*, *Videos*, *Archive*, *Code*, and *Sonstiges*.
- **Compound Extension Support:** Correctly recognizes multi-part extensions such as `.tar.gz` and `.tgz`.
- **Ignored Extension Filtering:** Automatically excludes temporary and incomplete files (e.g. `.crdownload`, `.part`, `.tmp`).
- **Collision Resolution:** Automatically avoids overwriting existing files by appending sequential numeric suffixes (e.g., `report.pdf` &rarr; `report_1.pdf`).
- **Age-Based Filtering:** Move only files older than a specified number of days (`--older-than`).
- **Safe Dry-Run Mode:** Simulate operations before making any file system modifications (`--dry-run`).
- **Configurable Logging:** Detailed verbose output support (`--verbose`).
- **Pure Standard Library:** No third-party dependencies required.

#### CLI Usage

```bash
# Organize current working directory in-place
organize

# Organize a specific source folder into a separate target directory
organize /path/to/source --target /path/to/organized

# Dry-run simulation (no files will be moved)
organize /path/to/downloads --dry-run --verbose

# Move only files older than 30 days
organize /path/to/downloads --older-than 30
```

---

### 2. Simple Backup Script (`backup.py`)

A clean, straightforward backup script that copies all files from a defined source folder to a destination backup folder with automatic folder creation and detailed operation & error logging.

#### Key Features
- **Automatic Directory Creation:** Creates the target backup directory automatically if it does not exist.
- **Timestamped Operation Logging:** Records each copied file (timestamp and filename) in `log.txt`.
- **Try-Except Error Handling:** Catches read and file system errors gracefully without interrupting the entire process.
- **Configurable Paths:** Custom source, target, and log paths can be configured directly or passed to `backup_files()`.

#### Usage

```bash
# Run backup with default directories (./source -> ./backup)
python3 backup.py
```

Or call programmatically in Python:

```python
from backup import backup_files

backup_files(source="./my_documents", target="./my_backup", log_path="./log.txt")
```

---

## Testing & Quality Assurance

The repository includes a comprehensive test suite covering all tools with unit behavior and full end-to-end integration workflows using isolated temporary environments.

Run all tests using Python's built-in `unittest` discover:

```bash
python3 -m unittest discover -v -s . -p "test_*.py"
```

---

## Development Standards & Architecture

- **Modern Python:** Full type hints (`typing` / modern standard collections), `pathlib.Path` for cross-platform compatibility, and clean exception handling.
- **Defensive Design:** Collision prevention, idempotent execution, and non-destructive dry-run capabilities.
- **Maintainability:** Modular, single-responsibility functions designed for reusability as both CLI scripts and importable modules.

---

## License

This project is licensed under the terms specified in the [LICENSE](LICENSE) file.
