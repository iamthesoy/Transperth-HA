# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-04-30

### Added
- Initial Home Assistant custom integration: `transperth_mobi`.
- Config flow setup for:
  - stop ID
  - display name
  - refresh interval
- Sensor entity with parsed departures in attributes:
  - `route`
  - `destination`
  - `minutes`
  - `scheduled_only`
  - `time`
- Bundled Lovelace custom card:
  - type: `custom:transperth-mobi-entity-card`
  - visual editor (title, sensor entity, max results)
- Static card asset serving and auto JS registration from integration.

### Changed
- Parser hardened for Transperth mobi HTML layout variations.
- Card UI improved:
  - top status line shows stop only
  - clearer live vs scheduled display labels
  - stable reload behavior (idempotent custom element registration).
