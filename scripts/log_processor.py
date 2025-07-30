import pandas as pd
from sklearn.ensemble import IsolationForest
from logs.models import LogEntry
from django.utils.timezone import make_aware
from logs.utils.email_utils import send_anomaly_alert
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

channel_layer = get_channel_layer()

def preprocess_and_detect_anomalies():
    logs = LogEntry.objects.all().values('id', 'timestamp', 'level', 'message', 'source')
    df = pd.DataFrame(list(logs))

    if df.empty:
        print("No logs to process.")
        return

    # Preprocessing
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['level_encoded'] = df['level'].astype('category').cat.codes
    df['message_length'] = df['message'].apply(len)
    df['source_encoded'] = df['source'].astype('category').cat.codes

    features = df[['level_encoded', 'message_length', 'source_encoded']]

    # Anomaly detection
    model = IsolationForest(n_estimators=100, contamination=0.1, random_state=42)
    df['anomaly'] = model.fit_predict(features)
    df['is_anomaly'] = df['anomaly'] == -1

    # Bulk-fetch all logs as objects to avoid N+1 queries
    log_qs = LogEntry.objects.filter(id__in=df['id'])
    log_map = {log.id: log for log in log_qs}

    for _, row in df.iterrows():
        is_anomaly = row['is_anomaly']
        log_id = row['id']
        log = log_map.get(log_id)
        if log is None:
            continue  # Safety: skip if not found

        # Update anomaly status
        log.is_anomaly = is_anomaly
        try:
            if is_anomaly and not log.alert_sent:
                send_anomaly_alert(log)  # Sends mail to uploader and admin, per your logic
                log.alert_sent = True

                async_to_sync(channel_layer.group_send)(
                    "logs",
                    {
                        "type": "send_log",
                        "log": {
                            "id": log.id,
                            "timestamp": log.timestamp.isoformat(),
                            "level": log.level,
                            "message": log.message,
                            "source": log.source,
                        }
                    }
                )
            log.save()
        except Exception as e:
            print(f"Error processing log {log.id}: {e}")

    print(f"Processed {len(df)} logs. Anomalies detected: {df['is_anomaly'].sum()}")

def run():
    print("🚀 Running log processor...")
    preprocess_and_detect_anomalies()
