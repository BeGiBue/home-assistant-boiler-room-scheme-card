# Changelog

## 2.0.1

- Aufräumarbeiten ohne Funktionsänderung: ungenutzten Code (alte Status-Pillen, nicht mehr verwendete Gestaltungsregeln und ein ungenutzter Farbverlauf) entfernt, doppelt vorhandene Bausteine von breitem und kompaktem Layout (Pumpe, Leitungen, Bilder, Logo, Farben und Pfeile) sowie Spracherkennung, Zahlenformatierung und Editor-Optionen zusammengeführt. Darstellung, Konfiguration und Verhalten bleiben unverändert (42 Ansichten pixelgleich geprüft).
- Repository verschlankt: nicht benötigte Logo-Dateien und die Release-Notes-Dateien entfernt, Entwicklungs- und Release-Abschnitte aus der README genommen, Security-Review entfernt.

## 2.0.0

- Aufnahme in den offiziellen HACS-Katalog; reguläre Installation über die HACS-Suche beschrieben.
- Migration bestehender Custom Repositories dokumentiert: nur den benutzerdefinierten Eintrag entfernen, die bestehende Installation nicht deinstallieren und Dashboard-Ressource sowie Konfigurationen behalten.
- Major-Version als HACS-Meilenstein: bedeutet nicht automatisch Breaking Changes. Kartentyp, Entitätszuordnungen und vorhandene Konfigurationsschlüssel bleiben erhalten.
- README auf Funktionen, Konfiguration, Bedienung, Voraussetzungen und Einschränkungen ausgerichtet; unnötige Erklärungen zur optischen Ausrichtung entfernt.
- Sicherheitskorrektur: adaptive und begrenzte Diagrammskalen verhindern Browser-Blockaden durch extreme Recorder-Werte; nicht endliche Live-/Verlaufswerte und Umrechnungsüberläufe werden verworfen.
- Sicherheitskorrektur: sehr große Verläufe verursachen bei der Min-/Max-Berechnung keinen JavaScript-Argumentüberlauf mehr.
- Entwicklungswerkzeuge auf geprüfte Versionen festgelegt; Pillow 13.0.0 ersetzt den verwundbaren lokalen Teststand 12.3.0. Keine zusätzlichen Laufzeitabhängigkeiten der Karte.
- Sicherheits-Regressionstests für die aktuelle Karte ergänzt.

## 1.0.8

- Sicherheitskorrektur: Entitäts-IDs werden in beiden Layouts vor dem Einsetzen in SVG-Attribute maskiert.
- Sicherheitskorrektur: Zahlen und Einheiten im Speicherdiagramm werden als Text behandelt; HTML aus Entitätsattributen wird nicht mehr als Markup interpretiert.
- Repository-Link und HACS-Ressourcenpfad im Dateikopf sowie der Dokumentationslink der Karte auf den aktuellen Repository-Namen korrigiert.
- Browser-Regressionstests für HTML-Injection, beide Layouts und Entitätsklicks ergänzt.

## 1.0.7

- Neue, im Browser erstellte Vorschauen aus dem unveränderten Original-Code in der README.
- Vorschau-Bilder über absolute Raw-URLs für die Anzeige in GitHub und HACS eingebunden.
- Versionsangaben für das Patch-Release aktualisiert.

Keine Änderungen an der Funktionsweise der Karte oder Integration.

## 1.0.6

- Neue Gerätegrafiken: Viessmann Vitocrossal 300 (Kessel), Vitocell 100-V (Speicher), Gaszähler, Wasserzähler und
  Aqmos-Enthärtungsanlage. Flammen- und Füllfenster sind als Overlay aufgesetzt, die Unterkanten von Kessel und Speicher
  liegen auf einer Höhe, die Leitungsanschlüsse wurden angepasst.
- Heizkörper als Vektorgrafik im Stil des Wasserhahns; in der kompakten Ansicht ist der Rücklauf am Heizkörper angeschlossen.
- Liter werden als normales „l“ angezeigt (statt ℓ).

## 1.0.5

- Boxen „Wasserzähler“ und „Enthärtungsanlage“: Alle Messwerte stehen jetzt samt Einheit rechtsbündig (bündig am rechten
  Rand), im breiten und im kompakten Layout. Die übrigen Boxen (Gas, Brenner, Speicher) behalten die Einheiten-Spalte.

## 1.0.4

- Enthärtungs-Tafel: Zeitstempel (letzte Regeneration) werden nur noch als Datum angezeigt (keine Uhrzeit, kein Überlappen mehr
  mit der Beschriftung). Neue Zeile „Noch ca. N Regenerationen“ mit der neuen Entität `softener_remaining` (Restbestand),
  auch im Karteneditor. Die Tafel ist im breiten Layout etwas breiter.
- Breites Layout: Die Kaltwasser-Box nutzt dieselben Schriftgrößen wie die anderen Boxen.

## 1.0.3

- Speicherdiagramm: Die Skala reicht jetzt von 5 K unter dem Mindest-Sollwert bis 5 K über dem Maximal-Sollwert
  (`limit_offset`); die grauen Grenzlinien sind Unter- und Obergrenze.
- Brennerdiagramm: Y-Achse mit den Werten der Kesseltemperatur.

## 1.0.2

- Breites Layout: Das Schema passt sich der Bildschirmhöhe an und wird ohne Scrollen vollständig angezeigt, z. B. auf dem iPad
  im Querformat (vorher war die untere Leiste abgeschnitten). Neue Optionen `fit_screen` (Standard an) und `screen_offset`
  (Abzug für Kopfzeile und Ränder in px, Standard 32), auch im Karteneditor.
- Vorschau-Werkzeug: `tools/harness.py --height` zeigt nur den sichtbaren Bereich, um die Passung ohne Scrollen zu prüfen.

## 1.0.1

- Layout Anpassungen

## 1.0.0

Erstes Release der Home-Assistant-Karte `custom:heizungsanlage-card`.

- Animiertes Anlagenschema einer Gas-/Ölheizung: Kessel mit Flamme (Größe folgt der Modulation), Warmwasserspeicher mit
  Füllanzeige, Heizkreis-, Lade- und Zirkulationspumpe mit drehendem Flügelrad, Heizkörper, Wasserhahn,
  Gas- und Wasserzähler, Enthärtungsanlage.
- Leitungen laufen nur, wenn die jeweilige Pumpe bzw. der Durchfluss aktiv ist.
- 24-h-Verläufe: Brenner (Modulation und Kesseltemperatur) und Warmwasserspeicher (Soll-Linie, Grenzlinien,
  Maximum, Istwert, Minimum).
- Gas und Wasser (Stand und Tagesverbrauch) automatisch aus dem Energie-Dashboard.
- Zwei Layouts: **breit** (Tablet/Desktop) und **kompakt** (Handy, Hochformat) mit Kerngeräten im Schema und
  aufklappbaren Detailbereichen; Umschaltung automatisch nach Breite oder fest per `layout`.
- Visueller Editor (deutsch und englisch) für alle Einstellungen, kein YAML nötig.
- Klick auf einen Wert öffnet den Home-Assistant-Entitätsdialog; native Formatierung der Werte.
- Gerätegrafiken sind eingebettet, die Karte besteht aus einer einzigen Datei ohne externe Abhängigkeiten.
