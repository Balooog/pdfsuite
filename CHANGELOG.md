# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v0.2.0] - 2025-11-11
### Added
- Hardened CLI expansion commands (`split`, `reorder`, `compare`, `audit`, `metadata_scrub`, `stamp`) with shared helpers for path validation and deterministic error handling.

### Changed
- Reworked `merge`, `split`, and `reorder` Typer wiring so usage/validation errors surface consistently and remain compatible with all supported qpdf releases.
- Updated `stamp` to support deterministic Bates numbering via per-page pdfcpu passes and qpdf page counts, while keeping the default text watermark path simple.
- Taught `metadata_scrub` to process copies via `mat2 --inplace`, preventing argument errors on current MAT2 builds.
- Ensured smoke tests cover the new commands end-to-end and continue to exercise the full CLI suite.

### Fixed
- `audit` now surfaces upstream tool failures unless explicitly permitted (pdfcpu validation), preventing silent misreports.
- Headless compare flow now bails out early when either input path is missing instead of failing deep inside Poppler/ImageMagick.

## [v0.1.0] - 2025-11-09
- Baseline release.
