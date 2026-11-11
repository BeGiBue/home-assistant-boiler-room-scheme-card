#!/usr/bin/env python3
"""Browser-Regressionen für Bedienung und Aktualisierung: Tastatur, Fokus, kein Neuaufbau bei neuen Werten.

Aufruf: python3 tools/test_interaction.py [--card pfad/zur/karte.js]
Benötigt Playwright und Chromium; optional PLAYWRIGHT_CHROMIUM_EXECUTABLE setzen.
"""
import argparse
import os
from pathlib import Path
import shutil

from harness import CARD


TEST_JS = r"""
async () => {
  const results = [];
  const check = (name, pass) => results.push({name, pass: !!pass});
  const st = (state, unit) => ({state, attributes: unit ? {unit_of_measurement: unit} : {}});
  const states = () => ({
    'sensor.vicare_boiler_temperature': st('58', '°C'),
    'sensor.vicare_supply_temperature': st('52.3', '°C'),
    'sensor.vicare_outside_temperature': st('12.7', '°C'),
    'binary_sensor.vicare_burner_active': st('on'),
    'binary_sensor.vicare_circulation_pump_active': st('on'),
    'sensor.vscotho1_72_ww_speichertemperatur': st('44.1', '°C'),
  });
  const create = (layout, config = {}) => {
    document.body.replaceChildren();
    document.body.style.width = layout === 'wide' ? '1100px' : '390px';
    const c = document.createElement('heizungsanlage-card'), events = [];
    c.addEventListener('hass-more-info', (e) => events.push(e.detail.entityId));
    c.setConfig({layout, ...config});
    document.body.appendChild(c);
    c.hass = {states: states(), language: 'de'};
    return {c, events, set: (s) => { c.hass = {states: s, language: 'de'}; }};
  };
  const key = (el, k) => el.dispatchEvent(new KeyboardEvent('keydown', {key: k, bubbles: true, composed: true, cancelable: true}));
  const btn = (c, topic) => c.shadowRoot.querySelector(`.btn[data-topic="${topic}"]`);

  for (const layout of ['wide', 'compact']) {
    const {c, events, set} = create(layout);
    const root = c.shadowRoot;
    const svg = root.querySelector('svg'), val = root.getElementById('v-supply') || root.getElementById('v-boiler');
    const clk = [...root.querySelectorAll('[data-entity]')];
    const withId = clk.filter((el) => el.getAttribute('data-entity')), without = clk.filter((el) => !el.getAttribute('data-entity'));
    check(`${layout}: Werte mit Entität sind per Tastatur erreichbar`, withId.length > 0 && withId.every((el) => el.getAttribute('tabindex') === '0' && el.getAttribute('role') === 'button'));
    check(`${layout}: Felder ohne Entität sind nicht fokussierbar`, without.every((el) => !el.hasAttribute('tabindex')));
    const first = withId[0];
    first.focus();
    key(first, 'Enter');
    key(first, ' ');
    key(first, 'a');
    first.dispatchEvent(new Event('click'));
    check(`${layout}: Enter, Leertaste und Klick öffnen die Entität, andere Tasten nicht`,
      events.length === 3 && events.every((id) => id === first.getAttribute('data-entity')));
    // Jedes klickbare Element zeigt bei Tastaturfokus einen Rahmen (auch Werte ohne Kasten, Pumpen, Heizkörper, Diagramme)
    const noFrame = withId.filter((el) => { el.focus(); const cs = getComputedStyle(el); return el.matches(':focus-visible') && !(cs.outlineStyle === 'solid' && parseFloat(cs.outlineWidth) >= 3); });
    check(`${layout}: sichtbarer Fokusrahmen an allen ${withId.length} klickbaren Elementen`, noFrame.length === 0);
    first.focus();
    const space = new KeyboardEvent('keydown', {key: ' ', bubbles: true, composed: true, cancelable: true});
    first.dispatchEvent(space);
    check(`${layout}: Leertaste rollt die Seite nicht`, space.defaultPrevented);
    events.length = 0;

    // Neue Werte: Texte werden gesetzt, die Grafik bleibt bestehen
    const s = states();
    s['sensor.vicare_supply_temperature'] = st('61.5', '°C');
    s['binary_sensor.vicare_burner_active'] = st('off');
    set(s);
    check(`${layout}: neue Werte erscheinen ohne Neuaufbau der Grafik`,
      root.querySelector('svg') === svg && /61,5/.test(root.getElementById('v-supply')?.textContent || '') && !root.getElementById('boiler').classList.contains('on'));
    check(`${layout}: Tastaturfokus bleibt bei neuen Werten erhalten`, root.activeElement === first);
    check(`${layout}: Kästen nutzen die gemeinsame Füllung (halbtransparent aus der Textfarbe)`,
      [...root.querySelectorAll('rect.box, rect.cell')].length > 0 && [...root.querySelectorAll('rect.box, rect.cell')].every((r) => /rgba|color\(|oklab|srgb/.test(getComputedStyle(r).fill)));
    c.remove();
  }

  // Kompakt: Schaltflächen der Themen
  {
    const {c} = create('compact');
    const root = c.shadowRoot;
    const b = btn(c, 'diagrams');
    check('kompakt: Themen-Schaltflächen sind fokussierbar und melden ihren Zustand', b.getAttribute('tabindex') === '0' && b.getAttribute('aria-pressed') === 'false');
    b.focus();
    key(b, 'Enter');
    const b2 = btn(c, 'diagrams');
    const framed = (el) => { const cs = getComputedStyle(el); return !el.matches(':focus-visible') || (cs.outlineStyle === 'solid' && parseFloat(cs.outlineWidth) >= 3); };
    check('kompakt: Fokusrahmen an Diagrammen und Werten im geöffneten Thema', [...root.querySelectorAll('[data-entity]')].filter((el) => el.getAttribute('data-entity')).every((el) => { el.focus(); return framed(el); }) && (b2.focus(), framed(b2)));
    check('kompakt: Enter öffnet das Thema, Schaltfläche ist markiert', c._open === 'diagrams' && b2.getAttribute('aria-pressed') === 'true' && b2.querySelector('rect').classList.contains('on') && !!root.getElementById('chart'));
    check('kompakt: Fokus bleibt nach dem Öffnen auf der Schaltfläche', root.activeElement === b2);
    check('kompakt: Text der aktiven Schaltfläche bleibt in Textfarbe lesbar', getComputedStyle(b2.querySelector('text')).fill === getComputedStyle(btn(c, 'status').querySelector('text')).fill);
    key(b2, ' ');
    check('kompakt: Leertaste schließt das Thema wieder, Fokus bleibt', c._open === null && root.activeElement === btn(c, 'diagrams') && btn(c, 'diagrams').getAttribute('aria-pressed') === 'false');
    btn(c, 'gas').dispatchEvent(new Event('click'));
    check('kompakt: Klick öffnet weiterhin genau ein Thema', c._open === 'gas' && [...root.querySelectorAll('.btn .tab.on')].length === 1);
    const meter = root.querySelector(':not(.btn)[data-topic="water"]');
    meter.focus();
    key(meter, 'Enter');
    check('kompakt: Zähler im Schema per Tastatur, Fokus bleibt auf dem Zähler', c._open === 'water' && root.activeElement === root.querySelector(':not(.btn)[data-topic="water"]'));
    c.remove();
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
        page.set_content('<html><body style="--primary-text-color:#212121;--secondary-text-color:#727272;--primary-color:#03a9f4"></body></html>')
        page.add_script_tag(content=source)
        results = page.evaluate(TEST_JS)
        results.append({"name": "Keine JavaScript-Fehler im Browser", "pass": not errors})
        browser.close()
    for result in results:
        print(("PASS " if result["pass"] else "FAIL ") + result["name"])
    failures = sum(not result["pass"] for result in results)
    print(f"\n{len(results)} Prüfungen, {failures} Fehler")
    if errors:
        print(errors)
    return bool(failures)


if __name__ == "__main__":
    raise SystemExit(main())
