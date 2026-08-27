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

### 2. Backup Utility (`backup.py`)

A reliable backup utility that copies all files from a source directory to a target directory with detailed operation logging, timestamp tracking, and resilient error handling.

#### Key Features
- **Automatic Directory Creation:** Automatically creates the target directory (and any necessary parent directories) if it does not already exist.
- **Detailed Operation Logging:** Records each file copy process with timestamp, source filename, and target destination in `log.txt`.
- **Resilient Error Handling:** Catches read/write and permission errors using `try-except` blocks, logs the failure details, and continues backing up remaining files.
- **Dry-Run Simulation:** Preview backup operations without copying any files (`--dry-run`).
- **Configurable Log Destination:** Choose a custom log file location (`--log-file`).

#### CLI Usage

```bash
# Run backup from source folder to target directory
backup /path/to/source /path/to/backup

# Run backup with custom log file location
backup /path/to/source /path/to/backup --log-file /var/log/backup.txt

# Simulate backup in dry-run mode
backup /path/to/source /path/to/backup --dry-run --verbose
```

#### Command-Line Arguments

| Argument | Description | Default |
| :--- | :--- | :--- |
| `source` | Source directory path to back up | *(Required)* |
| `target` | Destination backup directory path | *(Required)* |
| `-l`, `--log-file` | Path to log file for operation records | `log.txt` |
| `-n`, `--dry-run` | Simulate operations without copying files | `False` |
| `-v`, `--verbose` | Enable debug logging output | `False` |

#### Command-Line Arguments

| Argument | Description | Default |
| :--- | :--- | :--- |
| `source` | Source directory path | `.` (current directory) |
| `-t`, `--target` | Destination directory path | Same as `source` |
| `--older-than DAYS` | Only move files older than specified days | `None` (all files) |
| `-n`, `--dry-run` | Perform a trial run with no filesystem changes | `False` |
| `-v`, `--verbose` | Enable debug logging output | `False` |

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
