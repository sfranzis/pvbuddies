# pvBuddies

**Hinweis:** Diese Software wird "as is", also ohne jegliche Garantie oder Support, bereitgestellt.

## Zweck

Dieses Projekt dient der monatlichen Auswertung und automatisierten Berichterstattung der PV-Anlage. Es liest Energiedaten aus einer InfluxDB (gefüllt durch Home Assistant und verschiedene PV-Komponenten), erstellt einen Monatsbericht und veröffentlicht die Ergebnisse auf Mastodon und Bluesky. Optional kann auch ein Report per E-Mail versendet werden.

## Voraussetzungen

- Home Assistant zur Datenerfassung
- InfluxDB als Datenbank
- SMA PV-System (bzw. kompatible Sensoren)
- Python 3.12
- Zugangsdaten für E-Mail, Mastodon und Bluesky (siehe Umgebungsvariablen in [run_pv.sh](run_pv.sh))

## Hinweise

- Die Software ist auf meine persönliche Umgebung optimiert und erwartet bestimmte Entity-Namen und Datenstrukturen.
- Anpassungen für andere Setups sind möglich, aber mit Eigeninitiative und Know-How verbunden.
- Für InfluxDB-User mit Home Assistant ist ein guter Startpunkt in der InfluxDB UI, eine Query über die Dimension `filter(fn: (r) => r._measurement == "kWh" and r._value > 0)` zu starten.
- Nutzung auf eigene Gefahr!

## Lizenz

Siehe [LICENSE](LICENSE).