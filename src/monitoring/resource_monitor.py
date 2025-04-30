import threading
import time
import psutil
from monitoring.datadog_metrics import send_metric

def monitor_resources(interval_seconds=60):
    def run():
        while True:
            try:
                process = psutil.Process()
                cpu = process.cpu_percent(interval=1)  # 1 segundo de intervalo
                mem = process.memory_info().rss / (1024 * 1024)  # en MB
                report_resource_usage(cpu_usage=cpu, memory_usage=mem)
            except Exception as e:
                print(f"[monitor_resources] Error: {e}")
            time.sleep(interval_seconds)

    thread = threading.Thread(target=run, daemon=True)
    thread.start()

def report_resource_usage():
    cpu = psutil.cpu_percent()
    memory = psutil.virtual_memory().percent

    send_metric("app.cpu_usage", cpu)
    send_metric("app.memory_usage", memory)
