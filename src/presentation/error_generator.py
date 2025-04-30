from flask import jsonify, current_app

from monitoring.datadog_metrics import report_error

def get_error_json(title, detail, url, method="GET"):
    current_app.logger.error(f"{method} {url} - {title}: {detail}")
    report_error(endpoint_name=f"{method} {url}")
    return jsonify(
        {
            "type": "about:blank",
            "title": title,
            "status": 0,
            "detail": f"{title}: {detail}",
            "instance": url,
        }
    )
