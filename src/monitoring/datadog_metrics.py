import time
import requests
import os
#from flask import current_app

DATADOG_API_KEY = os.getenv('DATADOG_API_KEY')
DATADOG_API_URL = 'https://api.datadoghq.com/api/v1/series'
SERVICE_NAME = os.getenv('SERVICE_NAME', 'users')

def send_metric(metric_name, value, tags=None, metric_type="gauge"):
    #current_app.logger.debug(f"Send metric to Datadog: {metric_name}:{value}")
    if not DATADOG_API_KEY:
        #current_app.logger.error("Missing Datadog API key. Skipping metric send.")
        print("Missing Datadog API key. Skipping metric send.")
        return

    headers = {
        'Content-Type': 'application/json',
        'DD-API-KEY': DATADOG_API_KEY,
    }

    payload = {
        "series": [
            {
                "metric": metric_name,
                "points": [[time.time(), value]],
                "type": metric_type,   # gauge, count, rate
                "tags": (tags if isinstance(tags, list) else []) + [f"service:{SERVICE_NAME}"]
            }
        ]
    }

    try:
        response = requests.post(DATADOG_API_URL, headers=headers, json=payload, timeout=5)
        if response.status_code != 202:
            print(f"Failed to send metric {metric_name}: {response.text}")
            #current_app.logger.error(f"Failed to send metric {metric_name}: {response.text}")
    except requests.RequestException as e:
        #current_app.logger.error(f"Error sending metric {metric_name}: {e}")
        print(f"Error sending metric {metric_name}: {e}")


def report_response_time(endpoint_name, duration_seconds):
    send_metric(
        metric_name="app.response_time",
        value=duration_seconds,
        tags=[f"endpoint:{endpoint_name}"]
    )


def report_error(endpoint_name=None):
    tags = [f"error:true"]
    if endpoint_name:
        tags.append(f"endpoint:{endpoint_name}")
    send_metric(
        metric_name="app.errors",
        value=1,
        tags=tags,
        metric_type="count"
    )
