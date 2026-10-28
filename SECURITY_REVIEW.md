# Security-Review: Boiler Room Scheme Card

## Ergebnis

Zwei reproduzierbare Verfügbarkeitsfehler in der Diagrammberechnung wurden behoben.
Die HTML-/SVG-Injection-Korrekturen aus früheren Versionen sind weiterhin wirksam.
Keine weitere bestätigte XSS-, Authentifizierungs-, Credential- oder URL-Lücke gefunden.
Keine bestätigten offenen hohen oder kritischen Sicherheitsbefunde im geprüften Umfang.

## Befunde und Korrekturen

| ID | Datei / Funktion | Risiko | Schweregrad | Korrektur / Status |
|---|---|---|---|---|
| BR-01 | `dist/heizungsanlage-card.js`: `_ticks()`, aufgerufen von `_drawChart()` und `_drawBurnerChart()` | `_ticks()` benutzte höchstens Schrittweite 50 ohne Iterationsgrenze. Recorder-Werte wie `[1e20,1e21]` erzeugen eine nicht fortschreitende Gleitkomma-Addition und Endlosschleife; `[0,1e9]` verursacht Millionen Iterationen. Beide Diagramm-Renderer ließen sich damit blockieren. Ein fehlerhafter oder manipulierter zugeordneter HA-Sensor genügt. | **Mittel** (Verfügbarkeit des Browser-Frontends) | Adaptive Schrittweite, maximal 64 Schleifendurchläufe, Endlichkeits-/Fortschrittsprüfung und Abweisung unbrauchbarer Skalen. Live-/Recorder-Werte und Umrechnungsergebnisse werden auf Endlichkeit geprüft. **Behoben.** |
| BR-02 | `dist/heizungsanlage-card.js`: Min-/Max-Berechnung in `_drawChart()` und `_drawBurnerChart()` | `Math.min(...vals)` und `Math.max(...vals)` überschritten bei großen Verläufen das JavaScript-Argumentlimit. Mit 200.000 Punkten reproduzierbarer RangeError; solche Mengen sind bei häufig meldenden Sensoren über 24 Stunden möglich. | **Niedrig** (Diagrammausfall) | Min-/Max-Berechnung mit `reduce` statt Argument-Spread. Beide Renderer mit 200.000 Punkten getestet. **Behoben.** |
| BR-DEV-01 | `tools/images.py`, `tools/harness.py` (Entwicklungswerkzeuge) | Ein älterer Pillow-Stand hatte bekannte Advisories, unter anderem zu Bild-Decodern und Speicherfehlern. Das ist keine ausgelieferte Kartenabhängigkeit und kein nachgewiesener Exploit der Karte; relevant bei lokaler Verarbeitung nicht vertrauenswürdiger Bilder. | **Mittel im Werkzeugkontext** | `requirements-dev.txt` legt geprüfte Versionen von Pillow und Playwright fest; Anleitung und Test-CI verwenden diese Datei. Ein Test-Venv samt transitiven Paketen wurde auditiert: 0 bekannte Befunde. **Behoben.** |

BR-01 wurde am tatsächlichen `_drawChart()` und `_drawBurnerChart()` reproduziert.
Die numerischen Tests führen die echte Kartenklasse in einer Node-VM mit Zeitlimit aus: Der alte
Code scheitert bei 8 von 9 Prüfungen (Timeouts, Argumentüberlauf), der korrigierte Code besteht alle.
Normale Temperaturskalen bleiben gleich.

## Geprüfte Vertrauensgrenzen

- **HTML/SVG und Attribute:** gemeinsame `esc()`-Funktion für Konfigurationstitel, Untertitel,
  Entity-IDs und dynamische Diagrammtexte. Livewerte und Einheiten werden mit `textContent`
  gesetzt. Die Browser-Regressionen prüfen breite/kompakte Layouts, alle
  Detailbereiche, manipulierte Einheiten und Entity-Klicks; keine injizierten Elemente
  oder Inline-Event-Handler.
- **URLs und Bilder:** SVG-`image href` stammt ausschließlich aus festen eingebetteten
  WebP-Assets in `IMG`. Keine konfigurierbaren externen Bilder, dynamischen Navigations-URLs
  oder Event-Handler.
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

## Tests

- `npm run check`: Syntaxprüfung der Kartendatei.
- `npm test`: numerische Security-Regressionen (`tools/test_numeric_security.mjs`),
  Editor- und Layoutprüfungen (`tools/test_editor.py`) und HTML-Injection-Prüfungen
  (`tools/test_security.py`).
- Dieselben Prüfungen laufen in der CI (`.github/workflows/validate.yml`).
- Die Vorschau (`npm run preview`) verwendet Testdaten, keine echte Anlage.

## HACS

Der Eintrag `BeGiBue/home-assistant-boiler-room-scheme-card` wurde im offiziellen
HACS-Katalog `hacs/default` (Datei `plugin`) bestätigt. Kartentyp `custom:heizungsanlage-card`,
Standard-Entitäten und Konfigurationsschlüssel bleiben erhalten. Numerisch unbrauchbare
Daten werden verworfen, große Verläufe und extreme Skalen sicher verarbeitet.

## Restrisiken

- Fehlende, veraltete oder fachlich falsche, aber endliche Sensorwerte können weiterhin
  irreführende Anzeigen ergeben. Animationen ersetzen keine Anlagenüberwachung.
- Sehr große Recorder-Antworten verursachen weiterhin linearen Speicher-/Rechenaufwand;
  der Argumentüberlauf und die unbeschränkte Tick-Schleife sind behoben. Die Karte
  beschränkt nicht die vom HA-Backend gelieferte Gesamtgröße.
- Reale HA-/HACS-/Companion-/Kiosk-Kompatibilität und echte Gerätezuordnungen wurden nicht
  an einer echten Anlage geprüft.
- Der Release-Workflow (`.github/workflows/release.yml`) läuft bei jedem Push auf `main` und
  wartet nicht auf den Validate-Workflow (`.github/workflows/validate.yml`).
