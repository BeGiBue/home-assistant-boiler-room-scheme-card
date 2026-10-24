# Boiler Room Scheme Card v2.0.0

- Aufnahme in den offiziellen HACS-Katalog; reguläre Installation über die HACS-Suche beschrieben.
- Migration bestehender Custom Repositories dokumentiert: nur den benutzerdefinierten Eintrag entfernen, die bestehende Installation nicht deinstallieren und Dashboard-Ressource sowie Konfigurationen behalten.
- Major-Version als HACS-Meilenstein: bedeutet nicht automatisch Breaking Changes. Kartentyp, Entitätszuordnungen und vorhandene Konfigurationsschlüssel bleiben erhalten.
- README auf Funktionen, Konfiguration, Bedienung, Voraussetzungen und Einschränkungen ausgerichtet; unnötige Erklärungen zur optischen Ausrichtung entfernt.
- Sicherheitskorrektur: adaptive und begrenzte Diagrammskalen verhindern Browser-Blockaden durch extreme Recorder-Werte; nicht endliche Live-/Verlaufswerte und Umrechnungsüberläufe werden verworfen.
- Sicherheitskorrektur: sehr große Verläufe verursachen bei der Min-/Max-Berechnung keinen JavaScript-Argumentüberlauf mehr.
- Entwicklungswerkzeuge auf geprüfte Versionen festgelegt; Pillow 13.0.0 ersetzt den verwundbaren lokalen Teststand 12.3.0. Keine zusätzlichen Laufzeitabhängigkeiten der Karte.
- Security-Review der aktuellen Karte und Sicherheits-Regressionstests; Ergebnisse und verbleibende Prüfgrenzen in `SECURITY_REVIEW.md` dokumentiert.
