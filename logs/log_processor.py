import pandas as pd
from sklearn.ensemble import IsolationForest
from logs.models import LogEntry
from django.utils.timezone import make_aware
import numpy as np

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
        LogEntry.objects.filter(id=row['id']).update(is_anomaly=row['is_anomaly'])

    print(f"Processed {len(df)} logs. Anomalies detected: {df['is_anomaly'].sum()}")