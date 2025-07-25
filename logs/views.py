from django.shortcuts import render, redirect, get_object_or_404
from .forms import LogUploadForm
from .models import LogEntry
import csv
import io
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import HttpResponse
from django.db.models.functions import TruncDate, ExtractHour
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from scripts.log_processor import run
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

from django.contrib.auth.decorators import login_required
from .decorators import admin_required
from django.contrib import messages
import csv, io
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import LogEntry
from .forms import LogUploadForm
from scripts.log_processor import run
from datetime import datetime

@login_required
#@admin_required
def upload_logs(request):
    logs = []
    anomalies = []

    if request.method == 'POST':
        form = LogUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            decoded = file.read().decode('utf-8')
            reader = csv.DictReader(io.StringIO(decoded))
            for row in reader:
                # Convert timestamp to datetime object
                try:
                    timestamp = datetime.fromisoformat(row['timestamp'])
                except ValueError:
                    messages.error(request, f"Invalid timestamp format: {row['timestamp']}")
                    continue

                is_anomaly = 'error' in row['message'].lower() or row['level'].lower() == 'critical'
                
                log = LogEntry.objects.create(
                    user=request.user,
                    timestamp=timestamp,
                    level=row['level'],
                    message=row['message'],
                    source=row['source'],
                    is_anomaly=is_anomaly,
                )
                logs.append(log)


                # Send real-time alert if anomaly detected
                if is_anomaly:
                    channel_layer = get_channel_layer()
                    async_to_sync(channel_layer.group_send)(
                        "logs",
                        {
                            "type": "send_log",
                            "log": {
                                "level": log.level,
                                "message": log.message,
                                "timestamp": str(log.timestamp),
                            },
                        }
                    )

            # Run anomaly detection pipeline
            run()
            messages.success(request, f"Uploaded {len(logs)} logs. Anomalies: {sum(l.is_anomaly for l in logs)}")
            return redirect('logs:dashboard')
    else:
        form = LogUploadForm()

    return render(request, 'upload_logs.html', {
        'form': form,
        'logs': logs,
        'anomalies': anomalies,
    })

@login_required
def log_list(request):
    
    if request.user.profile.role=='admin':
        logs=LogEntry.objects.all().order_by('-timestamp')
    else:
        logs=LogEntry.objects.filter(user=request.user).order_by('-timestamp')
    level = request.GET.get('level')
    show_anomalies = request.GET.get('anomaly') == 'true'
    start_date = request.GET.get('start')
    end_date = request.GET.get('end')
    search_query = request.GET.get('search', '').strip()

    if show_anomalies:
        logs = logs.filter(is_anomaly=True)
    if level:
        logs = logs.filter(level=level)
    if start_date and end_date:
        logs = logs.filter(timestamp__range=[start_date, end_date])
    if search_query:
        logs = logs.filter(Q(message__icontains=search_query) | Q(source__icontains=search_query))

    paginator = Paginator(logs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'log_list.html', {
        'page_obj': page_obj,
        'show_anomalies': show_anomalies,
        'level': level,
        'start': start_date,
        'end': end_date,
        'search_query': search_query,
    })


def export_logs_csv(request):
    logs = LogEntry.objects.all().order_by('-timestamp')
    level = request.GET.get('level')
    show_anomalies = request.GET.get('anomaly') == 'true'
    start_date = request.GET.get('start')
    end_date = request.GET.get('end')

    if level:
        logs = logs.filter(level=level)
    if show_anomalies:
        logs = logs.filter(is_anomaly=True)
    if start_date and end_date:
        logs = logs.filter(timestamp__range=[start_date, end_date])

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="filtered_logs.csv"'

    writer = csv.writer(response)
    writer.writerow(['Timestamp', 'Level', 'Message', 'Source', 'Anomaly'])

    for log in logs:
        writer.writerow([log.timestamp, log.level, log.message, log.source, log.is_anomaly])

    return response


def log_detail(request, pk):
    log = get_object_or_404(LogEntry, pk=pk)
    return render(request, 'log_detail.html', {'log': log})

@login_required
def dashboard_view(request):
    # Filters from query parameters
    start = request.GET.get('start')
    end = request.GET.get('end')
    show_anomalies = request.GET.get('anomaly') == 'true'

    # Role-based filtering
    if request.user.profile.role == 'admin':
        logs = LogEntry.objects.all()
    else:
        logs = LogEntry.objects.filter(user=request.user)

    # Date and anomaly filtering
    if start:
        logs = logs.filter(timestamp__date__gte=start)
    if end:
        logs = logs.filter(timestamp__date__lte=end)
    if show_anomalies:
        logs = logs.filter(is_anomaly=True)

    total_logs = logs.count()
    total_anomalies = logs.filter(is_anomaly=True).count()

    # Level-wise aggregation for summary and charts
    level_counts_qs = logs.values('level').annotate(count=Count('level'))
    level_counts = {row['level']: row['count'] for row in level_counts_qs}
    level_labels = list(level_counts.keys())
    level_values = list(level_counts.values())

    # Trend per day
    daily_logs = (logs.annotate(date=TruncDate('timestamp'))
                      .values('date').annotate(count=Count('id')).order_by('date'))
    date_labels = [entry['date'].strftime('%Y-%m-%d') for entry in daily_logs]
    date_data = [entry['count'] for entry in daily_logs]

    # Anomaly per hour (for heatmaps)
    hourly_logs = (logs.filter(is_anomaly=True)
                       .annotate(hour=ExtractHour('timestamp'))
                       .values('hour').annotate(count=Count('id'))
                       .order_by('hour'))
    hour_labels = list(range(24))
    hour_data = [0] * 24
    for row in hourly_logs:
        hour_data[row['hour']] = row['count']

    recent_logs = logs.order_by('-timestamp')[:10]

    context = {
        'total_logs': total_logs,
        'total_anomalies': total_anomalies,
        'level_counts': level_counts,
        'level_labels': level_labels,
        'level_data': level_values,
        'date_labels': date_labels,
        'date_data': date_data,
        'hour_labels': hour_labels,
        'hour_data': hour_data,
        'start': start,
        'end': end,
        'show_anomalies': show_anomalies,
        'recent_logs': recent_logs,
    }
    return render(request, 'dashboard.html', context)

def export_anomalies_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment;filename="anomalies.csv"'
    writer = csv.writer(response)
    writer.writerow(['Timestamp', 'Level', 'Message', 'Source'])
    anomalies = LogEntry.objects.filter(is_anomaly=True).order_by('-timestamp')
    for log in anomalies:
        writer.writerow([log.timestamp, log.level, log.message, log.source])
    return response


def register(request):
    if request.method=='POST':
        form=UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form=UserCreationForm()
    return render(request,'auth/register.html',{'form':form})

def landing_page(request):
    return render(request, 'landing.html')  # Your landing page template