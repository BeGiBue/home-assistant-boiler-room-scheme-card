# Security-Review und HACS-Major-Vorbereitung: Boiler Room Scheme Card

Stand: 25.10.2026. Repository: `BeGiBue/home-assistant-boiler-room-scheme-card`.
Geprüfte Ausgangsbasis: `3be0a00a63260168d641e138e1772b16855533b8` (**1.0.8**).
Zielversion: **2.0.0**. Zeilenangaben unten beziehen sich auf diese Ausgangsbasis, sofern nicht anders angegeben.

## Ergebnis

Zwei reproduzierbare Verfügbarkeitsfehler in der Diagrammberechnung wurden behoben.
Die bereits in 1.0.8 enthaltenen HTML-/SVG-Injection-Korrekturen sind weiterhin wirksam.
Keine weitere bestätigte XSS-, Authentifizierungs-, Credential- oder URL-Lücke gefunden.
Keine bestätigten offenen hohen oder kritischen Sicherheitsbefunde im geprüften Umfang.

## Befunde und Korrekturen

| ID | Repository | Datei / Zeile | Risiko | Schweregrad | Korrektur / Status |
|---|---|---|---|---|---|
| BR-01 | home-assistant-boiler-room-scheme-card | `dist/heizungsanlage-card.js:1117–1121`; Aufrufer `:1156`, `:1212` | `_ticks()` benutzt höchstens Schrittweite 50 ohne Iterationsgrenze. Recorder-Werte wie `[1e20,1e21]` erzeugen eine nicht fortschreitende Gleitkomma-Addition und Endlosschleife; `[0,1e9]` verursacht Millionen Iterationen. Beide tatsächlichen Renderer lassen sich damit blockieren. Ein fehlerhafter oder manipulierter zugeordneter HA-Sensor genügt. | **Mittel** (Verfügbarkeit des Browser-Frontends) | Adaptive Schrittweite, maximal 64 Schleifendurchläufe, Endlichkeits-/Fortschrittsprüfung und Abweisung unbrauchbarer Skalen. Live-/Recorder-Werte und Umrechnungsergebnisse werden auf Endlichkeit geprüft. **Behoben.** |
| BR-02 | home-assistant-boiler-room-scheme-card | `dist/heizungsanlage-card.js:1150–1151`, `:1201–1202` | `Math.min(...vals)` und `Math.max(...vals)` überschreiten bei großen Verläufen das JavaScript-Argumentlimit. Mit 200.000 Punkten reproduzierbarer RangeError; solche Mengen sind bei häufig meldenden Sensoren über 24 Stunden möglich. | **Niedrig** (Diagrammausfall) | Min-/Max-Berechnung mit `reduce` statt Argument-Spread. Beide Renderer mit 200.000 Punkten getestet. **Behoben.** |
| BR-DEV-01 | home-assistant-boiler-room-scheme-card | `tools/images.py:35–44`, `tools/harness.py:118–120`; bisher unversionierte Pillow-Installationshinweise in README/CLAUDE | Der lokal verwendete Entwicklungsstand Pillow 12.3.0 hat 37 bekannte Advisories, unter anderem zu Bild-Decodern und Speicherfehlern. Das ist keine ausgelieferte Kartenabhängigkeit und kein nachgewiesener Exploit der Karte; relevant bei lokaler Verarbeitung nicht vertrauenswürdiger Bilder. | **Mittel im Werkzeugkontext**; Schwere einzelner Advisories variiert | `requirements-dev.txt` legt Pillow 13.0.0 und Playwright 1.64.1 fest; Anleitung und Test-CI verwenden diese Datei. Eigenes Test-Venv samt transitiven Paketen erneut auditiert: **0 bekannte Befunde**. **Behoben.** |

BR-01 wurde unabhängig am tatsächlichen `_drawChart()` und `_drawBurnerChart()` reproduziert.
Die neuen Tests führen die echte Kartenklasse in einer Node-VM mit Zeitlimit aus: Der alte
Code scheitert bei 8 von 9 Prüfungen, unter anderem mit Timeouts und Argumentüberlauf;
der korrigierte Code besteht alle 9. Normale Temperaturskalen bleiben gleich.

## Weitere geprüfte Vertrauensgrenzen

- **HTML/SVG und Attribute:** gemeinsame `esc()`-Funktion für Konfigurationstitel, Untertitel,
  Entity-IDs und dynamische Diagrammtexte. Livewerte und Einheiten werden mit `textContent`
  gesetzt. Die vorhandenen Browser-Regressionen prüfen breite/kompakte Layouts, alle
  Detailbereiche, manipulierte Einheiten und Entity-Klicks; keine injizierten Elemente
  oder Inline-Event-Handler. Die Escaping-Fixes stammen bereits aus 1.0.8.
- **URLs und Bilder:** SVG-`image href` stammt ausschließlich aus festen eingebetteten
  WebP-Assets in `IMG`. Keine konfigurierbaren externen Bilder, dynamischen Navigations-URLs
  oder Event-Handler. Eingebettete Bilddaten wurden unverändert erhalten.
- **Authentifizierung und API:** `hass.callWS` für Energie-Dashboard, Recorder-Statistiken,
  Metadaten und Verlauf läuft über die angemeldete HA-Sitzung. Keine eigene Geräte-API,
  kein `fetch`, eigener WebSocket-Client, `localStorage`, Token oder Gerätepasswort.
  Die Karte ruft keine Schalt-/Heizungsdienste auf; Klicks öffnen `hass-more-info`.
  Backend-Autorisierung bleibt Aufgabe von Home Assistant.
- **Sensible Daten:** Verlauf und Verbrauchsdaten bleiben in der HA-Sitzung; kein eigener
  externer Empfänger. Kein hartcodiertes Geheimnis im geprüften Laufzeitcode gefunden.
  Keine vollständige Geheimnissuche über die Git-Historie.
- **Python und Dateien:** keine Python-Integration und somit kein eigener HA-Python-Event-Loop-Pfad.
  Die Python-Dateien sind lokal bediente Entwicklungswerkzeuge. Feste Karten-/Paketpfade,
  explizite CLI-Eingabe-/Ausgabepfade und Bildschlüssel ohne Pfadbestandteile; kein
  fernbedienbarer Dateiserver oder privilegierter Dateizugriff.
- **Laufzeitabhängigkeiten:** die einzelne JS-Datei enthält keine externen Bibliotheken
  und benötigt keinen npm-Build. Python-Werkzeuge und Playwright werden nicht an
  HACS-Nutzer ausgeliefert. Advisory-Prüfungen sind zeitbezogen, kein Nachweis absoluter
  Schwachstellenfreiheit von Browser, HA-Core oder Geräteintegrationen.

## Tests und Nachprüfung

Lokal mit Node 24, CPython 3.14.8, Playwright 1.64.1, Pillow 13.0.0 und Chromium:

- `npm run check`: bestanden.
- `npm test`: **153 erfolgreiche Einzelprüfungen**: 9 neue numerische Security-Regressionen,
  57 vorhandene Editor-/Layoutprüfungen und 87 vorhandene HTML-Injection-Prüfungen.
- Baseline-Reproduktion mit derselben neuen numerischen Suite: 9 Prüfungen, **8 erwartete Fehler**.
- `npm run preview`: erfolgreich; breite, kompakte und kompakte Ansicht mit Diagrammen erzeugt
  und visuell geprüft. Die Vorschau verwendet Testdaten, keine echte Anlage.
- Unveränderte `DEFAULTS` und identischer `IMG`-Block gegen die Ausgangsbasis geprüft.
- `pip-audit --path <isoliertes Test-Venv>/lib/python3.14/site-packages`: **0 bekannte Befunde**
  für Playwright 1.64.1, Pillow 13.0.0, greenlet 3.5.6, pyee 14.0.0 und typing-extensions 4.16.0.
  Der vorherige lokale Pillow-12.3.0-Stand meldete 37 Advisories, jeweils mit Fix 13.0.0.
- Versionsgleichheit von `CARD_VERSION`, `package.json`, README sowie Changelog-/Release-Notes-Text geprüft.
- `git diff --check`: bestanden.
- Die neue numerische Suite läuft zusätzlich in der vorhandenen Syntax-CI; Browser-CI behält
  Editor-/Layout-/HTML-Prüfungen und installiert die festgelegten Entwicklungsabhängigkeiten.
  GitHub-CI ist vor Freigabe am PR zu prüfen.

## HACS, Migration und Version

Der Eintrag `BeGiBue/home-assistant-boiler-room-scheme-card` wurde im offiziellen
HACS-Katalog `hacs/default` (Datei `plugin`) bestätigt. README und Changelog beschreiben
die HACS-Suche als Standardweg und den Wechsel bestehender Custom Repositories:
Katalogverfügbarkeit prüfen, nur den benutzerdefinierten Eintrag entfernen, **nicht
deinstallieren**, HACS aktualisieren und vorhandene Karten/Ressourcen prüfen.

Die Major-Version 2.0.0 markiert den Katalog-Meilenstein und bedeutet **nicht automatisch
Breaking Changes**. Kartentyp `custom:heizungsanlage-card`, Standard-Entitäten,
Konfigurationsschlüssel und reguläre Layouts bleiben erhalten. Numerisch unbrauchbare
Daten werden jetzt verworfen, große Verläufe und extreme Skalen sicher verarbeitet.

## Restrisiken, Blocker und Freigaben

- Fehlende, veraltete oder fachlich falsche, aber endliche Sensorwerte können weiterhin
  irreführende Anzeigen ergeben. Animationen ersetzen keine Anlagenüberwachung.
- Sehr große Recorder-Antworten verursachen weiterhin linearen Speicher-/Rechenaufwand;
  der Argumentüberlauf und die unbeschränkte Tick-Schleife sind behoben. Die Karte
  beschränkt nicht die vom HA-Backend gelieferte Gesamtgröße.
- Reale HA-/HACS-/Companion-/Kiosk-Kompatibilität und echte Gerätezuordnungen vor
  Veröffentlichung prüfen. Es wurden keine Heizungseinstellungen oder Geräteaktionen ausgeführt.
- Keine aktiven Repository-Rulesets gefunden; Branch-Metadaten melden `protected:false`.
  Der gesonderte administrative Branch-Protection-Endpunkt war mit HTTP403 nicht lesbar.
  Schutzregeln wurden nicht verändert oder umgangen.
- **Merge-Sperre bis zur Veröffentlichungsfreigabe:** Der bestehende
  `.github/workflows/release.yml` veröffentlicht bei jedem Push auf `main` automatisch
  die Paketversion bzw. aktualisiert vorhandene Release Notes. Er wartet nicht auf
  den Validate-Workflow. Daher erst nach erfolgreichen Prüfungen und ausdrücklicher
  Release-Freigabe oder separat kontrolliertem Automatismus mergen.

Dieser Auftrag erstellt einen Entwurfs-PR. Kein Merge, Tag, Release oder
Veröffentlichungsworkflow wird ausgeführt. Die zuvor ausgenommene Boiler Room Card
ist durch den Folgeauftrag ausdrücklich im Umfang; `home-assistant-irrigation-card`
und die neun zuvor geprüften Repositories werden hier nicht verändert.

