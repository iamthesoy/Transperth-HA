## Transperth Mobi v1.0.0

Initial public release of the Transperth Mobi Home Assistant integration and bundled custom Lovelace card.

### Highlights

- Config-flow based setup (no YAML required for integration setup)
- Live/scheduled departure parsing from Transperth mobi stop endpoint
- Sensor attributes with normalized departure rows
- Bundled custom card with visual editor for first setup
- Improved card reload stability and UI behavior

### Included

- Integration domain: `transperth_mobi`
- Card type: `custom:transperth-mobi-entity-card`

### Installation

Install via HACS custom repository (category: **Integration**), restart Home Assistant, then:

1. Add integration: **Transperth Mobi**
2. Enter your stop ID (e.g. `12345`)
3. Add card from dashboard UI and select your sensor

### Notes

- If a browser has stale assets after update, hard refresh once.

---
