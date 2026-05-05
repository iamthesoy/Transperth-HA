# Changelog

## [v1.1.0] - 05/05/2026

Adds local brand icon support, device grouping, and fifteen “next route” helper sensors (route number, ETA, destination for departures 1–5).

### Highlights

- `brand/icon.png` for Home Assistant integration branding
- One device per stop with linked entities
- Sensors: **Next route 1–5 number / ETA / destination**

## [1.0.0] - 30/04/2026

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
