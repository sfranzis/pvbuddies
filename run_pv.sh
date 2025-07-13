#!/bin/sh

export INFLUXDB_TOKEN="--set-me-up--"
export INFLUXDB_ORG="--set-me-up--"

export MAIL_SERVER="smtp.ionos.de"
export MAIL_PORT=587
export MAIL_SENDER="--set-me-up--"
export MAIL_PASSWD="--set-me-up--"
export MAIL_RECIPIENT="--set-me-up--"

export MASTODON_INSTANCE="https://mastodon.social"
export MASTODON_API_TOKEN="--set-me-up--"

export BSKY_USER="--set-me-up--"
export BSKY_PASSWORD="--set-me-up--"


python3.12 ~/pvbuddies/pv_month.py
