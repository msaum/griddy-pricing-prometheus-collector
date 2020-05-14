#!/usr/bin/env python3
########################################################################################################################
#
# Griddy.py
# Extract pricing data from GoGriddy API and make it available to Prometheus via an exporter
#
########################################################################################################################
# MIT License
#
# Copyright (c) 2020 Mark Saum
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
########################################################################################################################
#
########################################################################################################################
# Griddy Code Examples:
# https://github.com/trentfoley/SmartThingsPublic/tree/master/smartapps/trentfoley/griddy-manager.src
# https://github.com/mikemrm/go-griddy
# https://github.com/randyr505/gogriddy_api
#
# Prometheus Code Examples:
# https://medium.com/@ikod/custom-exporter-with-prometheus-b1c23cb24e7a
# https://github.com/prometheus/client_python
# https://prometheus.io/docs/practices/instrumentation/
########################################################################################################################

import requests
import json
import os
import logging
import argparse
import time
from prometheus_client.core import GaugeMetricFamily, REGISTRY
from prometheus_client import start_http_server

########################################################################################################################

# -------------------------------------------------------------------------------
# setup simple logging
# -------------------------------------------------------------------------------
logging.basicConfig()
logger = logging.getLogger()

# -------------------------------------------------------------------------------
# Parse Program Arguments
# -------------------------------------------------------------------------------
parser = argparse.ArgumentParser(description='Go Griddy API Client')
parser.add_argument("--debug", "-d", help="turn on debugging output", action="store_true")
parser.add_argument("--verbose", "-v", help="turn on program status information output", action="store_true")

args = parser.parse_args()
if args.verbose:
    logger.setLevel(logging.INFO)
if args.debug:
    logger.setLevel(logging.DEBUG)

# -------------------------------------------------------------------------------
# Process Environment Variables (Container Arguments)
# -------------------------------------------------------------------------------
METERID = os.environ['METERID']
assert METERID
logger.info("METERID: %s" % METERID)

MEMBERID = os.environ['MEMBERID']
assert MEMBERID
logger.info("MEMBERID: %s" % MEMBERID)

SETTLEMENT_POINT = os.environ['SETTLEMENT_POINT']
assert SETTLEMENT_POINT
logger.info("SETTLEMENT_POINT: %s" % SETTLEMENT_POINT)

TDU_CHARGE = float(os.environ['TDU_CHARGE'])
assert TDU_CHARGE
logger.info("TDU_CHARGE: %s" % TDU_CHARGE)

COLLECTION_INTERVAL = int(os.environ['COLLECTION_INTERVAL'])
assert COLLECTION_INTERVAL
logger.info("COLLECTION_INTERVAL: %s" % COLLECTION_INTERVAL)

API_URL = os.environ['API_URL']
assert API_URL
logger.info("API_URL: %s" % API_URL)

HTTP_PORT = int(os.environ['HTTP_PORT'])
assert HTTP_PORT
logger.info("HTTP_PORT: %s" % HTTP_PORT)


class CustomCollector(object):
    def __init__(self):
        pass

    def collect(self):
        # Structure POST request
        payload = {'meterID': METERID, 'memberID': MEMBERID, 'settlement_point': SETTLEMENT_POINT}

        # Make HTTP POST Request to Griddy
        request = requests.post(API_URL, data=json.dumps(payload))

        # Get the JSON payload of the request
        json_payload = json.loads(request.text)

        # g_min_num
        logger.info('Griddy g_min_num: ' + json_payload["now"]["min_num"])
        g_min_num = GaugeMetricFamily("g_min_num", 'Griddy g_min_num')
        g_min_num.add_metric(['min_num'], json_payload["now"]["min_num"])
        yield g_min_num

        # g_price_ckwh
        logger.info('Griddy g_price_ckwh: ' + json_payload["now"]["price_ckwh"])
        g_price_ckwh = GaugeMetricFamily("g_price_ckwh", 'Griddy g_price_ckwh')
        g_price_ckwh.add_metric(['price_ckwh'], json_payload["now"]["price_ckwh"])
        yield g_price_ckwh

        # g_total_price_ckwh
        total_price = float(json_payload["now"]["price_ckwh"]) + TDU_CHARGE
        logger.info('Griddy g_total_price_ckwh: ' + str(total_price))
        g_total_price_ckwh = GaugeMetricFamily("g_total_price_ckwh", 'Griddy g_total_price_ckwh')
        g_total_price_ckwh.add_metric(['total_price_ckwh'], total_price)
        yield g_total_price_ckwh

        # g_value_score
        logger.info('Griddy g_value_score: ' + json_payload["now"]["value_score"])
        g_value_score = GaugeMetricFamily("g_value_score", 'Griddy g_value_score')
        g_value_score.add_metric(['value_score'], json_payload["now"]["value_score"])
        yield g_value_score

        # g_mean_price_ckwh
        logger.info('Griddy g_mean_price_ckwh: ' + json_payload["now"]["mean_price_ckwh"])
        g_mean_price_ckwh = GaugeMetricFamily("g_mean_price_ckwh", 'Griddy g_mean_price_ckwh')
        g_mean_price_ckwh.add_metric(['mean_price_ckwh'], json_payload["now"]["mean_price_ckwh"])
        yield g_mean_price_ckwh

        # g_diff_mean_ckwh
        logger.info('Griddy g_diff_mean_ckwh: ' + json_payload["now"]["diff_mean_ckwh"])
        g_diff_mean_ckwh = GaugeMetricFamily("g_diff_mean_ckwh", 'Griddy g_diff_mean_ckwh')
        g_diff_mean_ckwh.add_metric(['diff_mean_ckwh'], json_payload["now"]["diff_mean_ckwh"])
        yield g_diff_mean_ckwh

        # g_high_ckwh
        logger.info('Griddy g_high_ckwh: ' + json_payload["now"]["high_ckwh"])
        g_high_ckwh = GaugeMetricFamily("g_high_ckwh", 'Griddy g_high_ckwh')
        g_high_ckwh.add_metric(['high_ckwh'], json_payload["now"]["high_ckwh"])
        yield g_high_ckwh

        # g_low_ckwh
        logger.info('Griddy g_low_ckwh: ' + json_payload["now"]["low_ckwh"])
        g_low_ckwh = GaugeMetricFamily("g_low_ckwh", 'Griddy g_low_ckwh')
        g_low_ckwh.add_metric(['low_ckwh'], json_payload["now"]["low_ckwh"])
        yield g_low_ckwh

        # g_std_dev_ckwh
        logger.info('Griddy g_std_dev_ckwh: ' + json_payload["now"]["std_dev_ckwh"])
        g_std_dev_ckwh = GaugeMetricFamily("g_std_dev_ckwh", 'Griddy g_std_dev_ckwh')
        g_std_dev_ckwh.add_metric(['std_dev_ckwh'], json_payload["now"]["std_dev_ckwh"])
        yield g_std_dev_ckwh

        # g_price_display
        logger.info('Griddy g_price_display: ' + json_payload["now"]["price_display"])
        g_price_display = GaugeMetricFamily("g_price_display", 'Griddy g_price_display')
        g_price_display.add_metric(['price_display'], json_payload["now"]["price_display"])
        yield g_price_display

        # Forecast
        # g_price_forecast_0
        logger.info('Griddy g_price_forecast_0: ' + json_payload["forecast"][0]['price_display'])
        g_price_forecast_0 = GaugeMetricFamily("g_price_forecast_0", 'Griddy g_price_forecast_0')
        g_price_forecast_0.add_metric(['price_forecast_0'], json_payload["forecast"][0]['price_display'])
        yield g_price_forecast_0

        # Forecast
        # g_price_forecast_1
        logger.info('Griddy g_price_forecast_1: ' + json_payload["forecast"][1]['price_display'])
        g_price_forecast_1 = GaugeMetricFamily("g_price_forecast_1", 'Griddy g_price_forecast_1')
        g_price_forecast_1.add_metric(['price_forecast_1'], json_payload["forecast"][1]['price_display'])
        yield g_price_forecast_1

        # Forecast
        # g_price_forecast_2
        logger.info('Griddy g_price_forecast_2: ' + json_payload["forecast"][2]['price_display'])
        g_price_forecast_2 = GaugeMetricFamily("g_price_forecast_2", 'Griddy g_price_forecast_2')
        g_price_forecast_2.add_metric(['price_forecast_2'], json_payload["forecast"][2]['price_display'])
        yield g_price_forecast_2

        # Forecast
        # g_price_forecast_3
        logger.info('Griddy g_price_forecast_3: ' + json_payload["forecast"][3]['price_display'])
        g_price_forecast_3 = GaugeMetricFamily("g_price_forecast_3", 'Griddy g_price_forecast_3')
        g_price_forecast_3.add_metric(['price_forecast_3'], json_payload["forecast"][3]['price_display'])
        yield g_price_forecast_3

        # Forecast
        # g_price_forecast_4
        logger.info('Griddy g_price_forecast_4: ' + json_payload["forecast"][4]['price_display'])
        g_price_forecast_4 = GaugeMetricFamily("g_price_forecast_4", 'Griddy g_price_forecast_4')
        g_price_forecast_4.add_metric(['price_forecast_4'], json_payload["forecast"][4]['price_display'])
        yield g_price_forecast_4

        # Forecast
        # g_price_forecast_5
        logger.info('Griddy g_price_forecast_5: ' + json_payload["forecast"][5]['price_display'])
        g_price_forecast_5 = GaugeMetricFamily("g_price_forecast_5", 'Griddy g_price_forecast_5')
        g_price_forecast_5.add_metric(['price_forecast_5'], json_payload["forecast"][5]['price_display'])
        yield g_price_forecast_5

        # Forecast
        # g_price_forecast_6
        logger.info('Griddy g_price_forecast_6: ' + json_payload["forecast"][6]['price_display'])
        g_price_forecast_6 = GaugeMetricFamily("g_price_forecast_6", 'Griddy g_price_forecast_6')
        g_price_forecast_6.add_metric(['price_forecast_6'], json_payload["forecast"][6]['price_display'])
        yield g_price_forecast_6


if __name__ == '__main__':
    start_http_server(HTTP_PORT)
    REGISTRY.register(CustomCollector())
    while True:
        time.sleep(COLLECTION_INTERVAL)
