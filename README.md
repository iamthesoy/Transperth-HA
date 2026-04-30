# Transperth Mobi for Home Assistant

Home Assistant custom integration for Transperth stop departures, with a bundled Lovelace custom card editor (UI setup, no manual YAML required).

## Features

- Config flow setup (choose stop ID once)
- Polls Transperth mobi stop endpoint:
  - `https://136213.mobi/RealTime/RealTimeStopResults.aspx?SN=<STOP_ID>`
- Sensor attributes include normalized departures:
  - `route`
  - `destination`
  - `minutes` (live ETA when available)
  - `scheduled_only` (true when only scheduled value is available)
  - `time`
- Bundled custom card:
  - `custom:transperth-mobi-entity-card`
  - Visual editor for entity, title, max results

## HACS Installation

1. Push this repository to GitHub.
2. In Home Assistant, go to HACS -> Integrations -> 3-dot menu -> Custom repositories.
3. Add your repository URL, category: `Integration`.
4. Install **Transperth Mobi** from HACS.
5. Restart Home Assistant.
6. Add integration:
   - Settings -> Devices & Services -> Add Integration -> `Transperth Mobi`
   - Enter stop ID (e.g. `12345`)
7. Add card:
   - Edit dashboard -> Add Card -> search `Transperth Mobi Entity Card`
   - Select your sensor entity (e.g. `sensor.bus`)

## Notes

- The integration auto-registers the bundled JS card URL:
  - `/transperth_mobi/transperth-mobi-entity-card.js`
- If card updates do not appear immediately, do a browser hard refresh.

## Example Card YAML (optional)

```yaml
type: custom:transperth-mobi-entity-card
title: Transperth Departures
entity: sensor.bus
max_results: 5
```
