# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.2] - 2026-04-06

### Added
- **Staggered Offsets Support**: Added `offset` parameter to `SecopClient.search()` to support high-throughput parallel ingestion and dataset slicing.
- **Rate Limit Resilience**: Implemented exponential backoff for 429 status codes in `SecopClient.fetch()` to ensure stability during massive scraping loops.

### Changed
- **Strict Unified Schema**: `normalize_dataframe` now enforces a deterministic unified schema, ensuring all mapped columns are present (filled with `None` if missing) for Postgres compatibility.
- **Enhanced Normalization**: Improved deterministic behavior of `DataProcessor.process_dataset`.

### Fixed
- Resolved potential schema mismatch errors when consolidating parallel ingestion blocks.

## [1.2.1] - 2026-04-06
- Internal stability and maintenance release.

## [1.2.0] - 2026-04-06

### Added
- **Intelligent Normalization Layer**: Introduced `SmartNormalizer` to automatically handle malformed or inconsistently typed user inputs (e.g., NITs with dashes/dots, mixed-format dates).
- **Universal Matrix Consolidation**: Implemented 'Matrix-in-Blocks' strategy to provide a unified, non-destructive view across SECOP I and II.
- **Deep Homologation**: Expansively mapped dozens of fields between SECOP I and SECOP II, standardizing on the SECOP II schema while preserving 100% of unique source data.
- **Improved Type Safety**: Automatic numeric cleaning and SoQL-compatible casting for SODA queries.
- **Windows compatibility**: Added `make.bat` with simplified routing for easier developer onboarding on Windows.
- **Docker Support**: Provided a standardized `Dockerfile` and developer environment for isolated testing.
- **Build Tooling**: Added `dist` and `build` commands to `make.bat` for easy packaging.

### Changed
- Refactored `SecopClient.search()` to use a global "Deep Union" consolidation logic.
- Standardized the Unified Schema to prioritize SECOP II field names (`nombre_entidad`, `valor_del_contrato`, etc.).
- Enhanced `SecopClient.get_contracts_by_ids()` for full backward compatibility with the new unified architecture.
- Updated `QueryBuilder` to default to `select *` when no specific columns are requested, supporting complete data preservation.

### Fixed
- Resolved `400 Client Error: Bad Request` SoQL type-mismatch issues in SECOP II.
- Fixed `The system cannot find the batch label specified` error in Windows batch scripts.
- Corrected column duplication issues when merging homologated fields.

## [1.1.1] 
- Internal maintenance and dependency updates.
