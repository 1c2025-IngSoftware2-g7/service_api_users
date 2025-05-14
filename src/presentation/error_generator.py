from flask import jsonify, current_app

def get_error_json(title, detail, url, method="GET"):
    current_app.logger.error(f"{method} {url} - {title}: {detail}")
    return jsonify(
        {
            "type": "about:blank",
            "title": title,
            "status": 0,
            "detail": f"{title}: {detail}",
            "instance": url,
        }
    )
