class TransperthMobiEntityCard extends HTMLElement {
  static getConfigElement() {
    return document.createElement("transperth-mobi-entity-card-editor");
  }

  static getStubConfig(hass) {
    const entities = Object.keys(hass.states || {});
    const defaultEntity =
      entities.find((e) => e.startsWith("sensor.transperth")) ||
      entities.find((e) => e === "sensor.bus") ||
      entities.find((e) => e.startsWith("sensor.")) ||
      "sensor.bus";

    return {
      type: "custom:transperth-mobi-entity-card",
      title: "Transperth Departures",
      entity: defaultEntity,
      max_results: 5,
    };
  }

  set hass(hass) {
    this._hass = hass;
    this._render();
  }

  setConfig(config) {
    if (!config.entity) {
      throw new Error("entity is required");
    }
    this._config = {
      title: "Transperth Departures",
      max_results: 5,
      ...config,
    };
    this._render();
  }

  getCardSize() {
    return 4;
  }

  _render() {
    if (!this._hass || !this._config) return;

    if (!this._card) {
      this._card = document.createElement("ha-card");
      this._card.innerHTML = `
        <style>
          .wrap { padding: 16px; }
          .row {
            display: grid;
            grid-template-columns: auto 1fr auto;
            gap: 10px;
            align-items: baseline;
            padding: 6px 0;
            border-bottom: 1px solid var(--divider-color);
          }
          .row:last-child { border-bottom: none; }
          .route { font-weight: 600; min-width: 36px; }
          .dest { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
          .eta { font-weight: 600; }
          .muted { color: var(--secondary-text-color); }
          .sched { font-weight: 400; color: var(--secondary-text-color); margin-left: 6px; }
        </style>
        <div class="wrap">
          <div id="status" class="muted"></div>
          <div id="list"></div>
        </div>
      `;
      this.appendChild(this._card);
    }

    this._card.header = this._config.title;
    const stateObj = this._hass.states[this._config.entity];
    const statusEl = this._card.querySelector("#status");
    const listEl = this._card.querySelector("#list");

    if (!stateObj) {
      statusEl.textContent = `Entity not found: ${this._config.entity}`;
      listEl.innerHTML = "";
      return;
    }

    const departures = (stateObj.attributes.departures || []).slice(0, this._config.max_results);
    const stopId = stateObj.attributes.stop_id || "";

    statusEl.textContent = `Stop ${stopId}`;
    if (!departures.length) {
      listEl.innerHTML = "";
      return;
    }

    listEl.innerHTML = departures
      .map((d) => {
        const etaLabel = d.minutes != null ? `${d.minutes} min` : "No live ETA";
        const schedLabel = d.scheduled_only
          ? `<span class="sched">scheduled ${d.time || ""}</span>`
          : d.time
            ? `<span class="sched">${d.time}</span>`
            : "";
        return `
          <div class="row">
            <div class="route">${this._escape(d.route)}</div>
            <div class="dest">${this._escape(d.destination)}</div>
            <div class="eta">${etaLabel}${schedLabel}</div>
          </div>
        `;
      })
      .join("");
  }

  _escape(v) {
    return String(v)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#39;");
  }
}

class TransperthMobiEntityCardEditor extends HTMLElement {
  setConfig(config) {
    this._config = {
      title: "Transperth Departures",
      max_results: 5,
      ...config,
    };
    this._render();
  }

  set hass(hass) {
    this._hass = hass;
    this._render();
  }

  _render() {
    if (!this._hass || !this._config) return;

    const entities = Object.keys(this._hass.states || {})
      .filter((entityId) => entityId.startsWith("sensor."))
      .sort();

    const options = entities
      .map(
        (entityId) =>
          `<option value="${this._escape(entityId)}" ${entityId === this._config.entity ? "selected" : ""}>${this._escape(entityId)}</option>`,
      )
      .join("");

    this.innerHTML = `
      <style>
        .wrap { display: grid; gap: 12px; padding: 8px 0; }
        .field { display: grid; gap: 6px; }
        label { font-size: 12px; color: var(--secondary-text-color); }
        input, select {
          font: inherit;
          padding: 8px;
          border-radius: 8px;
          border: 1px solid var(--divider-color);
          background: var(--card-background-color);
          color: var(--primary-text-color);
        }
      </style>
      <div class="wrap">
        <div class="field">
          <label>Title</label>
          <input id="title" type="text" value="${this._escape(this._config.title || "")}" />
        </div>
        <div class="field">
          <label>Sensor Entity</label>
          <select id="entity">
            ${options}
          </select>
        </div>
        <div class="field">
          <label>Max Results</label>
          <input id="max_results" type="number" min="1" max="20" value="${Number(this._config.max_results || 5)}" />
        </div>
      </div>
    `;

    this.querySelector("#title")?.addEventListener("change", (ev) => {
      this._updateConfig({ title: ev.target.value });
    });

    this.querySelector("#entity")?.addEventListener("change", (ev) => {
      this._updateConfig({ entity: ev.target.value });
    });

    this.querySelector("#max_results")?.addEventListener("change", (ev) => {
      const value = Number(ev.target.value);
      this._updateConfig({ max_results: Number.isFinite(value) ? Math.max(1, value) : 5 });
    });
  }

  _updateConfig(patch) {
    const next = { ...this._config, ...patch };
    this.dispatchEvent(
      new CustomEvent("config-changed", {
        detail: { config: next },
        bubbles: true,
        composed: true,
      }),
    );
  }

  _escape(v) {
    return String(v)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#39;");
  }
}

if (!customElements.get("transperth-mobi-entity-card")) {
  customElements.define("transperth-mobi-entity-card", TransperthMobiEntityCard);
}

if (!customElements.get("transperth-mobi-entity-card-editor")) {
  customElements.define("transperth-mobi-entity-card-editor", TransperthMobiEntityCardEditor);
}

window.customCards = window.customCards || [];
if (!window.customCards.some((c) => c.type === "transperth-mobi-entity-card")) {
  window.customCards.push({
    type: "transperth-mobi-entity-card",
    name: "Transperth Mobi Entity Card",
    description: "Shows departures from transperth_mobi sensor attributes",
    preview: true,
  });
}
