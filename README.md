<p align="center">
  <img src="https://raw.githubusercontent.com/BeGiBue/home-assistant-boiler-room-scheme-card/main/docs/assets/logo-160.png?v=2" alt="Boiler Room Scheme Card" width="160">
</p>

# Boiler Room Scheme Card

**Version 2.0.1**

Eine Home-Assistant-Karte (`custom:heizungsanlage-card`), die eine Gas-/Ölheizung als
animiertes Anlagenschema darstellt: Kessel, Warmwasserspeicher, Pumpen, Heizkörper,
Gas- und Wasserzähler, Enthärtungsanlage – mit Live-Werten und Verläufen.

## Vorschau

**Heizbetrieb – schmal (350 px), Details geschlossen**

<img src="https://raw.githubusercontent.com/BeGiBue/home-assistant-boiler-room-scheme-card/main/screenshots/boiler-heating-350-closed-light.png" width="350" alt="Heizbetrieb im hellen Theme, 350 px Kartenbreite, Details geschlossen">

**Heizbetrieb – schmal (350 px), Diagramme geöffnet**

<img src="https://raw.githubusercontent.com/BeGiBue/home-assistant-boiler-room-scheme-card/main/screenshots/boiler-heating-350-diagrams-light.png" width="350" alt="Heizbetrieb im hellen Theme, 350 px Kartenbreite, Diagramme geöffnet">

**Heizbetrieb – breit (800 px)**

<img src="https://raw.githubusercontent.com/BeGiBue/home-assistant-boiler-room-scheme-card/main/screenshots/boiler-heating-800-light.png" width="800" alt="Vollständiges Heizungsschema im Heizbetrieb, 800 px Kartenbreite, helles Theme">

> Die Standardwerte der Karte passen zu einer Viessmann-Anlage
> mit der ViCare-Integration (Vitocrossal 300 & Vitocell 100-V), lassen sich aber komplett im
> visuellen Editor anpassen.

## Funktionen

- **Animierte Leitungen:** Heizkreis, Ladekreis, Zirkulation und Kaltwasser laufen nur, wenn die jeweilige Pumpe bzw. der Durchfluss aktiv ist.
- **Pumpen mit drehendem Flügelrad**, solange sie laufen.
- **Brenner:** Flamme im Sichtfenster, Größe folgt der Modulation. Darunter ein 24-h-Graph mit Modulation und Kesseltemperatur (Y-Achse in °C für die Kesseltemperatur).
- **Warmwasserspeicher:** Füllanzeige, 24-h-Verlauf mit Soll-Linie, zwei grauen Grenzlinien sowie Maximum, Istwert und Minimum. Die Skala reicht von 5 K unter dem Mindest-Sollwert bis 5 K über dem Maximal-Sollwert (`limit_offset`); die grauen Grenzlinien bilden Unter- und Obergrenze.
- **Einheiten umgerechnet:** Der Wasserzähler zeigt den Stand in m³ mit zwei Nachkommastellen und den Durchfluss in l/h. Unterstützte Volumeneinheiten und Durchflussraten (z. B. L, m³, m³/h, l/min und l/h) werden umgerechnet; unbekannte Einheiten werden unverändert angezeigt.
- **Gas und Wasser aus dem Energie-Dashboard** (Stand und Tagesverbrauch), ohne zusätzliche Konfiguration.
- **Enthärtungsanlage:** letzte Regeneration (Datum), Salzstand in % und geschätzter Restbestand in Regenerationen über passende Sensoren, z. B. aus [Water Softener Refill Sensor](https://github.com/BeGiBue/home-assistant-water-softener-refill-sensor).
- **Kompakte Ansicht** für Handy und kleine Hochformat-Displays mit aufklappbaren Details.
- **Untere Leiste:** Status (Außentemperatur, Frostschutz, Brennerstunden, Brennerstarts) und Einstellungen (Heizkurve, Temperaturen).
- Ein Klick auf jeden Wert öffnet den normalen Home-Assistant-Entitätsdialog.

## Installation

### Über den offiziellen HACS-Katalog (empfohlen)

1. HACS öffnen und nach **Boiler Room Scheme Card** suchen.
2. Die Karte auswählen und herunterladen.
3. Browser vollständig neu laden; in der Companion-App gegebenenfalls den Frontend-Cache zurücksetzen.

[![In HACS öffnen](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=BeGiBue&repository=home-assistant-boiler-room-scheme-card&category=plugin)

HACS legt die Dashboard-Ressource normalerweise automatisch an. Falls sie fehlt, unter
**Einstellungen → Dashboards → Ressourcen** die URL
`/hacsfiles/home-assistant-boiler-room-scheme-card/heizungsanlage-card.js` als **JavaScript-Modul** hinzufügen.
Eine bereits vorhandene Ressource nicht doppelt eintragen.

### Bestehende Custom-Repository-Installation migrieren

1. Prüfen, dass **Boiler Room Scheme Card** im offiziellen HACS-Katalog verfügbar ist.
2. Danach unter **HACS → ⋮ → Benutzerdefinierte Repositories** nur den Eintrag für
   `BeGiBue/home-assistant-boiler-room-scheme-card` entfernen.
3. **Die bestehende Installation nicht deinstallieren.** Dashboard-Ressource, Karten und YAML-Konfigurationen beibehalten.
4. HACS neu laden bzw. **Informationen aktualisieren**, angebotene Updates installieren, das Frontend vollständig neu laden und bestehende Karten prüfen.

Die Aufnahme in den offiziellen HACS-Katalog erfordert kein erneutes Anlegen der Karten.
`type: custom:heizungsanlage-card`, Entitätszuordnungen und vorhandene Konfigurationsschlüssel bleiben erhalten.
Die Major-Version 2.0.0 markiert diesen Meilenstein und bedeutet **nicht automatisch Breaking Changes**.

### Manuell

1. `dist/heizungsanlage-card.js` nach `/config/www/` kopieren.
2. *Einstellungen → Dashboards → ⋮ → Ressourcen* → Ressource hinzufügen:
   URL `/local/heizungsanlage-card.js`, Typ **JavaScript-Modul**.
3. Browser-Cache leeren.

## Einrichtung ohne YAML

Karte hinzufügen → **Heizungsanlage** wählen. Alle Einstellungen stehen im visuellen Editor
bereit, aufgeteilt in aufklappbare Bereiche (Allgemein, Status, Kessel & Brenner, Pumpen,
Warmwasserspeicher, Einstellungen, Gas & Wasser, Enthärtungsanlage). Die Felder nutzen die
Standard-Auswahlelemente von Home Assistant (Entitätsauswahl, Zahlenfelder).

Wird ein Feld geleert, wird die Entität bewusst abgewählt: Das zugehörige Element zeigt dann „–"
und löst keine Animation aus.

### Breite im Sections-Dashboard

Die Karte füllt die volle Breite ihres Abschnitts. Für die Breite von zwei Sektionen dem
Abschnitt die Breite **2 Spalten** geben (YAML: `column_span: 2`). Die Höhe passt sich
automatisch an.

### Layout: breit und kompakt

Die Karte wählt ihr Layout nach der verfügbaren Breite (Einstellung **Layout** im Editor):

- **Breit** (ab ca. 700 px, z. B. Tablet oder Desktop): vollständiges Schema mit allen Geräten,
  Diagrammen, Datenboxen und der unteren Leiste.
- **Kompakt** (unter ca. 700 px, z. B. Handy oder 7"-Display im Hochformat): Kerngeräte mit großen Zahlen
  (Vorlauf, Kessel, Speicher, Kaltwasser) sowie Gaszähler (links unten), Wasserzähler (rechts unten) und
  Enthärtungsanlage im Schema. Ein Tipp auf ein Gerät öffnet den passenden Bereich darunter. Alle weiteren Werte stehen hinter Schaltflächen:
  *Diagramme*, *Status*, *Einstellungen* (erste Zeile) sowie *Brenner*, *Gas*, *Wasser* und *Enthärtung* (zweite Zeile).
  Ein Tipp klappt den jeweiligen Bereich unter den Schaltflächen auf, ein zweiter Tipp schließt ihn.

Mit `layout: wide` oder `layout: compact` lässt sich das Layout fest vorgeben.

Im breiten Layout wird das Schema auf die Bildschirmhöhe verkleinert, damit es z. B. auf dem iPad im Querformat ohne Scrollen
vollständig zu sehen ist (`fit_screen`, standardmäßig an). Der Abzug für Kopfzeile und Ränder lässt sich mit `screen_offset`
(Pixel, Standard 32) anpassen; mit `fit_screen: false` wird die Anpassung abgeschaltet.

## YAML-Konfiguration (optional)

```yaml
type: custom:heizungsanlage-card
layout: auto              # auto | wide | compact
fit_screen: true          # breites Layout auf die Bildschirmhöhe verkleinern (kein Scrollen)
screen_offset: 32          # Abzug von der Bildschirmhöhe in px
title: Heizungsanlage
subtitle: Viessmann Vitocrossal 300 & Vitocell 100-V
tank_range: [20, 65]      # Temperaturbereich der Füllanzeige im Speicher (°C)
limit_offset: 5           # graue Grenzlinien und Skalengrenzen: Mindest-Soll minus 5 K, Maximal-Soll plus 5 K
entities:
  outside_temp: sensor.vicare_outside_temperature
  frost_protection: binary_sensor.vicare_frost_protection_active
  burner_hours: sensor.vicare_burner_hours
  burner_starts: sensor.vicare_burner_starts
  burner_active: binary_sensor.vicare_burner_active
  burner_modulation: sensor.vicare_burner_modulation
  boiler_temp: sensor.vicare_boiler_temperature
  supply_temp: sensor.vicare_supply_temperature
  heating_pump: binary_sensor.vicare_circulation_pump_active
  charge_pump: binary_sensor.vicare_dhw_pump_active
  dhw_circ_pump: binary_sensor.vicare_dhw_circulation_pump_active
  tank_temp: sensor.vscotho1_72_ww_speichertemperatur
  tank_target: number.vscotho1_72_warmwassertemperatur
  tank_min_target: sensor.vicare_hot_water_min_temperature
  tank_max_target: sensor.vicare_hot_water_max_temperature
  comfort_temp: number.vscotho1_72_komforttemperatur
  normal_temp: number.vscotho1_72_normaltemperatur
  reduced_temp: number.vscotho1_72_reduzierte_temperatur
  curve_slope: number.vscotho1_72_steigung_der_heizkurve
  curve_shift: number.vscotho1_72_verschiebung_der_heizkurve
  water_flow: sensor.wasserzahler_flow
  water_temp: sensor.wasserzahler_water_temperature
  # Gas und Wasser kommen automatisch aus dem Energie-Dashboard.
  # Nur eintragen, wenn andere Entitäten verwendet werden sollen:
  # gas_total: sensor.…
  # gas_today: sensor.…
  # water_total: sensor.…
  # water_today: sensor.…
  # Optional (Tafel der Enthärtungsanlage):
  # softener_regeneration: sensor.…   # Zeitstempel der letzten Regeneration (angezeigt wird nur das Datum)
  # softener_salt: sensor.…           # Salzfüllstand in %
  # softener_remaining: sensor.…      # Restbestand in Regenerationen („Noch ca. N Regenerationen“)
```

Im Editor werden nur Abweichungen von den Standardwerten in die YAML-Konfiguration geschrieben.

### Welche Entität schaltet was?

| Animation / Anzeige | Auslöser |
|---|---|
| Flamme und Glühen im Brennerfenster | `burner_active` ist an oder `burner_modulation` > 0 |
| Flammengröße | `burner_modulation` |
| Gasleitung | Brenner aktiv |
| Heizkreis-Leitungen, Pumpenrad, Heizkörper-Tönung | `heating_pump` |
| Ladekreis zum Speicher, Pumpenrad | `charge_pump` |
| Warmwasser-Zirkulation, Pumpenrad | `dhw_circ_pump` |
| Kaltwasserleitungen, Tropfen am Hahn | `water_flow` > 0 |
| Füllung im Speicherfenster | `tank_temp` (zwischen `tank_range`) |

## Voraussetzungen und Grenzen

- Home Assistant mit Custom-Card-Unterstützung und ein aktueller Browser mit SVG- und `ResizeObserver`-Unterstützung.
- Eine eingerichtete Geräteintegration und passende Entitäten. Die Karte liefert keine ViCare-, Zähler- oder Enthärtungsintegration mit.
- Die Standardzuordnungen passen zur oben genannten Viessmann-Anlage. Für andere Anlagen Entitäten im Editor zuordnen.
- Für automatische Gas-/Wasserwerte müssen passende Quellen im Energie-Dashboard eingerichtet sein. Alternativ lassen sich die Zählerentitäten ausdrücklich konfigurieren.
- Die Karte stellt Zustände dar und öffnet bei Klick den HA-Entitätsdialog. Sie ruft selbst keine Schalt- oder Heizungsdienste auf. Aktionen im Entitätsdialog unterliegen den Berechtigungen der angemeldeten HA-Sitzung.
- Animationen zeigen die gemeldeten Zustände, keine unabhängig gemessenen Strömungen. Fehlende oder veraltete Sensoren und Recorder-Daten begrenzen die Aussagekraft; die Karte ersetzt keine Anlagenüberwachung.
- Nicht endliche Messwerte werden verworfen.
- Die Verläufe (24 h) werden alle 5 Minuten über die Recorder-Datenbank neu geladen; die Entitäten müssen dafür im Verlauf aufgezeichnet werden.
- Werte werden mit der nativen Formatierung von Home Assistant angezeigt (Sprache, Einheit, Anzeige-Genauigkeit der Entität).
- Die Gerätegrafiken sind als Bilder in die JavaScript-Datei eingebettet, es werden keine weiteren Dateien nachgeladen.
- Texte in der Karte sind deutsch; der Editor ist deutsch und englisch.
