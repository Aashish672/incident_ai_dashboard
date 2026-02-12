"""
Anomaly detection pipeline using Isolation Forest.

Processes only unscored log entries for incremental anomaly detection,
sends email alerts, and broadcasts WebSocket notifications.
"""

import logging

import pandas as pd
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from sklearn.ensemble import IsolationForest

from logs.models import LogEntry, Notification
from logs.utils.email_utils import send_anomaly_alert

logger = logging.getLogger(__name__)


def preprocess_and_detect_anomalies():
    """Run Isolation Forest on unscored logs and update anomaly flags."""
    # Only process logs that haven't been scored yet
    logs = LogEntry.objects.filter(alert_sent=False).values(
        "id", "timestamp", "level", "message", "source"
    )
    df = pd.DataFrame(list(logs))

    if df.empty:
        logger.info("No new logs to process.")
        return

    # Feature engineering
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["level_encoded"] = df["level"].astype("category").cat.codes
    df["message_length"] = df["message"].apply(len)
    df["source_encoded"] = df["source"].astype("category").cat.codes
    df["hour"] = df["timestamp"].dt.hour

    features = df[["level_encoded", "message_length", "source_encoded", "hour"]]

    # Anomaly detection
    model = IsolationForest(n_estimators=100, contamination=0.1, random_state=42)
    df["anomaly"] = model.fit_predict(features)
    df["is_anomaly"] = df["anomaly"] == -1

    # Bulk-fetch log objects
    log_qs = LogEntry.objects.filter(id__in=df["id"])
    log_map = {log.id: log for log in log_qs}

    channel_layer = get_channel_layer()
    anomaly_count = 0

    for _, row in df.iterrows():
        log = log_map.get(row["id"])
        if log is None:
            continue

        log.is_anomaly = row["is_anomaly"]

        try:
            if row["is_anomaly"] and not log.alert_sent:
                anomaly_count += 1
                send_anomaly_alert(log)
                log.alert_sent = True

                # Create in-app notification
                if log.user:
                    Notification.objects.create(
                        user=log.user,
                        message=f"Anomaly detected in log: {log.message[:50]}...",
                    )

                # WebSocket broadcast
                async_to_sync(channel_layer.group_send)(
                    "logs",
                    {
                        "type": "send_alert",
                        "message": log.message,
                        "level": log.level,
                        "timestamp": log.timestamp.isoformat(),
                    },
                )
            log.save()
        except Exception:
            logger.exception("Error processing log %d", log.id)

    logger.info("Processed %d logs. Anomalies detected: %d", len(df), anomaly_count)


def run():
    """Entry point for the anomaly detection pipeline."""
    logger.info("Running log processor...")
    preprocess_and_detect_anomalies()
