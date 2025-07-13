import os
from influxdb_client import InfluxDBClient
from datetime import datetime
import locale
import calendar
import pytz

import post_bsky
import post_mastodon
import sendmail

# InfluxDB Verbindungsdetails
INFLUXDB_URL = "http://influxdb:8086"
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG")

# Flux Query
FLUX_QUERY = """
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
"""


def get_energy_data():
    with InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG) as client:
        query_api = client.query_api()
        result = query_api.query(FLUX_QUERY)

        data = [record.values for table in result for record in table.records]
        return data

def format_subject(entry):
    date_obj = entry.get("_time")
    if not date_obj:
        return "Fehler: Kein Datum gefunden"
    monat = calendar.month_name[date_obj.month]
    jahr = date_obj.year
    return f"PV Auswertung {monat} {jahr}"

def format_number(value):
    return f"{value:.{0 if value >= 100 else 1}f}"


def format_report(entry):
    date_obj = entry.get("_time")
    if not date_obj:
        return "Fehler: Kein Datum gefunden"
    monat = calendar.month_name[date_obj.month]
    jahr = date_obj.year

    ertrag_sma = entry.get("ertrag_sma")
    ertrag_hom = entry.get("ertrag_hom")
  
    einspeisung = entry.get("einspeisung")
    bezug = entry.get("bezug")
    auto = entry.get("auto")
    ladung = entry.get("ladung")
    entladung = entry.get("entladung")
      
    ertrag = ertrag_sma + ertrag_hom
    verlust = ladung - entladung
    eigenverbrauch = ertrag - einspeisung - verlust
    verbrauch = eigenverbrauch + bezug
    autarkie = (eigenverbrauch / verbrauch * 100) if verbrauch else 0
    effizienz = ertrag / 14.53 if ertrag else 0
  
    lines = [
      f"PV Auswertung {monat} {jahr}",
      f"Erzeugung ☀️: {format_number(ertrag)} kWh",
      f" • SMA: {format_number(ertrag_sma)} kWh",
      f" • Hoymiles: {format_number(ertrag_hom)} kWh",
      f"Effizienz 📊: {effizienz:.1f} kWh/kWp",
      f"Verbrauch ⚡\ufe0f: {format_number(verbrauch)} kWh",
      f" • BEV 🚘: {format_number(auto)} kWh",
      f"Netzbezug 🕸\ufe0f: {format_number(bezug)} kWh",
      f"Einspeisung 🏃: {format_number(einspeisung)} kWh",
      f"Autarkie 📈: {autarkie:.1f} %",
      f"Ladung 🔋: {format_number(ladung)} kWh",
      f"Entladung 🪫: {format_number(entladung)} kWh",
      f"Verlust 🕳️: {format_number(verlust)} kWh",
      f"#pvBuddies"
    ]

    return "\n".join(filter(None, lines))

if __name__ == "__main__":
    locale.setlocale(locale.LC_TIME, 'de_DE.UTF-8')
    tz = pytz.timezone('Europe/Berlin') 
    data = get_energy_data()
    
    entry = data[-1]
    report = format_report(entry)
    subject = format_subject(entry)
    print(report)
    sendmail.send_email(
        recipient=os.getenv("MAIL_RECIPIENT"),
        subject=subject,
        body=report
    )
    if datetime.now(tz).day == 1:
        post_bsky.post_to_bluesky(report)
        post_mastodon.post_to_mastodon(report)
