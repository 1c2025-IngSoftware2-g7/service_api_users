from flask import jsonify

from logger_config import get_logger

logger = get_logger("api-users")

def get_error_json(title, detail, url, method="GET"):
    logger.error(f"{method} {url} - {title}: {detail}")
    return jsonify(
        {
            "type": "about:blank",
            "title": title,
            "status": 0,
            "detail": f"{title}: {detail}",
            "instance": url,
        }
    )
