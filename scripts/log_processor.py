import pandas as pd
from sklearn.ensemble import IsolationForest
from logs.models import LogEntry
from django.utils.timezone import make_aware
import numpy as np
from logs.utils.email_utils import send_anomaly_alert
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

channel_layer=get_channel_layer()
def preprocess_and_detect_anomalies():
    logs=LogEntry.objects.all().values('id','timestamp','level','message','source')
    df=pd.DataFrame(list(logs))

    if df.empty:
        print("No logs to process.")
        return 
    
    df['timestamp']=pd.to_datetime(df['timestamp'])
    df['level_encoded']=df['level'].astype('category').cat.codes
    df['message_length']=df['message'].apply(len)
    df['source_encoded']=df['source'].astype('category').cat.codes

    features=df[['level_encoded','message_length','source_encoded']]

    model=IsolationForest(n_estimators=100,contamination=0.1,random_state=42)
    df['anomaly']=model.fit_predict(features)

    df['is_anomaly']=df['anomaly']==-1

    for _, row in df.iterrows():
        is_anomaly = row['is_anomaly']
        log_id = row['id']
        log=LogEntry.objects.get(id=log_id)
        log.is_anomaly = is_anomaly
        
        if is_anomaly and not log.alert_sent:
            
            send_anomaly_alert(log)
            log.alert_sent=True
            async_to_sync(channel_layer.group_send)(
                "logs",
                {
                    "type":"send_log",
                    "log":{
                        "id":log.id,
                        "timestamp":log.timestamp.isoformat(),
                        "level": log.level,
                        "message": log.message,
                        "source": log.source,
                    }
                }
            )
        log.save()
        
    print(f"Processed {len(df)} logs. Anomalies detected: {df['is_anomaly'].sum()}")

def run():
    print("🚀 Running log processor...")
    preprocess_and_detect_anomalies()