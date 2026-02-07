# Changelog

Log of major changes, based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [1.1.1] - 2026-02-05

## Added
- User-agent argument in tabula calls to fix/stabilize direct URL file requests
- Bug.yml issue template

## Changed
- Miscellaneous cosmetic edits to docs
- Update to request header constant param

## Removed
- tests/injuryasy_example.py script


## [1.1.0] - 2026-01-23

## Added
- Updates to datetimes and constant params relevant to 24-25 and 25-26 seasons
- Refactored logic to adjust for change in reporting cadence/format as of 2025-12-22 (@airhorns co-contributing)
- Additional unit testing for new report formats
- Basic actions workflows (ci, publish-pypi)

## Changed
- Miscellaneous edits to README, docstrings, error handling, and commenting to improve overall clarity

## [1.0.0] - 2025-08-04

### Added

- Pilot release to PyPI

### Changed

- Miscellaneous cosmetic changes to docstrings, README, __init__, etc

## [0.5.1] - 2025-07-24

### Added

- Started CHANGELOG

### Changed

- Decreased upper bound of jpype dependency (<1.6.0) to address discrepancy in JVM config/Java versioning
- Increased lower bound of python version (>= 3.10) for compatibility of "| hinting"

## [0.5.0] – 2025-07-17

### Added

- Baseline first release to Test PyPI