# pvBuddies

**Hinweis:** Diese Software wird "as is", also ohne jegliche Garantie oder Support, bereitgestellt.

## Zweck

Dieses Projekt dient der monatlichen Auswertung und automatisierten Berichterstattung der PV-Anlage. Es liest Energiedaten aus einer InfluxDB (gefüllt durch Home Assistant und verschiedene PV-Komponenten), erstellt einen Monatsbericht und veröffentlicht die Ergebnisse auf Mastodon und Bluesky. Optional kann auch ein Report per E-Mail versendet werden.

## Voraussetzungen

- Home Assistant zur Datenerfassung
- InfluxDB als Datenbank
- PV-System in HA eingebunden
- Python 3.12
- Zugangsdaten für E-Mail, Mastodon und Bluesky (siehe Umgebungsvariablen in [run_pv.sh](run_pv.sh))

## Flux Query Erklärung

Kern der Datenverarbeitung ist eine komplexe InfluxDB Flux Query, die monatliche Energiedaten aus Home Assistant abruft und aggregiert:

### Query-Aufbau

```flux
from(bucket: "homeassistant")
  |> range(start: -50d, stop: -1m)
  |> filter(fn: (r) => r._measurement == "kWh" and r._value > 0)
  |> filter(fn: (r) =>
      r["entity_id"] == "sn_3006924963_metering_total_absorbed" or
      r["entity_id"] == "sn_3006924963_metering_total_yield" or
      r["entity_id"] == "sn_3006924963_total_yield" or
      r["entity_id"] == "evcc_pv_1_energy" or
      r["entity_id"] == "sn_1901018498_battery_charge_total" or
      r["entity_id"] == "sn_1901018498_battery_discharge_total" or
      r["entity_id"] == "evcc_stat_total_charged_kwh"
    )
  |> aggregateWindow(every: 1mo, period: 1mo, fn: last, timeSrc: "_start")
  |> difference()
  |> fill(column: "_value", value: 0.0)
  |> group(columns: ["_measurement"])
  |> pivot(rowKey:["_time"], columnKey: ["friendly_name"], valueColumn: "_value")
  |> rename(columns: {
      "SN: 3006924963 Total Yield": "ertrag_sma",
      "Energie Hoymiles": "ertrag_hom",
      "SN: 3006924963 Metering Total Yield": "einspeisung",
      "SN: 3006924963 Metering Total Absorbed": "bezug",
      "SN: 1901018498 Battery Charge Total": "ladung",
      "SN: 1901018498 Battery Discharge Total": "entladung",
      "[evcc] Statistik: gesamt Ladeenergie": "auto"
    })
```

### Schritt-für-Schritt Erklärung

1. **Datenquelle**: `from(bucket: "homeassistant")` - Lädt Daten aus dem Home Assistant InfluxDB-Bucket
2. **Zeitbereich**: `range(start: -50d, stop: -1m)` - 50 Tage Vergangenheit bis 1 Minute vor jetzt
   *Warum 50 Tage?* Obwohl nur monatliche Daten benötigt werden, sind 50 Tage erforderlich, da:
   - Die monatliche Aggregation (`aggregateWindow`) mindestens 2 Datenpunkte für die nachfolgende `difference()` Operation benötigt
   - Je nach Zeitpunkt der Ausführung (z.B. am Monatsanfang) können Daten aus dem Vormonat fehlen
   - 50 Tage stellen sicher, dass immer genügend historische Daten für eine zuverlässige Differenzberechnung vorhanden sind
   - Dies ist ein Sicherheitspuffer für unregelmäßige Datenerfassung (wie bei einer Wallbox) oder Systemausfälle
3. **Grundfilter**: Nur kWh-Messungen mit positiven Werten
4. **Sensor-Auswahl**: Spezifische Entity-IDs für:
   - **SMA Wechselrichter** (SN: 3006924963): Ertrag, Einspeisung, Netzbezug
   - **Hoymiles Mikrowechselrichter**: Zusätzlicher PV-Ertrag (über evcc)
   - **Batteriesystem** (SN: 1901018498): Ladung und Entladung
   - **E-Auto**: Ladeenergie (über evcc)
5. **Monatliche Aggregation**: `aggregateWindow()` mit letztem Wert des Monats
6. **Differenzberechnung**: `difference()` berechnet die Differenz aus den kumulierten Zählerständen und liefert so die Werte für den jeweiligen Monat.
7. **Datenstrukturierung**: `pivot()` transformiert die Daten in tabellarische Form
8. **Umbenennung**: Deutsche Spaltennamen für bessere Lesbarkeit

### Erwartete Datenstruktur

Die Query liefert eine Tabelle mit folgenden Spalten:

- `ertrag_sma`: SMA Solarertrag (kWh)
- `ertrag_hom`: Hoymiles Solarertrag (kWh)
- `bezug`: Netzbezug (kWh)
- `einspeisung`: Netzeinspeisung (kWh)
- `ladung`: Batterieladung (kWh)
- `entladung`: Batterieentladung (kWh)
- `auto`: E-Auto Ladeenergie (kWh)

## Berechnete Kennzahlen

Aus den Rohdaten werden folgende Werte berechnet:

- **Gesamtertrag**: SMA + Hoymiles Ertrag
- **Batterieverlust**: Ladung - Entladung
- **Eigenverbrauch**: Ertrag - Einspeisung - Batterieverlust
- **Gesamtverbrauch**: Eigenverbrauch + Netzbezug
- **Autarkiegrad**: (Eigenverbrauch / Gesamtverbrauch) × 100%
- **Effizienz**: Ertrag / 14,53 kWp (spezifisch für diese Anlage)

## Hinweise

- Dieses Programm ist speziell auf ein Setup mit Home Assistant und InfluxDB 2 ausgelegt und auf meine persönliche Umgebung optimiert. Es erwartet bestimmte Entity-Namen und Datenstrukturen. Kommen andere Komponenten zur Datensammlung und Speicherung zum Einsatz, muss das Programm darauf angepasst werden. Dies erfordert Know-How über die entsprechenden Datenstrukturen.
- Für InfluxDB-User mit Home Assistant ist ein guter Startpunkt in der InfluxDB UI, eine Query über die Dimension `filter(fn: (r) => r._measurement == "kWh" and r._value > 0)` zu starten.
- Die Entity-IDs müssen entsprechend der eigenen Home Assistant Konfiguration angepasst werden.
- Die installierte PV-Leistung (14,53 kWp) muss für die Effizienzberechnung angepasst werden.

- Nutzung auf eigene Gefahr!

## Lizenz

Siehe [LICENSE](LICENSE).