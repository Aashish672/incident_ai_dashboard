"""Synchronous log processing tasks (Celery removed)."""

import logging

logger = logging.getLogger(__name__)


def process_logs_sync():
    """Run the anomaly detection pipeline synchronously."""
    try:
        from scripts.log_processor import run
        run()
        logger.info("Anomaly detection pipeline completed successfully.")
    except Exception:
        logger.exception("Anomaly detection pipeline failed.")
