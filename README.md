# Automation Scripts

A curated collection of modular, production-ready Python automation scripts designed to streamline everyday workflows, file management, and system administration tasks.

Built with modern Python practices, type safety, zero external runtime dependencies, and comprehensive unit/integration test coverage.

---

## Repository Structure

```text
.
├── organizer.py        # CLI file organization tool
├── test_organizer.py   # Test suite for organizer.py (unit & integration tests)
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
python3 organizer.py

# Organize a specific source folder into a separate target directory
python3 organizer.py /path/to/source --target /path/to/organized

# Dry-run simulation (no files will be moved)
python3 organizer.py /path/to/downloads --dry-run --verbose

# Move only files older than 30 days
python3 organizer.py /path/to/downloads --older-than 30
```

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

The repository includes a comprehensive test suite covering unit behavior (extension parsing, collision resolution, timestamp math) and full end-to-end integration workflows using isolated temporary environments.

Run the test suite using Python's built-in `unittest` runner:

```bash
python3 -m unittest test_organizer.py -v
```

---

## Development Standards & Architecture

- **Modern Python:** Full type hints (`typing` / modern standard collections), `pathlib.Path` for cross-platform compatibility, and clean exception handling.
- **Defensive Design:** Collision prevention, idempotent execution, and non-destructive dry-run capabilities.
- **Maintainability:** Modular, single-responsibility functions designed for reusability as both CLI scripts and importable modules.

---

## License

This project is licensed under the terms specified in the [LICENSE](LICENSE) file.
