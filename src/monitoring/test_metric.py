import time
import requests
import os

DATADOG_API_KEY = os.getenv("DATADOG_API_KEY")
DATADOG_API_URL = "https://api.datadoghq.com/api/v1/series" 

def send_test_metric():
    if not DATADOG_API_KEY:
        print("DATADOG_API_KEY no está seteada")
        return
    
    print(f"Usando clave Datadog: {DATADOG_API_KEY[:6]}...{DATADOG_API_KEY[-4:]}")

    headers = {
        "Content-Type": "application/json",
        "DD-API-KEY": DATADOG_API_KEY,
    }

    payload = {
        "series": [
            {
                "metric": "test.metric",
                "points": [[time.time(), 42]],
                "type": "gauge",
                "tags": ["env:test"]
            }
        ]
    }

    response = requests.post(DATADOG_API_URL, headers=headers, json=payload)
    print(response.status_code, response.text)

send_test_metric()

from datadog_metrics import send_metric
import random

random_value = random.uniform(1.0, 100.0)
send_metric("debug.unique_test_metric_20250428", random_value, tags=["env:test", "manual:true"])
send_metric("debug.unique_test_metric_count_20250428", 1, tags=["env:test", "type:count"])
