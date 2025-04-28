from flask import jsonify

def get_error_json(title, detail, url):
    return jsonify(
        {
            "type": "about:blank",
            "title": title,
            "status": 0,
            "detail": f"{title}: {detail}",
            "instance": url,
        }
    )
