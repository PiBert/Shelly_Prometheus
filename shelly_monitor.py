#!/usr/bin/python
# -*- coding:utf-8 -*-
import ctypes
import logging
import time
import requests
import re

from prometheus_client import Gauge, start_http_server
from systemd.journal import JournaldLogHandler

#SCRIPT_PATH=$(dirname "$(realpath "$0")")

# Setup logging to the Systemd Journal
log = logging.getLogger('Shelly_Plug_Power')
log.addHandler(JournaldLogHandler())
log.setLevel(logging.INFO)

# The time in seconds between sensor reads
READ_INTERVAL = 60.0

# Create Prometheus gauges for humidity and temperature in
# Celsius and Fahrenheit
gt = Gauge('power',
           'power', ['scale'])

# Initialize the labels for the temperature scale
gt.labels('Watt')

def read_shelly():
    try:
        #HTTP Anfrage an Shelly und Weitergabe an Prometheus
        response=requests.get("http://192.168.0.70/meter/0")
        powertxt=re.search('"power":(.*),"overpower"',response.text)
        power=float(powertxt.group(1))
        print(type(power))
    except RuntimeError as e:
        # GPIO access may require sudo permissions
        # Other RuntimeError exceptions may occur, but
        # are common.  Just try again.
        log.error("RuntimeError: {}".format(e))

    if power is not None:
        gt.labels('Watt').set(power)

        log.info("Power:{0:0.1f}*W".format(power))

   # time.sleep(READ_INTERVAL)

if __name__ == "__main__":
    # Expose metrics
    metrics_port = 8000
    start_http_server(metrics_port)
    print("Serving sensor metrics on :{}".format(metrics_port))
    log.info("Serving sensor metrics on :{}".format(metrics_port))

    while True:
        read_shelly()
        time.sleep(60)
