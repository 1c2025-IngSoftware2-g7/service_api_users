import time
import requests
import os

DATADOG_API_KEY = os.getenv('DATADOG_API_KEY')
DATADOG_API_URL = 'https://api.datadoghq.com/api/v1/series'

def send_metric(metric_name, value, tags=None, metric_type="gauge"):
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
                "tags": tags or []
            }
        ]
    }

    response = requests.post(DATADOG_API_URL, headers=headers, json=payload)
    if response.status_code != 202:
        print(f"Error sending metric: {response.text}")
    else:
        print(f"Metric {metric_name} sent successfully!")
