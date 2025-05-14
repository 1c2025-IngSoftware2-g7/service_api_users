import os
import sys
import logging
import structlog


def add_service_tag(logger, method_name, event_dict):
    """Add tag in each log."""
    service = os.environ.get('SERVICE_NAME', 'users')
    event_dict["service"] = service
    return event_dict

def configure_logging():
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.DEBUG,
    )

    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.processors.TimeStamper(fmt="iso"),
            add_service_tag,
            structlog.processors.JSONRenderer()

        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True
    )

def get_logger(name: str = None):
    if name:
        return structlog.get_logger(name)
    return structlog.get_logger()

configure_logging()
