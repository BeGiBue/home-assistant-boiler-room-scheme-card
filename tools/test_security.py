#!/usr/bin/env python3
"""Browser-Regressionen für nicht vertrauenswürdige Texte und Entitäts-IDs.

Aufruf: python3 tools/test_security.py [--card pfad/zur/karte.js]
Benötigt Playwright und Chromium; optional PLAYWRIGHT_CHROMIUM_EXECUTABLE setzen.
"""
import argparse
import os
from pathlib import Path
import shutil
import sys

from harness import CARD


TEST_JS = r"""
() => {
  const results = [];
  const check = (name, pass, detail = '') => results.push({name, pass: !!pass, detail});
  const title = '<tspan data-injected="title">Titel & "Text"</tspan>';
  const subtitle = '<g data-injected="subtitle">Untertitel & \'Text\'</g>';
  const topics = ['', 'diagrams', 'gas', 'water', 'softener', 'settings', 'status', 'burner'];
  const create = (layout, config = {}, states = {}) => {
    document.body.style.width = layout === 'wide' ? '1100px' : '390px';
    const c = document.createElement('heizungsanlage-card');
    c.setConfig({layout, title, subtitle, ...config});
    document.body.appendChild(c);
    c.hass = {states, language: 'de'};
    return c;
  };
  const open = (c, topic) => {
    if (topic) {
      const button = [...c.shadowRoot.querySelectorAll('.btn[data-topic]')]
        .find((el) => el.dataset.topic === topic);
      if (!button) throw new Error('Thema fehlt: ' + topic);
      button.dispatchEvent(new Event('click'));
    }
  };
  const literalText = (c, text) => [...c.shadowRoot.querySelectorAll('text')]
    .some((el) => el.textContent === text && el.children.length === 0);
  const clean = (c) => !c.shadowRoot.querySelector('[data-injected], script, foreignObject') &&
    ![...c.shadowRoot.querySelectorAll('*')].some((el) =>
      [...el.attributes].some((a) => /^on/i.test(a.name)));
  const value = (root, id) => {
    const n = root.getElementById(id), u = root.getElementById(id + '-u');
    return n && n.textContent + (u && u.textContent ? ' ' + u.textContent : '');
  };

  // Jede konfigurierte ID bekommt Anführungszeichen, Markup und eine HTML-Entität.
  // So werden auch Hilfsfunktionen und nur im Detailbereich sichtbare Attribute geprüft.
  for (const layout of ['wide', 'compact']) {
    const probe = document.createElement('heizungsanlage-card');
    probe.setConfig({});
    const entities = Object.fromEntries(Object.keys(probe._config.entities).map((key) =>
      [key, `sensor.${key}" data-injected="entity" onpointerover="window.__injected=1" data-tail="&amp;<b>'`]));
    const allowed = new Set(Object.values(entities));
    const states = Object.fromEntries([...allowed].map((id) =>
      [id, {state: '50', attributes: {unit_of_measurement: '°C'}}]));
    const seen = new Set();
    for (const topic of layout === 'wide' ? [''] : topics) {
      const tag = `${layout}/${topic || 'Schema'}`;
      const c = create(layout, {entities}, states);
      open(c, topic);
      const root = c.shadowRoot;
      check(`${tag}: Titel und Untertitel bleiben reiner Text`,
        literalText(c, title) && literalText(c, subtitle));
      check(`${tag}: keine injizierten Elemente oder Attribute`, clean(c));
      const targets = [...root.querySelectorAll('[data-entity]')];
      check(`${tag}: sämtliche Entitäts-IDs bleiben unverändert`, targets.length &&
        targets.every((el) => allowed.has(el.getAttribute('data-entity'))));
      const clicks = [];
      c.addEventListener('hass-more-info', (event) => clicks.push(event.detail.entityId));
      let correct = true;
      for (const target of targets) {
        const id = target.getAttribute('data-entity');
        seen.add(id);
        const before = clicks.length;
        target.dispatchEvent(new Event('click'));
        if (clicks.length !== before + 1 || clicks[before] !== id) correct = false;
      }
      check(`${tag}: Klicks öffnen die ursprüngliche Entitäts-ID`, correct);
      c.remove();
    }
    check(`${layout}: Entity-Prüfung deckt Pumpen, Boxen und Einstellungen ab`,
      seen.size >= 20, String(seen.size));
  }

  // Historie direkt einspeisen: kein Recorder und keine Netzwerkanfragen nötig.
  // Payload 1 landet ohne Leerzeichen in u, Payload 2 verteilt Markup auf n und u.
  const units = [
    '°C</text><tspan>unit-probe</tspan><text>',
    '°C</text><tspan data-injected="unit">unit probe</tspan><text>',
    '&deg;C & " \' < >',
    '°C', '%', 'kWh',
  ];
  for (const layout of ['wide', 'compact']) {
    for (const unit of units) {
      const c = create(layout, {entities: {tank_temp: 'sensor.test_tank'}}, {
        'sensor.test_tank': {state: '44.1', attributes: {unit_of_measurement: unit}},
      });
      const now = Date.now();
      c._hists = {'sensor.test_tank': [{t: now - 60000, v: 40}, {t: now, v: 50}]};
      if (layout === 'compact') open(c, 'diagrams');
      else c._update();
      const root = c.shadowRoot;
      const tag = `${layout}: Einheit ${JSON.stringify(unit)}`;
      check(`${tag} bleibt im Maximum unveränderter Text`, value(root, 'ch-max') === '50,0 ' + unit);
      check(`${tag} bleibt im Minimum unveränderter Text`, value(root, 'ch-min') === '40,0 ' + unit);
      check(`${tag}: keine zusätzlichen Diagrammelemente`,
        !!root.getElementById('chart') && !root.getElementById('chart').querySelector('tspan') && clean(c));
      check(`${tag}: Istwert bleibt unveränderter Text`, value(root, 'v-tank') === '44,1 ' + unit);
      c.remove();
    }
  }
  return results;
}
"""


def main():
    from playwright.sync_api import sync_playwright

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--card", default=CARD)
    args = parser.parse_args()
    source = Path(args.card).read_text(encoding="utf8")
    with sync_playwright() as playwright:
        options = {}
        executable = os.environ.get("PLAYWRIGHT_CHROMIUM_EXECUTABLE")
        if not executable and not Path(playwright.chromium.executable_path).exists():
            executable = shutil.which("chromium") or shutil.which("chromium-browser")
        if executable:
            options["executable_path"] = executable
        browser = playwright.chromium.launch(**options)
        page = browser.new_page()
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.set_content("<html><body></body></html>")
        page.add_script_tag(content=source)
        results = page.evaluate(TEST_JS)
        results.append({"name": "Keine JavaScript-Fehler im Browser", "pass": not errors, "detail": str(errors)})
        browser.close()
    for result in results:
        print(("PASS " if result["pass"] else "FAIL ") + result["name"])
        if not result["pass"] and result.get("detail"):
            print("  " + result["detail"])
    failures = sum(not result["pass"] for result in results)
    print(f"\n{len(results)} Prüfungen, {failures} Fehler")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
