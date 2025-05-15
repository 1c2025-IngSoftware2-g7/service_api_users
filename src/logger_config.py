import os
import sys
import logging
import structlog

LOGGER_NAME = "api-users"

def add_service_tag(logger, method_name, event_dict):
    """Add tag in each log."""
    service = os.environ.get('SERVICE_NAME', 'users')
    event_dict["service"] = service
    return event_dict

def configure_logging():
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    if not logger.handlers:
        # avoid duplication
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.INFO)
        handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(handler)

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
    std_logger = logging.getLogger(name or LOGGER_NAME)
    std_logger.propagate = False  # do not duplicate the root log
    return structlog.get_logger(name or LOGGER_NAME)

configure_logging()
